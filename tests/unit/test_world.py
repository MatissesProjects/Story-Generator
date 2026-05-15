import pytest
import world_engine
import db
import llm
import json
import random
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_resolve_new_location_success():
    we = world_engine.WorldEngine()
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"biome": "Forest", "elevation": 100, "climate": "Humid"}'
        
        loc_id = await we.resolve_new_location("Dark Woods", "Spooky")
        assert loc_id > 0
        
        loc = db.get_location(loc_id)
        assert loc['name'] == "Dark Woods"
        assert loc['biome_type'] == "Forest"

@pytest.mark.asyncio
async def test_resolve_new_location_existing():
    we = world_engine.WorldEngine()
    db.add_location("Existing", "D", 0, 0, "P")
    
    loc_id = await we.resolve_new_location("Existing", "D")
    assert loc_id == 1
    # Check player position updated
    pos = db.get_entity_position("player", 0)
    assert pos['current_location_id'] == 1

@pytest.mark.asyncio
async def test_resolve_new_location_relative():
    we = world_engine.WorldEngine()
    db.add_location("Center", "D", 0, 0, "P")
    
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"biome": "P", "elevation": 0, "climate": "T"}'
        
        loc_id = await we.resolve_new_location("North Loc", "D", relative_to_name="Center", direction="north")
        loc = db.get_location(loc_id)
        assert loc['y'] == we.grid_size

@pytest.mark.asyncio
async def test_resolve_new_location_collision_retry():
    we = world_engine.WorldEngine()
    db.add_location("Blocker", "D", 0, 0, "P")
    
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm, \
         patch("random.randint") as mock_rand:
         
        mock_llm.return_value = '{}'
        # First attempt (0,0) -> collision. Second attempt (5,5) -> success.
        mock_rand.side_effect = [0, 0, 0, 0, 5, 5]
        
        loc_id = await we.resolve_new_location("New", "D")
        loc = db.get_location(loc_id)
        assert loc['x'] == 5
        assert loc['y'] == 5

def test_move_entity():
    we = world_engine.WorldEngine()
    db.add_location("Target", "D", 0, 0, "P")
    
    res = we.move_entity("character", 1, "Target")
    assert res is True
    pos = db.get_entity_position("character", 1)
    assert pos['current_location_id'] == 1
    
    res_fail = we.move_entity("character", 1, "Nonexistent")
    assert res_fail is False

@pytest.mark.asyncio
async def test_move_entity_error():
    we = world_engine.WorldEngine()
    with patch("db.get_location_by_name", side_effect=Exception("Err")):
        res = we.move_entity("player", 0, "Any")
        assert res is False

@pytest.mark.asyncio
async def test_errors():
    we = world_engine.WorldEngine()
    # If property detection fails, it should still succeed in adding location with defaults
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        res = await we.resolve_new_location("E", "D")
        assert res is not None
        
        props = await we.detect_physical_properties("E", "D", 0)
        assert props['biome'] == "Plain"

@pytest.mark.asyncio
async def test_resolve_new_location_critical_error():
    we = world_engine.WorldEngine()
    # Mock db.get_location_by_name to crash everything
    with patch("db.get_location_by_name", side_effect=Exception("DB Down")):
        # This will hit the 'Final fallback' in resolve_new_location
        res = await we.resolve_new_location("Critical", "D")
        assert res is not None
