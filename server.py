from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import db
import llm
import spark
import curator
import parser
import tts
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
                
                if user_input.lower() == "spark":
                    idea = spark.generate_spark()
                    await websocket.send_text(json.dumps({"type": "spark", "content": idea}))
                else:
                    # Get context
                    facts = curator.get_relevant_context(user_input)
                    await websocket.send_text(json.dumps({"type": "debug", "content": f"Using context: {facts}"}))
                    
                    full_response = ""
                    # Stream LLM output back to client
                    for chunk in llm.generate_story_segment(user_input, context_facts=facts):
                        await websocket.send_text(json.dumps({"type": "story_chunk", "content": chunk}))
                        full_response += chunk
                    
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
                
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.GENERATOR_HOST, port=config.GENERATOR_PORT)