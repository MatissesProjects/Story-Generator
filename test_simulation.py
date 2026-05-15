import pytest
import asyncio
import db
import simulation_manager
from unittest.mock import AsyncMock, patch

@pytest.fixture(autouse=True)
def setup_test_db():
    import uuid
    import os
    old_path = db.DB_PATH
    test_db = f"test_sim_{uuid.uuid4()}.db"
    
    db.close_db()
    db.DB_PATH = test_db
    db.init_db()
    
    # Initialize world time
    db.set_story_state("world_time", "0")
    
    yield
    
    db.close_db()
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except:
            pass
    db.DB_PATH = old_path
    db.close_db()

@pytest.mark.asyncio
async def test_simulation_tick_progression():
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
async def test_simulation_event_injection():
    # Add a simulation event manually
    db.execute_db(
        "INSERT INTO simulation_history (tick_number, event_type, description) VALUES (?, ?, ?)",
        (10, "Political", "A new king was crowned.")
    )
    
    import curator
    with patch('memory_engine.search_semantic_with_scores', return_value=[]):
        facts = curator.get_relevant_context("Who is the king?")
        assert any("WORLD EVENT (Tick 10): A new king was crowned." in f for f in facts)
