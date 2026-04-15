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
                        
                    # Get Context and Director Plan in parallel
                    context_task = asyncio.to_thread(curator.get_relevant_context, user_input)
                    
                    # Get Player State for Validation
                    player_inv = db.get_inventory("player", 0)
                    player_stats = db.get_entity_stats("player", 0)
                    active_threads = db.get_active_plot_threads()
                    active_quests = db.get_active_quests()
                    recent_history = db.get_recent_history(limit=10)

                    # Parallel 1: Context, Validation, hidden check
                    # We need facts for validation and dicemaster
                    facts = await context_task
                    
                    val_task = None
                    if intent in ['ACTION', 'DIALOGUE']:
                        val_task = validator.validate_action(user_input, facts, inventory=player_inv, stats=player_stats)
                    
                    dice_task = None
                    if intent == 'ACTION':
                        dice_task = dicemaster.perform_hidden_check(user_input, facts)

                    # Parallel 2: Director Plan
                    plan_task = director.generate_action_plan(user_input, recent_history, active_threads, active_quests)
                    
                    # Gather initial results
                    validation_result = (True, "")
                    mechanical_result = ""
                    
                    tasks_to_gather = [plan_task]
                    if val_task: tasks_to_gather.append(val_task)
                    if dice_task: tasks_to_gather.append(dice_task)
                    
                    gathered_results = await asyncio.gather(*tasks_to_gather)
                    
                    plan = gathered_results[0]
                    idx = 1
                    if val_task:
                        validation_result = gathered_results[idx]
                        idx += 1
                    if dice_task:
                        success, roll, dc, sides, reason = gathered_results[idx]
                        res_str = "SUCCESS" if success else "FAILURE"
                        mechanical_result = f"MECHANICAL RESULT: {res_str} (Rolled {roll} vs DC {dc} on a D{sides}). Narrate the outcome accordingly."
                        await websocket.send_text(json.dumps({"type": "debug", "content": f"DiceMaster: {mechanical_result} - {reason}"}))
                        idx += 1

                    # Logic Validation Check
                    if not validation_result[0]:
                        await websocket.send_text(json.dumps({"type": "validation_failure", "content": validation_result[1]}))
                        continue

                    # Execute Plan Updates (Synchronous DB calls)
                    for update in plan['quest_updates']:
                        db.update_objective_status(update['objective_id'], update['status'])
                        await websocket.send_text(json.dumps({"type": "info", "content": f"Objective update: {update['status']}"}))

                    if plan['milestone_completed']:
                        m_idx = db.get_current_milestone_index()
                        arc = db.get_active_arc()
                        if arc and m_idx < len(arc['milestones']) - 1:
                            db.set_current_milestone_index(m_idx + 1)
                            new_milestone = arc['milestones'][m_idx + 1]
                            await websocket.send_text(json.dumps({
                                "type": "info", 
                                "content": f"Milestone Achieved! Next Chapter: {new_milestone['name']}"
                            }))
                            summarizer.update_narrative_seed()
                        else:
                            await websocket.send_text(json.dumps({"type": "info", "content": "Adventure Arc Completed!"}))

                    if plan['new_location']:
                        loc = plan['new_location']
                        # world.resolve_new_location is now async
                        await world.resolve_new_location(loc['name'], loc['desc'], relative_to_name=loc['rel_to'], direction=loc['direction'])
                        db.set_story_state("current_location", loc['name'])
                        world.move_entity("player", 0, loc['name'])
                        
                        env_url = await vision.generate_environment(loc['name'], loc['desc'])
                        await websocket.send_text(json.dumps({"type": "scene_update", "location": loc['name'], "url": env_url}))

                    # Director Instructions & Personas
                    director_instructions = director.evaluate_state(user_input)
                    persona_blocks = director.get_persona_blocks(user_input)
                    
                    # Hierarchical Memory: Get the 'Story So Far'
                    narrative_seed = db.get_story_state("narrative_seed")
                    
                    # Pacing Director: Get current pacing
                    current_pacing = db.get_story_state("current_pacing") or "Exploration"

                    # Foreshadowing: Check for pending payoffs
                    foreshadow_note = ""
                    payoff = foreshadowing.check_for_payoff(recent_history)
                    if payoff:
                        payoff_id, element_name, foreshadow_note = payoff
                        db.resolve_foreshadowing(payoff_id)
                        await websocket.send_text(json.dumps({"type": "info", "content": f"Foreshadowing payoff: {element_name}"}))

                    await websocket.send_text(json.dumps({"type": "debug", "content": f"Intent: {intent}, Using context: {len(facts)} facts, Director: {director_instructions is not None}, Personas: {len(persona_blocks)}, Seed: {narrative_seed is not None}"}))
                    
                    full_response = ""
                    # Stream LLM output back to client
                    async for chunk in llm.async_generate_story_segment(
                        prompt, 
                        context_facts=facts, 
                        director_instructions=director_instructions, 
                        persona_blocks=persona_blocks,
                        narrative_seed=narrative_seed,
                        mechanical_result=mechanical_result,
                        foreshadowing_payoff=foreshadow_note,
                        pacing_directive=current_pacing
                    ):
                        await websocket.send_text(json.dumps({"type": "story_chunk", "content": chunk}))
                        full_response += chunk
                    
                    # Log to history for future summarization
                    db.log_history(user_input, full_response)

                    # Post-generation parallel tasks
                    curr_loc_name = db.get_story_state("current_location") or "Unknown"
                    
                    post_tasks = [
                        foreshadowing.extract_seeds(full_response, curr_loc_name),
                        canon_checker.extract_claims(full_response),
                        social_engine.update_social_state(user_input, full_response),
                        music.detect_mood(full_response)
                    ]
                    
                    post_results = await asyncio.gather(*post_tasks)
                    
                    # Canon check results (Phase 2)
                    claims = post_results[1]
                    if claims:
                        contradictions = await canon_checker.check_for_contradictions(claims, facts)
                        if contradictions:
                            for c in contradictions:
                                await websocket.send_text(json.dumps({"type": "info", "content": f"Canon Warning: {c['violation']}"}))

                    # Music results
                    mood = post_results[3]
                    if db.get_history_count() % 3 == 0 or plan['new_location']:
                        track = music.select_track(mood)
                        if track:
                            file_path = track['file_path']
                            url = f"/music_examples/{os.path.basename(file_path)}" if "musicExamples" in file_path else f"/gen_assets/{os.path.basename(file_path)}"
                            await websocket.send_text(json.dumps({"type": "music_event", "url": url, "mood": mood, "filename": track['filename']}))

                    # Research Check
                    if plan['needs_research']:
                        await websocket.send_text(json.dumps({"type": "info", "content": f"Director suggests research mission: '{plan['research_theme']}'"}))
                        await researcher.perform_research_injection(plan['research_theme'], context=full_response)
                        await websocket.send_text(json.dumps({"type": "info", "content": f"Researcher injected new inspiration for '{plan['research_theme']}'."}))

                    # Initiative Check (Proactive DM)
                    if intent in ['CONTINUE', 'EMPTY'] and not plan['new_location'] and not plan['quest_updates']:
                        # If nothing happened, trigger initiative
                        initiative = await director.generate_initiative(recent_history, active_threads)
                        await websocket.send_text(json.dumps({"type": "info", "content": "Director Initiative Triggered."}))
                        await websocket.send_text(json.dumps({"type": "story_chunk", "content": f"\n\n[SUDDEN EVENT]: {initiative}"}))
                        db.log_history("DIRECTOR_INITIATIVE", initiative)

                    # Commit Snapshot
                    loc_id = None
                    if curr_loc_name:
                        loc_obj = db.get_location_by_name(curr_loc_name)
                        loc_id = loc_obj['id'] if loc_obj else None
                    db.commit_snapshot("default_session", user_input, full_response, narrative_seed, loc_id)

                    # Parse and generate audio
                    dialogue_lines = parser.parse_dialogue(full_response)
                    for speaker, text in dialogue_lines:
                        voice_model = db.get_character_voice(speaker)
                        audio_path = tts.generate_audio(text, speaker, voice_model)
                        if audio_path:
                            audio_url = f"/audio/{os.path.basename(audio_path)}"
                            await websocket.send_text(json.dumps({"type": "audio_event", "url": audio_url, "speaker": speaker}))

                    # Trigger periodic summarization (every 10 turns)
                    if db.get_history_count() % 10 == 0:
                        await summarizer.update_narrative_seed()
                        await websocket.send_text(json.dumps({"type": "info", "content": "Narrative summary updated."}))

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

            elif message["type"] == "load_arc":
                filename = message["filename"]
                filepath = os.path.join("static", "arcs", filename)
                if os.path.exists(filepath):
                    with open(filepath, "r") as f:
                        arc_data = json.load(f)
                        db.set_active_arc(arc_data)
                        await websocket.send_text(json.dumps({"type": "info", "content": f"Adventure Arc '{arc_data['title']}' loaded."}))
                        await websocket.send_text(json.dumps({"type": "state_update_request"}))
                else:
                    await websocket.send_text(json.dumps({"type": "info", "content": f"Arc file {filename} not found."}))

            elif message["type"] == "set_pacing":
                pacing = message["pacing"]
                db.set_story_state("current_pacing", pacing)
                await websocket.send_text(json.dumps({"type": "info", "content": f"Pacing set to {pacing}."}))

            elif message["type"] == "get_state":
                seed = db.get_story_state("narrative_seed")
                threads = db.get_active_plot_threads()
                curr_loc = db.get_story_state("current_location")
                curr_pacing = db.get_story_state("current_pacing") or "Exploration"
                
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
                
                # Get active arc
                active_arc = db.get_active_arc()
                milestone_idx = db.get_current_milestone_index()

                # Get player inventory and stats
                inventory = db.get_inventory("player", 0)
                stats = db.get_entity_stats("player", 0)

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
                    "location_image": loc_url,
                    "pacing": curr_pacing,
                    "active_arc": active_arc,
                    "milestone_index": milestone_idx,
                    "inventory": [dict(i) for i in inventory],
                    "stats": [dict(s) for s in stats]
                }))

            elif message["type"] == "add_item":
                item = message["content"]
                db.add_inventory_item("player", 0, item["name"], item.get("description", ""), item.get("quantity", 1))
                await websocket.send_text(json.dumps({"type": "info", "content": f"Item '{item['name']}' added."}))
                await websocket.send_text(json.dumps({"type": "state_update_request"}))

            elif message["type"] == "set_stat":
                stat = message["content"]
                db.set_entity_stat("player", 0, stat["name"], stat["value"])
                await websocket.send_text(json.dumps({"type": "info", "content": f"Stat '{stat['name']}' set to {stat['value']}."}))
                await websocket.send_text(json.dumps({"type": "state_update_request"}))

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