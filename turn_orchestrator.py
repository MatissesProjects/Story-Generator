import json
import asyncio
import os
import time

import db
import llm
import curator
import parser
import tts
import director
import summarizer
import researcher
import validator
import dicemaster
import social_engine
import foreshadowing
import canon_checker
import simulation_manager
import config

async def process_turn(
    websocket, client_id, user_input, intent,
    log_progress, vision_orchestrator, music, world, atmosphere, curator_visual
):
    # Modify prompt for continuation
    if intent in ['CONTINUE', 'EMPTY']:
        prompt = "The player is waiting for the story to continue. Describe the next sequence of events, focusing on atmospheric detail and character reaction. Do not wait for player input yet. Only write the next segment of dialogue/action."
    else:
        prompt = user_input

    # --- PHASE 1: Parallel Context & Planning ---
    start_phase = time.time()
    await log_progress(websocket, "Parallel processing: context, planning, and validation...")
    
    # Get shared state in a background thread to prevent event loop blocking
    def get_turn_state():
        return (
            db.get_inventory("player", 0),
            db.get_entity_stats("player", 0),
            db.get_active_plot_threads(),
            db.get_active_quests(),
            db.get_recent_history(limit=10),
            db.get_story_state("current_location") or "Unknown"
        )
    
    state_task = asyncio.to_thread(get_turn_state)
    
    # 1. Context retrieval (Sync but in thread)
    context_task = asyncio.to_thread(curator.get_relevant_context, user_input)
    
    # Fetch state
    start_state = time.time()
    player_inv, player_stats, active_threads, active_quests, recent_history, curr_loc_name = await state_task
    print(f"DEBUG: State retrieval took {time.time() - start_state:.2f}s")
    
    # 2. Director Action Plan (Async)
    plan_task = director.generate_action_plan(user_input, recent_history, active_threads, active_quests, current_location=curr_loc_name)
    
    # 3. HTN Plan Generation (if needed)
    active_plan = db.get_active_plan()
    if not active_plan and intent != 'SPARK':
        # Auto-generate a new plan for the mystery
        await director.generate_narrative_plan("solve_mystery")
        active_plan = db.get_active_plan()

    # Wait for context first
    start_context = time.time()
    facts = await context_task
    print(f"DEBUG: Context retrieval took {time.time() - start_context:.2f}s")
    
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
    
    start_gather = time.time()
    gathered_results = await asyncio.gather(*tasks_to_gather, return_exceptions=True)
    print(f"DEBUG: Gathered remaining tasks in {time.time() - start_gather:.2f}s")
    print(f"DEBUG: Total parallel phase took {time.time() - start_phase:.2f}s")
    
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
        return

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
        
        # Immediately inform frontend of location change so text can flow
        await websocket.send_text(json.dumps({"type": "scene_update", "location": loc['name']}))
        
        # Generate environment image in background so it doesn't block LLM
        async def background_env_gen(loc_name, loc_desc):
            try:
                env_url = await vision_orchestrator.request_generation(websocket, client_id, "environment", {"name": loc_name, "description": loc_desc}, session_id="default_session")
                if env_url:
                    await websocket.send_text(json.dumps({"type": "scene_update", "location": loc_name, "url": env_url}))
            except Exception as e:
                print(f"Background Env Gen Error: {e}")
                
        asyncio.create_task(background_env_gen(loc['name'], loc['desc']))
        curr_loc_name = loc['name']

    # --- PHASE 3: Generation ---
    turn_count = db.get_history_count()
    director_instructions = director.evaluate_state(user_input)
    persona_blocks = director.get_persona_blocks(user_input, current_turn=turn_count)
    narrative_seed = db.get_story_state("narrative_seed")
    current_pacing = db.get_story_state("current_pacing") or "Exploration"

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
                    await websocket.send_text(json.dumps({
                        "type": "audio_event", 
                        "url": audio_url, 
                        "speaker": speaker,
                        "content": text
                    }))
                    
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
            await websocket.send_text(json.dumps({
                "type": "audio_event", 
                "url": audio_url, 
                "speaker": speaker,
                "content": text
            }))
            
            # Final visual sync
            current_entities = [name for name in db.get_all_entities() if name.lower() in full_response.lower()]
            current_atmos = atmosphere.get_atmosphere_by_mood(current_pacing)
            vstack = curator_visual.get_visual_stack(curr_loc_name, current_entities, current_atmos, primary_entity=speaker)
            await websocket.send_text(json.dumps({"type": "visual_update", "content": vstack}))

    db.log_history(user_input, full_response)

    # --- PHASE 4: Post-Generation Tasks (Parallel) ---
    await log_progress(websocket, "Finalizing turn processing...")
    
    # 1. HTN Plan Verification
    active_plan = db.get_active_plan()
    if active_plan:
        idx = active_plan['current_task_index']
        tasks = active_plan['task_sequence']
        if idx < len(tasks):
            current_task = tasks[idx]
            import htn_monitor
            success, explanation = await htn_monitor.verify_task_completion(current_task, f"Player: {user_input}\nStory: {full_response}")
            if success:
                print(f"HTN Monitor: Task '{current_task}' completed! {explanation}")
                db.update_plan_progress(idx + 1)
                await websocket.send_text(json.dumps({
                    "type": "info", 
                    "content": f"Narrative Goal Advanced: {explanation}"
                }))
                if idx + 1 >= len(tasks):
                    db.complete_active_plan('completed')
                    await websocket.send_text(json.dumps({"type": "info", "content": f"Narrative Arc '{active_plan['goal_name']}' Completed!"}))

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
        
        sudden_text = f"[SUDDEN EVENT] {initiative}"
        voice_config = db.get_character_voice("Narrator")
        audio_path = await asyncio.to_thread(tts.generate_audio, sudden_text, "Narrator", voice_config=voice_config)
        if audio_path:
            audio_url = f"/audio/{os.path.basename(audio_path)}"
            await websocket.send_text(json.dumps({
                "type": "audio_event", 
                "url": audio_url, 
                "speaker": "Narrator",
                "content": sudden_text
            }))
            
        full_response += f"\n\n[Narrator]: {sudden_text}"
        db.log_history("DIRECTOR_INITIATIVE", initiative)

    # Commit Snapshot
    loc_id = None
    if curr_loc_name:
        loc_obj = db.get_location_by_name(curr_loc_name)
        loc_id = loc_obj['id'] if loc_obj else None
    db.commit_snapshot("default_session", user_input, full_response, narrative_seed, loc_id)

    # Periodic Maintenance: Summary and Plot Thread Analysis
    h_count = db.get_history_count()
    needs_state_update = False

    # 1. Update Narrative Seed (Summary) & Analyze Plot Threads every 3 turns
    if h_count > 0 and h_count % 3 == 0:
        await log_progress(websocket, "Updating story summary and analyzing plot threads...")
        
        # Update Summary
        await summarizer.update_narrative_seed()
        await websocket.send_text(json.dumps({"type": "info", "content": "Narrative summary updated."}))
        needs_state_update = True
        
        # Analyze Plot Threads
        thread_updates = await director.analyze_plot_threads(recent_history, active_threads)
        
        for tid in thread_updates.get("resolved_ids", []):
            db.update_plot_thread_status(tid, "resolved")
            await websocket.send_text(json.dumps({"type": "info", "content": f"Plot Thread Resolved: {tid}"}))
            
        for desc in thread_updates.get("new_threads", []):
            db.add_plot_thread(desc)
            await websocket.send_text(json.dumps({"type": "info", "content": f"New Plot Thread Discovered: {desc}"}))

    if needs_state_update:
        await websocket.send_text(json.dumps({"type": "state_update_request"}))

    # Global Simulation Tick (Every 5 turns)
    if db.get_history_count() % 5 == 0:
        await log_progress(websocket, "Triggering global simulation tick...")
        sim_events = await simulation_manager.trigger_tick()
        if sim_events:
            print(f"Simulation tick completed with {len(sim_events)} events.")
            # Notify the user of background developments
            for event in sim_events:
                await websocket.send_text(json.dumps({
                    "type": "info", 
                    "content": f"Background Development: {event.get('description')}"
                }))

    await log_progress(websocket, "Turn complete.", "success")
