import pytest
import asyncio
import db
import simulation_manager
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_simulation_tick_progression():
    # Initialize world time
    db.set_story_state("world_time", "0")
    # Clear characters to prevent NPC actions from cluttering events
    db.execute_db("DELETE FROM characters")
    
    # Trigger first tick
    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"type": "Environmental", "description": "A storm happens.", "location_name": null, "impact_level": 2}'
        
        events = await simulation_manager.trigger_tick()
        assert len(events) == 1
        assert events[0]['description'] == "A storm happens."
        
        # Check DB state
        assert db.get_story_state("world_time") == "1"
        
        history = db.get_recent_sim_events()
        assert len(history) == 1
        assert history[0]['description'] == "A storm happens."

@pytest.mark.asyncio
async def test_trigger_tick_with_npcs():
    db.add_character("Actor", "D", "T")
    # Mock agency to return an action
    with patch("simulation_manager.agency.run_tick", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = [{"char_name": "Actor", "description": "did something", "location_id": 1}]
        # Mock background event
        with patch("simulation_manager.generate_background_event", new_callable=AsyncMock) as mock_env:
            mock_env.return_value = {"type": "E", "description": "D"}
            
            events = await simulation_manager.trigger_tick()
            assert len(events) == 2
            assert any("Actor" in e['description'] for e in events)

@pytest.mark.asyncio
async def test_generate_background_event_with_location():
    db.add_location("Silver City", "Rich", 0, 0, "Plain")
    
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"type": "Pol", "description": "Tax", "location_name": "Silver City"}'
        
        res = await simulation_manager.generate_background_event(1)
        assert res['location_id'] == 1

@pytest.mark.asyncio
async def test_trigger_tick_critical_error():
    # Mock db.get_story_state to crash
    with patch("db.get_story_state", side_effect=Exception("DB Dead")):
        events = await simulation_manager.trigger_tick()
        assert events == []

@pytest.mark.asyncio
async def test_generate_background_event_error():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        res = await simulation_manager.generate_background_event(1)
        assert res is None
