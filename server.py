from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import db
import llm
import spark
import curator
import parser
import tts
import director
import summarizer
import researcher
import validator
import vision
import music_orchestrator
import world_engine
import dicemaster
import social_engine
import foreshadowing
import canon_checker
import config
import os
import json
import random

app = FastAPI()
music = music_orchestrator.MusicOrchestrator()
world = world_engine.WorldEngine()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount the portraits directory
if not os.path.exists(config.PORTRAITS_DIR):
    os.makedirs(config.PORTRAITS_DIR)
app.mount("/portraits", StaticFiles(directory=config.PORTRAITS_DIR), name="portraits")

# Mount AudioSequencer directories if they exist
music_examples = os.path.join(config.AUDIO_SEQUENCER_PATH, "musicExamples")
if os.path.exists(music_examples):
    app.mount("/music_examples", StaticFiles(directory=music_examples), name="music_examples")

gen_assets = os.path.join(config.AUDIO_SEQUENCER_PATH, "generated_assets")
if os.path.exists(gen_assets):
    app.mount("/gen_assets", StaticFiles(directory=gen_assets), name="gen_assets")

# Mount the audio output directory so it can be accessed via HTTP
if not os.path.exists(config.AUDIO_OUTPUT_DIR):
    os.makedirs(config.AUDIO_OUTPUT_DIR)
app.mount("/audio", StaticFiles(directory=config.AUDIO_OUTPUT_DIR), name="audio")

# Mount the environments directory
if not os.path.exists(config.ENVIRONMENTS_DIR):
    os.makedirs(config.ENVIRONMENTS_DIR)
app.mount("/environments", StaticFiles(directory=config.ENVIRONMENTS_DIR), name="environments")

# Mount the map tiles directory
if not os.path.exists(config.MAP_TILES_DIR):
    os.makedirs(config.MAP_TILES_DIR)
app.mount("/map_tiles", StaticFiles(directory=config.MAP_TILES_DIR), name="map_tiles")

@app.get("/")
async def get():
    return FileResponse('static/index.html')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "user_input":
                user_input = message["content"]
                intent = parser.detect_intent(user_input)
                
                if intent == 'SPARK':
                    idea = spark.generate_spark()
                    await websocket.send_text(json.dumps({"type": "spark", "content": idea}))
                else:
                    # Modify prompt for continuation
                    if intent in ['CONTINUE', 'EMPTY']:
                        prompt = "The player is waiting for the story to continue. Describe the next sequence of events, focusing on atmospheric detail and character reaction. Do not wait for player input yet. Only write the next segment of dialogue/action."
                    else:
                        prompt = user_input
                        
                    # Get context
                    facts = curator.get_relevant_context(user_input)
                    
                    # Logic Validation (Phase 1/2)
                    if intent in ['ACTION', 'DIALOGUE']:
                        is_valid, reason = validator.validate_action(user_input, facts)
                        if not is_valid:
                            await websocket.send_text(json.dumps({"type": "validation_failure", "content": reason}))
                            # Skip generation for invalid actions
                            continue

                    # DiceMaster: Perform hidden check for actions
                    mechanical_result = ""
                    if intent == 'ACTION':
                        success, roll, dc, sides, reason = dicemaster.perform_hidden_check(user_input, facts)
                        res_str = "SUCCESS" if success else "FAILURE"
                        mechanical_result = f"MECHANICAL RESULT: {res_str} (Rolled {roll} vs DC {dc} on a D{sides}). Narrate the outcome accordingly."
                        # Log to debug
                        await websocket.send_text(json.dumps({"type": "debug", "content": f"DiceMaster: {mechanical_result} - {reason}"}))

                    # Director Agent: Evaluate story state
                    director_instructions = director.evaluate_state(user_input)
                    
                    # Persona Conditioning: Get persona blocks for mentioned characters
                    persona_blocks = director.get_persona_blocks(user_input)
                    
                    # Hierarchical Memory: Get the 'Story So Far'
                    narrative_seed = db.get_story_state("narrative_seed")
                    
                    # Foreshadowing: Check for pending payoffs
                    foreshadow_note = ""
                    recent_history = db.get_recent_history(limit=5)
                    payoff = foreshadowing.check_for_payoff(recent_history)
                    if payoff:
                        payoff_id, element_name, foreshadow_note = payoff
                        db.resolve_foreshadowing(payoff_id)
                        await websocket.send_text(json.dumps({"type": "info", "content": f"Foreshadowing payoff: {element_name}"}))

                    await websocket.send_text(json.dumps({"type": "debug", "content": f"Intent: {intent}, Using context: {len(facts)} facts, Director: {director_instructions is not None}, Personas: {len(persona_blocks)}, Seed: {narrative_seed is not None}"}))
                    
                    full_response = ""
                    # Stream LLM output back to client
                    for chunk in llm.generate_story_segment(
                        prompt, 
                        context_facts=facts, 
                        director_instructions=director_instructions, 
                        persona_blocks=persona_blocks,
                        narrative_seed=narrative_seed,
                        mechanical_result=mechanical_result,
                        foreshadowing_payoff=foreshadow_note # Pass payoff instruction
                    ):
                        await websocket.send_text(json.dumps({"type": "story_chunk", "content": chunk}))
                        full_response += chunk
                    
                    # Log to history for future summarization
                    db.log_history(user_input, full_response)

                    # Foreshadowing: Extract new seeds from the response
                    curr_loc_name = db.get_story_state("current_location") or "Unknown"
                    foreshadowing.extract_seeds(full_response, curr_loc_name)

                    # Canon Checker: Validate world-building consistency
                    claims = canon_checker.extract_claims(full_response)
                    if claims:
                        contradictions = canon_checker.check_for_contradictions(claims, facts)
                        if contradictions:
                            for c in contradictions:
                                await websocket.send_text(json.dumps({"type": "info", "content": f"Canon Warning: {c['violation']}"}))
                                await websocket.send_text(json.dumps({"type": "debug", "content": f"Contradiction: {c['claim']} violates {c['violation']}"}))
                    
                    # Quest Evaluation (Check for completed objectives)
                    quest_updates = director.evaluate_quest_progress(full_response)
                    for update in quest_updates:
                        db.update_objective_status(update['objective_id'], update['status'])
                        await websocket.send_text(json.dumps({"type": "info", "content": f"Objective update: {update['status']}"}))

                    # Get location ID for snapshot
                    curr_loc_name = db.get_story_state("current_location")
                    loc_id = None
                    if curr_loc_name:
                        loc_obj = db.get_location_by_name(curr_loc_name)
                        loc_id = loc_obj['id'] if loc_obj else None

                    # Commit Snapshot (Narrative Version Control)
                    session_id = "default_session" # Future: dynamic sessions
                    db.commit_snapshot(session_id, user_input, full_response, narrative_seed, loc_id)
                    
                    # Social Layer: Update relationships based on interaction
                    social_engine.update_social_state(user_input, full_response)

                    # Environment Detection & Generation (Every turn)
                    recent_history = db.get_recent_history(limit=5)
                    loc_name, loc_desc, rel_to, direction = director.identify_location(user_input, recent_history)
                    
                    # Music Orchestration (Every 3 turns or on location change)
                    if db.get_history_count() % 3 == 0 or loc_name:
                        mood = music.detect_mood(full_response)
                        track = music.select_track(mood)
                        if track:
                            # Map file path to mounted URL
                            file_path = track['file_path']
                            url = None
                            if "musicExamples" in file_path:
                                url = f"/music_examples/{os.path.basename(file_path)}"
                            elif "generated_assets" in file_path:
                                url = f"/gen_assets/{os.path.basename(file_path)}"
                            
                            if url:
                                await websocket.send_text(json.dumps({
                                    "type": "music_event", 
                                    "url": url, 
                                    "mood": mood, 
                                    "filename": track['filename']
                                }))

                    if loc_name:
                        prev_loc = db.get_story_state("current_location")
                        if loc_name != prev_loc:
                            # Use world engine to place it
                            world.resolve_new_location(loc_name, loc_desc, relative_to_name=rel_to, direction=direction)
                            db.set_story_state("current_location", loc_name)
                            # Update player position
                            world.move_entity("player", 0, loc_name)
                            
                            env_url = vision.generate_environment(loc_name, loc_desc)
                            await websocket.send_text(json.dumps({"type": "scene_update", "location": loc_name, "url": env_url}))

                    # Trigger periodic summarization (every 10 turns)
                    if db.get_history_count() % 10 == 0:
                        summarizer.update_narrative_seed()
                        await websocket.send_text(json.dumps({"type": "info", "content": "Narrative summary updated."}))

                        # ALSO check for narrative gaps and trigger research if needed
                        recent_history = db.get_recent_history(limit=5)
                        active_threads = db.get_active_plot_threads()
                        needs_research, theme = director.check_narrative_gaps(recent_history, active_threads)
                        
                        if needs_research:
                            await websocket.send_text(json.dumps({"type": "info", "content": f"Director suggests research mission: '{theme}'"}))
                            researcher.perform_research_injection(theme, context=full_response)
                            await websocket.send_text(json.dumps({"type": "info", "content": f"Researcher injected new inspiration for '{theme}'."}))

                    # Parse and generate audio
                    dialogue_lines = parser.parse_dialogue(full_response)
                    for speaker, text in dialogue_lines:
                        voice_model = db.get_character_voice(speaker)
                        audio_path = tts.generate_audio(text, speaker, voice_model)
                        if audio_path:
                            # Send URL to client for playback
                            audio_url = f"/audio/{os.path.basename(audio_path)}"
                            await websocket.send_text(json.dumps({"type": "audio_event", "url": audio_url, "speaker": speaker}))
                            
            elif message["type"] == "add_character":
                char_data = message["content"]
                db.add_character(
                    char_data["name"], 
                    char_data["description"], 
                    char_data["traits"], 
                    char_data.get("voice_id", "en_US-lessac-medium.onnx")
                )
                # Generate portrait asynchronously
                portrait_url = vision.generate_portrait(char_data["name"], char_data["description"], char_data["traits"])
                await websocket.send_text(json.dumps({"type": "info", "content": f"Character {char_data['name']} added with portrait."}))
                await websocket.send_text(json.dumps({"type": "portrait_update", "name": char_data["name"], "url": portrait_url}))
                
            elif message["type"] == "add_lore":
                lore_data = message["content"]
                db.add_lore(lore_data["topic"], lore_data["description"])
                await websocket.send_text(json.dumps({"type": "info", "content": f"Lore topic '{lore_data['topic']}' added."}))

            elif message["type"] == "add_meta":
                meta_data = message["content"]
                db.add_meta_lore(meta_data["topic"], meta_data["description"], meta_data["keywords"])
                await websocket.send_text(json.dumps({"type": "info", "content": f"Meta-narrative '{meta_data['topic']}' added."}))

            elif message["type"] == "add_plot_thread":
                thread_data = message["content"]
                db.add_plot_thread(thread_data["description"])
                await websocket.send_text(json.dumps({"type": "info", "content": f"Plot thread '{thread_data['description']}' added."}))

            elif message["type"] == "add_quest":
                quest_data = message["content"]
                quest_id = db.add_quest(quest_data["title"], quest_data["description"], quest_data.get("priority", 1))
                for obj in quest_data.get("objectives", []):
                    db.add_quest_objective(quest_id, obj)
                await websocket.send_text(json.dumps({"type": "info", "content": f"Quest '{quest_data['title']}' added."}))

            elif message["type"] == "add_quest_objective":
                obj_data = message["content"]
                db.add_quest_objective(obj_data["quest_id"], obj_data["description"])
                await websocket.send_text(json.dumps({"type": "info", "content": "Objective added."}))

            elif message["type"] == "get_state":
                seed = db.get_story_state("narrative_seed")
                threads = db.get_active_plot_threads()
                curr_loc = db.get_story_state("current_location")
                
                loc_url = None
                if curr_loc:
                    safe_name = "".join([char for char in curr_loc if char.isalnum()]).lower()
                    loc_path = os.path.join(config.ENVIRONMENTS_DIR, f"{safe_name}.png")
                    loc_url = f"/static/environments/{safe_name}.png" if os.path.exists(loc_path) else None

                # Get characters with portraits
                chars = db.query_db("SELECT name, description, traits FROM characters")
                char_list = []
                for c in chars:
                    safe_name = "".join([char for char in c['name'] if char.isalnum()]).lower()
                    portrait_path = os.path.join(config.PORTRAITS_DIR, f"{safe_name}.png")
                    url = f"/static/portraits/{safe_name}.png" if os.path.exists(portrait_path) else None
                    char_list.append({
                        "name": c['name'],
                        "description": c['description'],
                        "traits": c['traits'],
                        "portrait": url
                    })
                
                # Get active quests
                quests = db.get_active_quests()
                
                # Get character relationships with player
                relationships = []
                for c in chars:
                    rel = db.get_relationship(0, c['id'])
                    relationships.append({
                        "other_name": c['name'],
                        "trust": rel['trust'],
                        "fear": rel['fear'],
                        "affection": rel['affection']
                    })

                await websocket.send_text(json.dumps({
                    "type": "state_update", 
                    "seed": seed, 
                    "threads": [t['description'] for t in threads],
                    "characters": char_list,
                    "quests": [dict(q) for q in quests],
                    "relationships": relationships,
                    "location": curr_loc,
                    "location_image": loc_url
                }))

            elif message["type"] == "get_map":
                locations = db.get_all_locations()
                paths = db.get_all_paths()
                # Convert to plain lists/dicts and ensure tiles exist
                loc_list = []
                for l in locations:
                    ldict = dict(l)
                    # Generate tile if missing
                    if ldict['biome_type']:
                        ldict['tile_url'] = vision.generate_map_tile(ldict['biome_type'])
                    loc_list.append(ldict)
                    
                path_list = [dict(p) for p in paths]
                await websocket.send_text(json.dumps({
                    "type": "map_data",
                    "locations": loc_list,
                    "paths": path_list
                }))

            elif message["type"] == "get_timeline":
                session_id = "default_session"
                history = db.get_snapshot_history(session_id)
                await websocket.send_text(json.dumps({
                    "type": "timeline_data",
                    "snapshots": [dict(s) for s in history]
                }))

            elif message["type"] == "checkout_snapshot":
                snap_id = message["snapshot_id"]
                snap = db.query_db("SELECT * FROM snapshots WHERE id = ?", (snap_id,), one=True)
                if snap:
                    # Update story head
                    db.execute_db(
                        "UPDATE story_heads SET current_snapshot_id = ? WHERE session_id = ?",
                        (snap_id, "default_session")
                    )
                    # Restore state
                    db.set_story_state("narrative_seed", snap['narrative_seed'])
                    if snap['location_id']:
                        loc = db.get_location(snap['location_id'])
                        if loc:
                            db.set_story_state("current_location", loc['name'])
                    
                    await websocket.send_text(json.dumps({"type": "info", "content": f"Switched to turn {snap['turn_number']}."}))
                    # Request full state update
                    await websocket.send_text(json.dumps({"type": "state_update_request"}))

    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.GENERATOR_HOST, port=config.GENERATOR_PORT)