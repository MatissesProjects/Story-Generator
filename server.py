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
            url = await vision.generate_portrait(asset_name, char['description'], char['traits'])
            curator_visual.entity_cache[asset_name] = url
            return FileResponse(url.lstrip('/'))
        else:
            return {"error": "Character not found for on-demand generation"}

    elif asset_type == 'environment':
        loc = db.query_db("SELECT description FROM locations WHERE name LIKE ?", (f"%{asset_name}%",), one=True)
        if loc:
            url = await vision.generate_environment(asset_name, loc['description'])
        else:
            # If we don't have it, we generate a generic one based on the name
            url = await vision.generate_environment(asset_name, f"A cinematic scene of {asset_name}")
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

class VisionOrchestrator:
    async def request_generation(self, websocket: WebSocket, client_id: str, request_type: str, content: dict):
        """
        Orchestrates image generation: local or offloaded to client.
        """
        capabilities = client_capabilities.get(client_id, {})
        
        # If client supports offloading and we want to offload
        if capabilities.get("can_offload_vision"):
            request_id = str(uuid.uuid4())
            event = asyncio.Event()

            name_key = content.get('name') or content.get('location_name') or content.get('biome')
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
                url = pending_vision_requests[request_id]["url"]
                del pending_vision_requests[request_id]
                return url
            except asyncio.TimeoutError:
                print(f"Vision: Timeout offloading to {client_id}. Falling back to local.")
                if request_id in pending_vision_requests:
                    del pending_vision_requests[request_id]
        
        # Fallback to local generation on the 4090
        if request_type == "portrait":
            url = await vision.generate_portrait(content['name'], content['description'], content['traits'])
        elif request_type == "environment":
            url = await vision.generate_environment(content['name'], content['description'])
        elif request_type == "map_tile":
            url = await vision.generate_map_tile(content['biome'])

        # Store in cache for consistent retrieval
        if url:
            name_key = content.get('name') or content.get('location_name') or content.get('biome')
            if name_key:
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
                if rid in pending_vision_requests:
                    pending_vision_requests[rid]["url"] = url
                    # Also try to update entity_cache if we can find the name
                    name_key = pending_vision_requests[rid].get("name_key")
                    if name_key:
                        curator_visual.entity_cache[name_key] = url
                    pending_vision_requests[rid]["event"].set()
                continue

            if message["type"] == "user_input":
                user_input = message["content"]
                await log_progress(websocket, f"Received user input: '{user_input[:50]}...'")
                
                await log_progress(websocket, "Analyzing intent...")
                intent = parser.detect_intent(user_input)

                if intent == 'SPARK':
                    await log_progress(websocket, "Conjuring a new story spark...")
                    
                    # Notify client that a spark is starting
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
                                await websocket.send_text(json.dumps({"type": "audio_event", "url": audio_url, "speaker": speaker}))

                    remaining_blocks = stream_parser.flush()
                    for speaker, text in remaining_blocks:
                        voice_config = db.get_character_voice(speaker)
                        audio_path = await asyncio.to_thread(tts.generate_audio, text, speaker, voice_config=voice_config)
                        if audio_path:
                            audio_url = f"/audio/{os.path.basename(audio_path)}"
                            await websocket.send_text(json.dumps({"type": "audio_event", "url": audio_url, "speaker": speaker}))

                    await log_progress(websocket, "Spark conjured.", "success")
                else:
                    # Modify prompt for continuation
                    if intent in ['CONTINUE', 'EMPTY']:
                        prompt = "The player is waiting for the story to continue. Describe the next sequence of events, focusing on atmospheric detail and character reaction. Do not wait for player input yet. Only write the next segment of dialogue/action."
                    else:
                        prompt = user_input

                    # --- PHASE 1: Parallel Context & Planning ---
                    await log_progress(websocket, "Parallel processing: context, planning, and validation...")
                    
                    # Get shared state
                    player_inv = db.get_inventory("player", 0)
                    player_stats = db.get_entity_stats("player", 0)
                    active_threads = db.get_active_plot_threads()
                    active_quests = db.get_active_quests()
                    recent_history = db.get_recent_history(limit=10)
                    
                    # 1. Context retrieval (Sync but in thread)
                    context_task = asyncio.to_thread(curator.get_relevant_context, user_input)
                    
                    # 2. Director Action Plan (Async)
                    plan_task = director.generate_action_plan(user_input, recent_history, active_threads, active_quests)
                    
                    # Start context task and plan task
                    facts_future = context_task
                    
                    # We need facts for validation and dicemaster, so we wait for context first
                    facts = await facts_future
                    
                    # 3. Validation & DiceMaster (using facts)
                    val_task = None
                    if intent in ['ACTION', 'DIALOGUE']:
                        val_task = validator.validate_action(user_input, facts, inventory=player_inv, stats=player_stats)
                    
                    dice_task = None
                    if intent == 'ACTION':
                        dice_task = dicemaster.perform_hidden_check(user_input, facts)

                    # Gather results
                    tasks_to_gather = [plan_task]
                    if val_task: tasks_to_gather.append(val_task)
                    if dice_task: tasks_to_gather.append(dice_task)
                    
                    gathered_results = await asyncio.gather(*tasks_to_gather, return_exceptions=True)
                    
                    # 1. Action Plan
                    plan = gathered_results[0]
                    if isinstance(plan, Exception):
                        print(f"Director Error: {plan}")
                        await websocket.send_text(json.dumps({"type": "debug", "content": f"Director failed: {plan}"}))
                        # Fallback empty plan
                        plan = {
                            "needs_research": False,
                            "research_theme": "",
                            "quest_updates": [],
                            "milestone_completed": False,
                            "new_location": None
                        }
                    
                    idx = 1
                    
                    # 2. Validation
                    validation_result = (True, "")
                    if val_task:
                        val_res = gathered_results[idx]
                        if isinstance(val_res, Exception):
                            print(f"Validator Error: {val_res}")
                            # If validator fails, assume valid but log it
                            validation_result = (True, "")
                        else:
                            validation_result = val_res
                        idx += 1
                    
                    # 3. DiceMaster
                    mechanical_result = ""
                    if dice_task:
                        dice_res = gathered_results[idx]
                        if isinstance(dice_res, Exception):
                            print(f"DiceMaster Error: {dice_res}")
                        elif isinstance(dice_res, tuple) and len(dice_res) == 5:
                            success, roll, dc, sides, reason = dice_res
                            res_str = "SUCCESS" if success else "FAILURE"
                            mechanical_result = f"MECHANICAL RESULT: {res_str} (Rolled {roll} vs DC {dc} on a D{sides}). Narrate the outcome accordingly."
                            await websocket.send_text(json.dumps({"type": "debug", "content": f"DiceMaster: {mechanical_result} - {reason}"}))
                        idx += 1

                    # Logic Validation Check
                    if not validation_result[0]:
                        await websocket.send_text(json.dumps({"type": "validation_failure", "content": validation_result[1]}))
                        continue

                    # --- PHASE 2: Execute Plan Updates ---
                    # 1. Discover any new characters mentioned in the input or plan
                    await social_engine.discover_new_characters(user_input)

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
                            await summarizer.update_narrative_seed()
                        else:
                            await websocket.send_text(json.dumps({"type": "info", "content": "Adventure Arc Completed!"}))

                    if plan['new_location']:
                        loc = plan['new_location']
                        await world.resolve_new_location(loc['name'], loc['desc'], relative_to_name=loc['rel_to'], direction=loc['direction'])
                        db.set_story_state("current_location", loc['name'])
                        world.move_entity("player", 0, loc['name'])
                        
                        env_url = await vision_orchestrator.request_generation(websocket, client_id, "environment", {"name": loc['name'], "description": loc['desc']})
                        await websocket.send_text(json.dumps({"type": "scene_update", "location": loc['name'], "url": env_url}))

                    # --- PHASE 3: Generation ---
                    turn_count = db.get_history_count()
                    director_instructions = director.evaluate_state(user_input)
                    persona_blocks = director.get_persona_blocks(user_input, current_turn=turn_count)
                    narrative_seed = db.get_story_state("narrative_seed")
                    current_pacing = db.get_story_state("current_pacing") or "Exploration"
                    curr_loc_name = db.get_story_state("current_location") or "Unknown"

                    # Foreshadowing check
                    foreshadow_note = ""
                    try:
                        payoff = await foreshadowing.check_for_payoff(recent_history)
                        if payoff:
                            payoff_id, element_name, foreshadow_note = payoff
                            db.resolve_foreshadowing(payoff_id)
                            await websocket.send_text(json.dumps({"type": "info", "content": f"Foreshadowing payoff: {element_name}"}))
                    except Exception as e:
                        print(f"Error in foreshadowing payoff check: {e}")
                        await websocket.send_text(json.dumps({"type": "debug", "content": f"Foreshadowing check failed: {e}"}))

                    await websocket.send_text(json.dumps({"type": "debug", "content": f"Intent: {intent}, Using context: {len(facts)} facts, Director: {director_instructions is not None}, Personas: {len(persona_blocks)}, Seed: {narrative_seed is not None}"}))

                    full_response = ""
                    await log_progress(websocket, "Generating story response...")
                    stream_parser = parser.StreamParser()

                    chunk_count = 0
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
                        chunk_count += 1
                        
                        # Aggressive discovery: if the chunk contains a potential tag end ':', scan immediately
                        if ':' in chunk or chunk_count % 5 == 0:
                            # Kick off discovery in background to avoid blocking text flow
                            asyncio.create_task(social_engine.discover_new_characters(full_response))
                        
                        # Real-time audio and visual parsing
                        completed_blocks = stream_parser.feed(chunk)
                        if completed_blocks:
                            # Final safety discovery check before TTS processing (keep this awaited to ensure pre-registration)
                            await social_engine.discover_new_characters(full_response)
                            
                            for speaker, text in completed_blocks:
                                voice_config = db.get_character_voice(speaker)
                                # Offload CPU-heavy synchronous TTS generation to a thread
                                audio_path = await asyncio.to_thread(tts.generate_audio, text, speaker, voice_config=voice_config)
                                if audio_path:
                                    audio_url = f"/audio/{os.path.basename(audio_path)}"
                                    await websocket.send_text(json.dumps({"type": "audio_event", "url": audio_url, "speaker": speaker}))
                                    
                                    # Send visual sync for the speaker
                                    current_entities = [name for name in db.get_all_entities() if name.lower() in full_response.lower()]
                                    current_atmos = atmosphere.get_atmosphere_by_mood(current_pacing) # Fallback atmosphere
                                    vstack = curator_visual.get_visual_stack(curr_loc_name, current_entities, current_atmos, primary_entity=speaker)
                                    await websocket.send_text(json.dumps({"type": "visual_update", "content": vstack}))

                    # Final flush for any remaining text in buffer
                    remaining_blocks = stream_parser.flush()
                    if remaining_blocks:
                        await social_engine.discover_new_characters(full_response)
                        
                    for speaker, text in remaining_blocks:
                        voice_config = db.get_character_voice(speaker)
                        audio_path = await asyncio.to_thread(tts.generate_audio, text, speaker, voice_config=voice_config)
                        if audio_path:
                            audio_url = f"/audio/{os.path.basename(audio_path)}"
                            await websocket.send_text(json.dumps({"type": "audio_event", "url": audio_url, "speaker": speaker}))
                            
                            # Final visual sync
                            current_entities = [name for name in db.get_all_entities() if name.lower() in full_response.lower()]
                            current_atmos = atmosphere.get_atmosphere_by_mood(current_pacing)
                            vstack = curator_visual.get_visual_stack(curr_loc_name, current_entities, current_atmos, primary_entity=speaker)
                            await websocket.send_text(json.dumps({"type": "visual_update", "content": vstack}))

                    db.log_history(user_input, full_response)

                    # --- PHASE 4: Post-Generation Tasks (Parallel) ---
                    await log_progress(websocket, "Finalizing turn processing...")
                    
                    post_tasks = [
                        foreshadowing.extract_seeds(full_response, curr_loc_name),
                        canon_checker.extract_claims(full_response),
                        social_engine.update_social_state(user_input, full_response, current_turn=turn_count),
                        music.detect_mood(full_response),
                        atmosphere.detect_atmosphere(full_response, curr_loc_name)
                    ]
                    
                    post_results = await asyncio.gather(*post_tasks, return_exceptions=True)
                    
                    # Log any exceptions from post-tasks
                    for i, res in enumerate(post_results):
                        if isinstance(res, Exception):
                            task_name = ["Seeds", "Claims", "Social", "Music", "Atmos"][i]
                            print(f"Post-task '{task_name}' failed: {res}")
                            await websocket.send_text(json.dumps({"type": "debug", "content": f"Post-task '{task_name}' failed: {res}"}))

                    # Canon consistency check
                    claims = post_results[1] if not isinstance(post_results[1], Exception) else None
                    if claims:
                        try:
                            contradictions = await canon_checker.check_for_contradictions(claims, facts)
                            if contradictions:
                                for c in contradictions:
                                    resolution = await canon_checker.resolve_contradiction(c, facts)
                                    if resolution:
                                        msg = f"Canon Alert: {c['violation']} -> Resolved via {resolution['resolution_type']}"
                                        await websocket.send_text(json.dumps({"type": "info", "content": msg}))
                                    else:
                                        await websocket.send_text(json.dumps({"type": "info", "content": f"Canon Warning: {c['violation']}"}))
                        except Exception as e:
                            print(f"Error in canon contradiction check: {e}")

                    # Music selection
                    if config.MUSIC_ENABLED:
                        # Priority 1: Leitmotif (Character Theme)
                        leitmotif = music.get_leitmotif(full_response)
                        if leitmotif:
                            file_path = leitmotif['file_path']
                            # Determine URL (Check if it's in music_examples or gen_assets)
                            url = ""
                            if "musicExamples" in file_path:
                                url = f"/music_examples/{os.path.basename(file_path)}"
                            elif "generated_assets" in file_path:
                                url = f"/gen_assets/{os.path.basename(file_path)}"
                            else:
                                # Fallback/External
                                url = f"/audio/{os.path.basename(file_path)}"
                            
                            await websocket.send_text(json.dumps({
                                "type": "music_event", 
                                "url": url, 
                                "mood": f"Leitmotif: {leitmotif['character']}", 
                                "filename": leitmotif['filename'],
                                "is_leitmotif": True
                            }))
                        else:
                            # Priority 2: Mood-based track
                            mood = post_results[3]
                            if db.get_history_count() % 3 == 0 or plan['new_location']:
                                track = music.select_track(mood)
                                if track:
                                    file_path = track['file_path']
                                    url = f"/music_examples/{os.path.basename(file_path)}" if "musicExamples" in file_path else f"/gen_assets/{os.path.basename(file_path)}"
                                    await websocket.send_text(json.dumps({
                                        "type": "music_event", 
                                        "url": url, 
                                        "mood": mood, 
                                        "filename": track['filename'],
                                        "is_leitmotif": False
                                    }))

                    # Atmosphere update
                    atmos_data = post_results[4]
                    await websocket.send_text(json.dumps({"type": "atmosphere_update", "content": atmos_data}))

                    # Final Visual Stack curation (sync with end of text)
                    current_entities = [name for name in db.get_all_entities() if name.lower() in full_response.lower()]
                    visual_stack = curator_visual.get_visual_stack(curr_loc_name, current_entities, atmos_data)
                    await websocket.send_text(json.dumps({"type": "visual_update", "content": visual_stack}))

                    # Ambiance loop selection
                    if config.MUSIC_ENABLED:
                        amb_filename = atmosphere.get_ambiance_filename(atmos_data.get('ambiance', 'silence'))
                        if amb_filename:
                            amb_url = f"/ambiance/{amb_filename}"
                            await websocket.send_text(json.dumps({"type": "ambiance_event", "url": amb_url}))

                    # Research injection
                    if plan['needs_research']:
                        await websocket.send_text(json.dumps({"type": "info", "content": f"Director suggests research mission: '{plan['research_theme']}'"}))
                        await researcher.perform_research_injection(plan['research_theme'], context=full_response)
                        await websocket.send_text(json.dumps({"type": "info", "content": f"Researcher injected new inspiration for '{plan['research_theme']}'."}))

                    # Proactive Initiative
                    if intent in ['CONTINUE', 'EMPTY'] and not plan['new_location'] and not plan['quest_updates']:
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

                    # Periodic Maintenance: Summary and Plot Thread Analysis
                    if db.get_history_count() % 3 == 0:
                        await log_progress(websocket, "Analyzing plot threads and updating summary...")
                        
                        # 1. Update Narrative Seed (Summary)
                        if db.get_history_count() % 10 == 0:
                            await summarizer.update_narrative_seed()
                            await websocket.send_text(json.dumps({"type": "info", "content": "Narrative summary updated."}))
                        
                        # 2. Analyze Plot Threads
                        thread_updates = await director.analyze_plot_threads(recent_history, active_threads)
                        
                        for tid in thread_updates.get("resolved_ids", []):
                            db.update_plot_thread_status(tid, "resolved")
                            await websocket.send_text(json.dumps({"type": "info", "content": f"Plot Thread Resolved: {tid}"}))
                            
                        for desc in thread_updates.get("new_threads", []):
                            db.add_plot_thread(desc)
                            await websocket.send_text(json.dumps({"type": "info", "content": f"New Plot Thread Discovered: {desc}"}))
                        
                        if thread_updates.get("resolved_ids") or thread_updates.get("new_threads"):
                             await websocket.send_text(json.dumps({"type": "state_update_request"}))

                    # Global Simulation Tick (Every 5 turns)
                    if db.get_history_count() % 5 == 0:
                        await log_progress(websocket, "Triggering global simulation tick...")
                        sim_events = await simulation_manager.trigger_tick()
                        if sim_events:
                            # We don't necessarily show these to the user, 
                            # but they are logged and will affect future context.
                            print(f"Simulation tick completed with {len(sim_events)} events.")

                await log_progress(websocket, "Turn complete.", "success")

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
                portrait_url = await vision_orchestrator.request_generation(websocket, client_id, "portrait", {"name": char_data['name'], "description": char_data['description'], "traits": char_data['traits']})
                curator_visual.entity_cache[char_data['name']] = portrait_url
                await websocket.send_text(json.dumps({"type": "info", "content": f"Character {char_data['name']} added with portrait and tic: {tic}"}))
                await websocket.send_text(json.dumps({"type": "portrait_update", "name": char_data["name"], "url": portrait_url}))
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
                seed = db.get_story_state("narrative_seed")
                threads = db.get_active_plot_threads()
                curr_loc_name = db.get_story_state("current_location")
                curr_pacing = db.get_story_state("current_pacing") or "Exploration"

                loc_url = None
                if curr_loc_name:
                    if curr_loc_name in curator_visual.entity_cache:
                        loc_url = curator_visual.entity_cache[curr_loc_name]
                    else:
                        safe_name = "".join([char for char in curr_loc_name if char.isalnum()]).lower()
                        loc_path = os.path.join(config.ENVIRONMENTS_DIR, f"{safe_name}.png")
                        loc_url = f"/static/environments/{safe_name}.png" if os.path.exists(loc_path) else None

                chars = db.query_db("SELECT id, name, description, traits, social, ambition, safety, resources, current_goal, current_task, signature_tic, narrative_role FROM characters")
                char_list = []
                for c in chars:
                    url = None
                    if c['name'] in curator_visual.entity_cache:
                        url = curator_visual.entity_cache[c['name']]
                    else:
                        safe_name = "".join([char for char in c['name'] if char.isalnum()]).lower()
                        portrait_path = os.path.join(config.PORTRAITS_DIR, f"{safe_name}.png")
                        url = f"/static/portraits/{safe_name}.png" if os.path.exists(portrait_path) else None
                    
                    rel = db.get_relationship(0, c['id'])
                    char_list.append({
                        "name": c['name'],
                        "description": c['description'],
                        "traits": c['traits'],
                        "portrait": url,
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
