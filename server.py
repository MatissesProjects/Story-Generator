from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import db
import llm
import spark
import curator
import parser
import tts
import director
import summarizer
import researcher
import config
import os
import json

app = FastAPI()

# Mount the audio output directory so it can be accessed via HTTP
if not os.path.exists(config.AUDIO_OUTPUT_DIR):
    os.makedirs(config.AUDIO_OUTPUT_DIR)
app.mount("/audio", StaticFiles(directory=config.AUDIO_OUTPUT_DIR), name="audio")

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
                    
                    # Trigger periodic summarization (every 10 turns)
                    if db.get_history_count() % 10 == 0:
                        summarizer.update_narrative_seed()
                        await websocket.send_text(json.dumps({"type": "info", "content": "Narrative summary updated."}))

                    # Trigger autonomous research for inspiration (every 15 turns)
                    if db.get_history_count() % 15 == 0:
                        all_entities = db.get_all_entities()
                        research_theme = random.choice(all_entities) if all_entities else "weird mythology"
                        researcher.perform_research_injection(research_theme)
                        await websocket.send_text(json.dumps({"type": "info", "content": f"Researcher found new inspiration for '{research_theme}'."}))

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
                await websocket.send_text(json.dumps({"type": "info", "content": f"Character {char_data['name']} added."}))
                
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

    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.GENERATOR_HOST, port=config.GENERATOR_PORT)