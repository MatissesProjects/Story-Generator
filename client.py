import asyncio
import websockets
import json
import config
import requests
import os
import winsound
import argparse

async def receive_messages(websocket, generator_host, generator_port):
    try:
        while True:
            response = await websocket.recv()
            message = json.loads(response)
            
            if message["type"] == "story_chunk":
                print(message["content"], end="", flush=True)
            elif message["type"] == "spark":
                print(f"\nSpark:\n{message['content']}")
            elif message["type"] == "info":
                print(f"\n[INFO]: {message['content']}")
            elif message["type"] == "debug":
                # print(f"\n[DEBUG]: {message['content']}")
                pass
            elif message["type"] == "audio_event":
                # Download and play audio
                audio_url = f"http://{generator_host}:{generator_port}{message['url']}"
                file_name = os.path.basename(message["url"])
                
                # Fetch audio file via HTTP
                try:
                    r = requests.get(audio_url)
                    if r.status_code == 200:
                        local_audio = os.path.join(config.AUDIO_OUTPUT_DIR, file_name)
                        with open(local_audio, 'wb') as f:
                            f.write(r.content)
                        # Play it (try-except to avoid crash if audio device is busy or winsound fails)
                        try:
                            winsound.PlaySound(local_audio, winsound.SND_FILENAME)
                        except Exception as playback_error:
                            print(f"\n[Playback Error]: {playback_error}")
                except Exception as fetch_error:
                    print(f"\n[Audio Fetch Error]: {fetch_error}")
                    
    except Exception as e:
        print(f"Error receiving message: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Story Generator Client")
    parser.add_argument("--host", default="localhost", help="Generator PC IP (default: localhost)")
    parser.add_argument("--port", type=int, default=config.GENERATOR_PORT, help=f"Generator PC Port (default: {config.GENERATOR_PORT})")
    args = parser.parse_args()

    generator_host = args.host
    generator_port = args.port
    ws_url = f"ws://{generator_host}:{generator_port}/ws"
    
    if not os.path.exists(config.AUDIO_OUTPUT_DIR):
        os.makedirs(config.AUDIO_OUTPUT_DIR)
    
    async with websockets.connect(ws_url) as websocket:
        print(f"Connected to {ws_url}")
        print("Type your input or 'exit' to quit.")
        
        # Start background task for receiving
        asyncio.create_task(receive_messages(websocket, generator_host, generator_port))
        
        while True:
            user_input = await asyncio.get_event_loop().run_in_executor(None, input, "\nYou: ")
            if user_input.lower() == "exit":
                break
            
            if user_input.lower() == "add character":
                name = input("Name: ")
                desc = input("Description: ")
                traits = input("Traits: ")
                await websocket.send(json.dumps({"type": "add_character", "content": {"name": name, "description": desc, "traits": traits}}))
            elif user_input.lower() == "add lore":
                topic = input("Topic: ")
                desc = input("Description: ")
                await websocket.send(json.dumps({"type": "add_lore", "content": {"topic": topic, "description": desc}}))
            else:
                await websocket.send(json.dumps({"type": "user_input", "content": user_input}))

if __name__ == "__main__":
    asyncio.run(main())
