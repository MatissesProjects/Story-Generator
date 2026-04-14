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
import config
import os
import json
import random

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount the portraits directory
if not os.path.exists(config.PORTRAITS_DIR):
    os.makedirs(config.PORTRAITS_DIR)
app.mount("/portraits", StaticFiles(directory=config.PORTRAITS_DIR), name="portraits")

# Mount the audio output directory so it can be accessed via HTTP
if not os.path.exists(config.AUDIO_OUTPUT_DIR):
    os.makedirs(config.AUDIO_OUTPUT_DIR)
app.mount("/audio", StaticFiles(directory=config.AUDIO_OUTPUT_DIR), name="audio")

# Mount the environments directory
if not os.path.exists(config.ENVIRONMENTS_DIR):
    os.makedirs(config.ENVIRONMENTS_DIR)
app.mount("/environments", StaticFiles(directory=config.ENVIRONMENTS_DIR), name="environments")

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

                    # Director Agent: Evaluate story state
                    director_instructions = director.evaluate_state(user_input)
                    
                    # Persona Conditioning: Get persona blocks for mentioned characters
                    persona_blocks = director.get_persona_blocks(user_input)
                    
                    # Hierarchical Memory: Get the 'Story So Far'
                    narrative_seed = db.get_story_state("narrative_seed")
                    
                    await websocket.send_text(json.dumps({"type": "debug", "content": f"Intent: {intent}, Using context: {len(facts)} facts, Director: {director_instructions is not None}, Personas: {len(persona_blocks)}, Seed: {narrative_seed is not None}"}))
                    
                    full_response = ""
                    # Stream LLM output back to client
                    for chunk in llm.generate_story_segment(
                        prompt, 
                        context_facts=facts, 
                        director_instructions=director_instructions, 
                        persona_blocks=persona_blocks,
                        narrative_seed=narrative_seed
                    ):
                        await websocket.send_text(json.dumps({"type": "story_chunk", "content": chunk}))
                        full_response += chunk
                    
                    # Log to history for future summarization
                    db.log_history(user_input, full_response)
                    
                    # Environment Detection & Generation (Every turn)
                    recent_history = db.get_recent_history(limit=5)
                    loc_name, loc_desc = director.identify_location(user_input, recent_history)
                    if loc_name:
                        prev_loc = db.get_story_state("current_location")
                        if loc_name != prev_loc:
                            db.set_story_state("current_location", loc_name)
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
                
                await websocket.send_text(json.dumps({
                    "type": "state_update", 
                    "seed": seed, 
                    "threads": [t['description'] for t in threads],
                    "characters": char_list,
                    "location": curr_loc,
                    "location_image": loc_url
                }))

    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.GENERATOR_HOST, port=config.GENERATOR_PORT)