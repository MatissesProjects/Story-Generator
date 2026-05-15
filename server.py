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
import simulation_manager
import atmosphere_engine
import visual_curator
import config
import turn_orchestrator
import os
import json
import random
import asyncio
import uuid

app = FastAPI()

# Initialize the database on startup
db.init_db()

music = music_orchestrator.MusicOrchestrator()
world = world_engine.WorldEngine()
atmosphere = atmosphere_engine.AtmosphereEngine()
curator_visual = visual_curator.VisualCurator()

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

# Mount Ambiance if it exists
ambiance_path = os.path.join(config.AUDIO_SEQUENCER_PATH, "ambiance")
if os.path.exists(ambiance_path):
    app.mount("/ambiance", StaticFiles(directory=ambiance_path), name="ambiance")

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

@app.get("/asset/{asset_type}/{asset_name}")
async def get_asset(asset_type: str, asset_name: str):
    """
    Returns an asset if it exists, otherwise triggers on-demand generation.
    asset_type: 'portrait', 'environment', 'tile'
    """
    # Prefer cached path from curator if available
    if asset_name in curator_visual.entity_cache:
        cached_url = curator_visual.entity_cache[asset_name]
        # url is like /static/portraits/name_hash.png
        cached_path = cached_url.lstrip('/')
        if os.path.exists(cached_path):
            return FileResponse(cached_path)

    if asset_type == 'portrait':
        # Fallback to DB to find character for on-demand generation
        char = db.query_db("SELECT description, traits FROM characters WHERE name LIKE ?", (f"%{asset_name}%",), one=True)
        if char:
            # Namespaced: portrait/environment generation
            url = await vision.generate_portrait(asset_name, char['description'], char['traits'], session_id="default_session")
            curator_visual.entity_cache[asset_name] = url
            return FileResponse(url.lstrip('/'))
        else:
            return {"error": "Character not found for on-demand generation"}

    elif asset_type == 'environment':
        loc = db.query_db("SELECT description FROM locations WHERE name LIKE ?", (f"%{asset_name}%",), one=True)
        if loc:
            url = await vision.generate_environment(asset_name, loc['description'], session_id="default_session")
        else:
            # If we don't have it, we generate a generic one based on the name
            url = await vision.generate_environment(asset_name, f"A cinematic scene of {asset_name}", session_id="default_session")
        curator_visual.entity_cache[asset_name] = url
        return FileResponse(url.lstrip('/'))

    return {"error": "Invalid asset type"}

@app.get("/")
async def get():
    return FileResponse('static/index.html')

async def log_progress(websocket: WebSocket, message: str, level: str = "info"):
    """Logs progress to the server console and sends it to the client."""
    print(f"[{level.upper()}] {message}")
    await websocket.send_text(json.dumps({"type": "progress", "content": message, "level": level}))

# Track connected client capabilities
client_capabilities = {}
pending_vision_requests = {}
vision_lock = asyncio.Lock()

class VisionOrchestrator:
    async def request_generation(self, websocket: WebSocket, client_id: str, request_type: str, content: dict, session_id="default"):
        """
        Orchestrates image generation: local or offloaded to client.
        """
        capabilities = client_capabilities.get(client_id, {})
        
        # If client supports offloading and we want to offload
        if capabilities.get("can_offload_vision"):
            request_id = str(uuid.uuid4())
            event = asyncio.Event()

            name_key = content.get('name') or content.get('location_name') or content.get('biome')
            async with vision_lock:
                pending_vision_requests[request_id] = {"event": event, "url": None, "name_key": name_key}

            print(f"Vision: Offloading {request_type} to {client_id}")            
            await websocket.send_text(json.dumps({
                "type": "vision_request",
                "request_id": request_id,
                "request_type": request_type,
                "content": content
            }))
            
            # Wait for completion (with timeout)
            try:
                await asyncio.wait_for(event.wait(), timeout=60.0)
                async with vision_lock:
                    url = pending_vision_requests[request_id]["url"]
                    del pending_vision_requests[request_id]
                return url
            except asyncio.TimeoutError:
                print(f"Vision: Timeout offloading to {client_id}. Falling back to local.")
                async with vision_lock:
                    if request_id in pending_vision_requests:
                        del pending_vision_requests[request_id]
        
        # Fallback to local generation on the 4090
        if request_type == "portrait":
            url = await vision.generate_portrait(content['name'], content['description'], content['traits'], session_id=session_id)
        elif request_type == "environment":
            url = await vision.generate_environment(content['name'], content['description'], session_id=session_id)
        elif request_type == "map_tile":
            url = await vision.generate_map_tile(content['biome'], session_id=session_id)
        return url
        # Store in cache for consistent retrieval
        if url:
            name_key = content.get('name') or content.get('location_name') or content.get('biome')
            if name_key:
                async with vision_lock:
                    curator_visual.entity_cache[name_key] = url

        return url

vision_orchestrator = VisionOrchestrator()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = f"{websocket.client.host}:{websocket.client.port}"
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "handshake":
                capabilities = message["content"]
                client_capabilities[client_id] = capabilities
                print(f"Handshake accepted from {client_id}: {capabilities['gpu']} (Offload Vision: {capabilities['can_offload_vision']})")
                await websocket.send_text(json.dumps({"type": "info", "content": f"Handshake verified. Orchestrating for {capabilities['gpu']}."}))
                continue

            if message["type"] == "vision_complete":
                rid = message.get("request_id")
                url = message.get("url")
                async with vision_lock:
                    if rid in pending_vision_requests:
                        pending_vision_requests[rid]["url"] = url
                        name_key = pending_vision_requests[rid].get("name_key")
                        if name_key:
                            curator_visual.entity_cache[name_key] = url
                        pending_vision_requests[rid]["event"].set()
                continue

            if message["type"] == "user_input":
                try:
                    user_input = message["content"]
                    await log_progress(websocket, f"Received user input: '{user_input[:50]}...'")
                    await log_progress(websocket, "Analyzing intent...")
                    intent = parser.detect_intent(user_input)

                    if intent == 'SPARK':
                        await log_progress(websocket, "Conjuring a new story spark...")
                        await websocket.send_text(json.dumps({"type": "spark", "content": ""}))
                        genre = message.get("genre")
                        matrix = spark.PromptMatrix()
                        prompt = matrix.build_prompt(genre=genre)
                        full_spark = ""
                        stream_parser = parser.StreamParser()
                        async for chunk in llm.async_generate_story_segment(prompt, model=config.FAST_MODEL):
                            await websocket.send_text(json.dumps({"type": "story_chunk", "content": chunk}))
                            full_spark += chunk
                            completed_blocks = stream_parser.feed(chunk)
                            for speaker, text in completed_blocks:
                                voice_config = db.get_character_voice(speaker)
                                audio_path = await asyncio.to_thread(tts.generate_audio, text, speaker, voice_config=voice_config)
                                if audio_path:
                                    audio_url = f"/audio/{os.path.basename(audio_path)}"
                                    await websocket.send_text(json.dumps({"type": "audio_event", "url": audio_url, "speaker": speaker, "content": text}))
                        remaining_blocks = stream_parser.flush()
                        for speaker, text in remaining_blocks:
                            voice_config = db.get_character_voice(speaker)
                            audio_path = await asyncio.to_thread(tts.generate_audio, text, speaker, voice_config=voice_config)
                            if audio_path:
                                audio_url = f"/audio/{os.path.basename(audio_path)}"
                                await websocket.send_text(json.dumps({"type": "audio_event", "url": audio_url, "speaker": speaker, "content": text}))
                        await log_progress(websocket, "Spark conjured.", "success")
                    else:
                        await turn_orchestrator.process_turn(
                            websocket, client_id, user_input, intent,
                            log_progress, vision_orchestrator, music, world, atmosphere, curator_visual
                        )
                except Exception as e:
                    print(f"Server Error (user_input): {e}")
                    await websocket.send_text(json.dumps({"type": "error", "content": "An internal error occurred."}))
                    await log_progress(websocket, "Turn failed.", "error")
                continue
            elif message["type"] == "add_character":
                char_data = message["content"]
                
                # Auto-generate name if placeholder or missing
                name = char_data.get("name", "").strip()
                if not name or name.lower() in ["stranger", "mysterious figure", "unknown"]:
                    await log_progress(websocket, "Generating creative name for character...")
                    recent_history = db.get_recent_history(limit=5)
                    history_text = "\n".join([f"P: {h['user_input']}\nS: {h['assistant_response']}" for h in recent_history])
                    name = await director.generate_creative_name("character", history_text, theme=char_data.get("traits"))
                    char_data["name"] = name

                # Auto-generate tic if not provided
                tic = char_data.get("signature_tic")
                if not tic:
                    await log_progress(websocket, f"Generating signature tic for {char_data['name']}...")
                    tic = await director.generate_character_tic(char_data["name"], char_data["description"], char_data["traits"])

                db.add_character(
                    char_data["name"], 
                    char_data["description"], 
                    char_data["traits"], 
                    char_data.get("voice_id", config.DEFAULT_VOICE),
                    char_data.get("length_scale", 1.0),
                    char_data.get("noise_scale", 0.667),
                    char_data.get("noise_w", 0.8),
                    signature_tic=tic,
                    narrative_role=char_data.get("narrative_role", "NPC")
                )
                # Generate portrait in background
                async def background_portrait_gen(name, desc, traits):
                    try:
                        portrait_url = await vision_orchestrator.request_generation(websocket, client_id, "portrait", {"name": name, "description": desc, "traits": traits}, session_id="default_session")
                        curator_visual.entity_cache[name] = portrait_url
                        await websocket.send_text(json.dumps({"type": "portrait_update", "name": name, "url": portrait_url}))
                        await websocket.send_text(json.dumps({"type": "info", "content": f"Portrait for {name} generated."}))
                    except Exception as e:
                        print(f"Background Portrait Gen Error: {e}")
                
                asyncio.create_task(background_portrait_gen(char_data['name'], char_data['description'], char_data['traits']))
                
                await websocket.send_text(json.dumps({"type": "info", "content": f"Character {char_data['name']} added with tic: {tic}"}))
                await websocket.send_text(json.dumps({"type": "state_update_request"}))

            elif message["type"] == "get_creative_name":
                req = message["content"]
                await log_progress(websocket, f"Generating creative name for {req['category']}...")
                recent_history = db.get_recent_history(limit=5)
                history_text = "\n".join([f"P: {h['user_input']}\nS: {h['assistant_response']}" for h in recent_history])
                name = await director.generate_creative_name(req['category'], history_text, theme=req.get('theme'))
                await websocket.send_text(json.dumps({"type": "creative_name", "category": req['category'], "name": name}))

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
                filename = message.get("content", {}).get("filename") or message.get("filename")
                if not filename:
                    await websocket.send_text(json.dumps({"type": "error", "content": "No filename provided for load_arc"}))
                    continue
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
                pacing = message.get("content", {}).get("pacing") or message.get("pacing")
                if pacing:
                    db.set_story_state("current_pacing", pacing)
                    await websocket.send_text(json.dumps({"type": "info", "content": f"Pacing set to {pacing}."}))
                else:
                    await websocket.send_text(json.dumps({"type": "error", "content": "No pacing value provided"}))

            elif message["type"] == "get_state":
                def get_full_state():
                    seed = db.get_story_state("narrative_seed")
                    threads = db.get_active_plot_threads()
                    curr_loc_name = db.get_story_state("current_location")
                    curr_pacing = db.get_story_state("current_pacing") or "Exploration"

                    chars = db.query_db("SELECT id, name, description, traits, social, ambition, safety, resources, current_goal, current_task, signature_tic, narrative_role FROM characters")
                    char_list = []
                    for c in chars:
                        rel = db.get_relationship(0, c['id'])
                        char_list.append({
                            "name": c['name'],
                            "description": c['description'],
                            "traits": c['traits'],
                            "social": c['social'],
                            "ambition": c['ambition'],
                            "safety": c['safety'],
                            "resources": c['resources'],
                            "current_goal": c['current_goal'],
                            "current_task": c['current_task'],
                            "signature_tic": c['signature_tic'],
                            "narrative_role": c['narrative_role'],
                            "relationship": {
                                "trust": rel['trust'],
                                "fear": rel['fear'],
                                "affection": rel['affection']
                            }
                        })

                    quests = db.get_active_quests()
                    active_arc = db.get_active_arc()
                    milestone_idx = db.get_current_milestone_index()
                    inventory = db.get_inventory("player", 0)
                    stats = db.get_entity_stats("player", 0)
                    
                    return seed, threads, curr_loc_name, curr_pacing, char_list, quests, active_arc, milestone_idx, inventory, stats

                seed, threads, curr_loc_name, curr_pacing, char_list, quests, active_arc, milestone_idx, inventory, stats = await asyncio.to_thread(get_full_state)

                loc_url = None
                if curr_loc_name:
                    if curr_loc_name in curator_visual.entity_cache:
                        loc_url = curator_visual.entity_cache[curr_loc_name]
                    else:
                        safe_name = "".join([char for char in curr_loc_name if char.isalnum()]).lower()
                        loc_path = os.path.join(config.ENVIRONMENTS_DIR, f"{safe_name}.png")
                        loc_url = f"/static/environments/{safe_name}.png" if os.path.exists(loc_path) else None

                # Post-process character list to add cached portrait URLs (done on main thread since it touches global cache)
                for char in char_list:
                    url = None
                    if char['name'] in curator_visual.entity_cache:
                        url = curator_visual.entity_cache[char['name']]
                    else:
                        safe_name = "".join([c for c in char['name'] if c.isalnum()]).lower()
                        portrait_path = os.path.join(config.PORTRAITS_DIR, f"{safe_name}.png")
                        url = f"/static/portraits/{safe_name}.png" if os.path.exists(portrait_path) else None
                    char['portrait'] = url

                await websocket.send_text(json.dumps({
                    "type": "state_update", 
                    "seed": seed, 
                    "threads": [t['description'] for t in threads],
                    "characters": char_list,
                    "quests": [dict(q) for q in quests],
                    "location": curr_loc_name,
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

            elif message["type"] == "reset_story":
                await log_progress(websocket, "Resetting story database...")
                db.clear_all_data()
                curator_visual.entity_cache = {}
                await websocket.send_text(json.dumps({"type": "info", "content": "Story database cleared. Starting fresh."}))
                await websocket.send_text(json.dumps({"type": "state_update_request"}))

            elif message["type"] == "get_map":
                locations = db.get_all_locations()
                paths = db.get_all_paths()
                loc_list = []
                for l in locations:
                    ldict = dict(l)
                    if ldict['biome_type']:
                        ldict['tile_url'] = await vision_orchestrator.request_generation(websocket, client_id, "map_tile", {"biome": ldict['biome_type']})
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
                snap_id = message.get("content", {}).get("snapshot_id") or message.get("snapshot_id")
                if not snap_id:
                    await websocket.send_text(json.dumps({"type": "error", "content": "No snapshot_id provided"}))
                    continue
                snap = db.query_db("SELECT * FROM snapshots WHERE id = ?", (snap_id,), one=True)
                if snap:
                    db.execute_db(
                        "UPDATE story_heads SET current_snapshot_id = ? WHERE session_id = ?",
                        (snap_id, "default_session")
                    )
                    db.set_story_state("narrative_seed", snap['narrative_seed'])
                    if snap['location_id']:
                        loc = db.get_location(snap['location_id'])
                        if loc:
                            db.set_story_state("current_location", loc['name'])

                    await websocket.send_text(json.dumps({"type": "info", "content": f"Switched to turn {snap['turn_number']}."}))
                    await websocket.send_text(json.dumps({"type": "state_update_request"}))


    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    # Set generous ping timeouts for long LLM generation sessions
    uvicorn.run(
        app, 
        host=config.GENERATOR_HOST, 
        port=config.GENERATOR_PORT,
        ws_ping_interval=300.0,
        ws_ping_timeout=300.0
    )
