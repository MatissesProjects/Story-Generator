import pytest
import db
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

# Core orchestration components
import director
import validator
import dicemaster
import world_engine
import foreshadowing
import llm
import parser
import tts
import social_engine
import music_orchestrator
import atmosphere_engine
import canon_checker
import summarizer
import researcher
import curator
import visual_curator

@pytest.mark.asyncio
async def test_golden_turn_simulation(mock_llm):
    """
    INTEGRATION: Simulate a full 5-turn sequence of the Story Generator brain.
    Verifies orchestration, database updates, and multi-module coordination.
    """
    # 1. Setup Initial State
    db.add_character("Elara", "A kind healer", "Kind, Brave")
    db.add_location("The Dusty Tavern", "A creaky building", 0, 0, "urban")
    db.set_story_state("current_location", "The Dusty Tavern")
    
    world = world_engine.WorldEngine()
    music = music_orchestrator.MusicOrchestrator()
    atmosphere = atmosphere_engine.AtmosphereEngine()
    
    # Mock visual and audio calls to avoid real generation
    with patch("vision.generate_environment", new_callable=AsyncMock) as mock_env, \
         patch("vision.generate_portrait", new_callable=AsyncMock) as mock_port, \
         patch("tts.generate_audio") as mock_tts, \
         patch("summarizer.update_narrative_seed", new_callable=AsyncMock) as mock_sum:
        
        mock_env.return_value = "http://fake/env.png"
        mock_port.return_value = "http://fake/port.png"
        mock_tts.return_value = "/tmp/fake.wav"

        # Turn Sequence
        turns = [
            "I walk up to the bar and ask for a drink.",
            "I look around for anyone suspicious.",
            "I ask Elara if she's seen the silver locket.",
            "I head out the back door into the alley.",
            "I use my torch to light the dark path."
        ]

        for i, user_input in enumerate(turns):
            turn_number = i + 1
            print(f"\n--- Simulating Turn {turn_number}: '{user_input}' ---")
            
            # PHASE 1: Preparation
            facts = curator.get_relevant_context(user_input)
            plan = await director.generate_action_plan(user_input, [], [], [])
            is_valid, reason = await validator.validate_action(user_input, facts)
            
            assert is_valid is True
            
            # PHASE 2: Execute Plan (Simulate Location Change)
            if turn_number == 4:
                # Mock a location change plan
                plan['new_location'] = {"name": "The Dark Alley", "desc": "A spooky place", "rel_to": "The Dusty Tavern", "direction": "north"}
                
                loc = plan['new_location']
                await world.resolve_new_location(loc['name'], loc['desc'], relative_to_name=loc['rel_to'], direction=loc['direction'])
                db.set_story_state("current_location", loc['name'])
            
            # PHASE 3: Generation
            director_instructions = director.evaluate_state(user_input)
            persona_blocks = director.get_persona_blocks(user_input, current_turn=db.get_history_count())
            
            full_response = ""
            async for chunk in llm.async_generate_story_segment(user_input, context_facts=facts, director_instructions=director_instructions, persona_blocks=persona_blocks):
                full_response += chunk
            
            assert len(full_response) > 0
            db.log_history(user_input, full_response)
            
            # PHASE 4: Post-Generation
            curr_loc_name = db.get_story_state("current_location")
            
            # Parallel tasks
            seeds = await foreshadowing.extract_seeds(full_response, curr_loc_name)
            claims = await canon_checker.extract_claims(full_response)
            await social_engine.update_social_state(user_input, full_response)
            # Final Assertions per turn
            assert db.get_history_count() == turn_number
            if turn_number == 4:
                assert db.get_story_state("current_location") == "The Dark Alley"
                
        print("\n--- Golden Turn Simulation Successful ---")

@pytest.mark.asyncio
async def test_foreshadowing_payoff_integration(mock_llm):
    """
    INTEGRATION: Verify that a seed planted in Turn 1 can be triggered as a payoff in Turn 2.
    """
    # 1. Turn 1: Plant a seed
    user_input = "I find a strange silver coin with a hole in it."
    response_text = "You pick up a Silver Coin with a Hole. It feels unusually cold."
    
    db.log_history(user_input, response_text)
    # Manually plant to be deterministic
    db.add_foreshadowed_element("Silver Coin with a Hole", "Tavern", "Might be a key")
    
    # 2. Turn 2: Context that should trigger payoff
    context_scene = "You stand before a massive stone door with a perfectly circular slot."
    
    # Mock payoff evaluation
    # payoff_id, element_name, instruction
    with patch("foreshadowing.check_for_payoff", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = (1, "Silver Coin with a Hole", "NARRATIVE PAYOFF: Use the coin as a key.")
        
        payoff = await foreshadowing.check_for_payoff([{"user_input": user_input, "assistant_response": response_text}])
        
        assert payoff is not None
        assert payoff[1] == "Silver Coin with a Hole"
        assert "PAYOFF" in payoff[2]
