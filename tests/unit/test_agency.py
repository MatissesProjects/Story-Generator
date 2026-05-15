import pytest
import asyncio
import db
import agency_engine
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_agency_tick_social_priority():
    # Setup character
    db.add_character("TestNPC", "A loner", "Quiet")
    db.execute_db("UPDATE characters SET social = 10 WHERE name = 'TestNPC'")
    
    engine = agency_engine.AgencyEngine()
    
    # Mock LLM for the action description
    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "TestNPC chatted with a passerby."
        
        actions = await engine.run_tick(1)
        
        assert len(actions) == 1
        assert actions[0]['char_name'] == "TestNPC"
        # Should prioritize Socialize because social was set to 10
        assert actions[0]['action'] == "Socialize"
        
        # Check DB update
        char = db.get_all_characters()[0]
        assert char['social'] > 10 # Recovery happened
        assert char['current_goal'] == "Socialize"

@pytest.mark.asyncio
async def test_agency_idle_logic():
    db.add_character("Idler", "D", "T")
    db.execute_db("UPDATE characters SET social=90, ambition=90, safety=90, resources=90")
    engine = agency_engine.AgencyEngine()
    with patch('random.random', return_value=0.5):
        actions = await engine.run_tick(1)
        assert actions[0]['action'] == "Idle"

@pytest.mark.asyncio
async def test_agency_travel_logic():
    db.add_character("Traveler", "D", "T")
    db.add_location("Start", "S", 0, 0, "Plains")
    db.add_location("Dest", "D", 1, 1, "Plains")
    
    # Set destination
    db.execute_db("INSERT INTO entity_positions (entity_type, entity_id, current_location_id, destination_id) VALUES ('character', 1, 1, 2)")
    
    engine = agency_engine.AgencyEngine()
    actions = await engine.run_tick(1)
    
    assert actions[0]['action'] == "Travel"
    # Should have arrived
    pos = db.get_entity_position("character", 1)
    assert pos['current_location_id'] == 2
    assert pos['destination_id'] is None

@pytest.mark.asyncio
async def test_agency_move_logic():
    db.add_character("Mover", "D", "T")
    db.add_location("L1", "D1", 0, 0, "Forest")
    db.add_location("L2", "D2", 1, 1, "Forest")
    db.execute_db("INSERT INTO entity_positions (entity_type, entity_id, current_location_id) VALUES ('character', 1, 1)")
    # Set needs high to trigger boredom (Move/Idle)
    db.execute_db("UPDATE characters SET social=90, ambition=90, safety=90, resources=90")

    engine = agency_engine.AgencyEngine()
    # Mock random to force Move
    with patch('random.random', return_value=0.1): 
        actions = await engine.run_tick(1)
        assert actions[0]['action'] == "Move"
        
    pos = db.get_entity_position("character", 1)
    assert pos['destination_id'] == 2

@pytest.mark.asyncio
async def test_agency_socialize_logic():
    db.add_character("Char1", "D", "T")
    db.add_character("Char2", "D", "T")
    db.add_location("L1", "D", 0, 0, "P")
    db.execute_db("INSERT INTO entity_positions (entity_type, entity_id, current_location_id) VALUES ('character', 1, 1)")
    db.execute_db("INSERT INTO entity_positions (entity_type, entity_id, current_location_id) VALUES ('character', 2, 1)")
    # Force socialize
    db.execute_db("UPDATE characters SET social = 0 WHERE id = 1")
    
    engine = agency_engine.AgencyEngine()
    actions = await engine.run_tick(1)
    
    # actions[0] should be Char1 socializing
    assert actions[0]['action'] == "Socialize"
    assert "talking" in actions[0]['description']

@pytest.mark.asyncio
async def test_agency_move_single_location():
    db.add_character("Mover", "D", "T")
    db.add_location("Only", "D", 0, 0, "P")
    db.execute_db("INSERT INTO entity_positions (entity_type, entity_id, current_location_id) VALUES ('character', 1, 1)")
    db.execute_db("UPDATE characters SET social=90, ambition=90, safety=90, resources=90")
    
    engine = agency_engine.AgencyEngine()
    with patch('random.random', return_value=0.1): 
        actions = await engine.run_tick(1)
        # Should say "stayed put"
        assert "stayed put" in actions[0]['description']

@pytest.mark.asyncio
async def test_agency_process_npc_action_error():
    db.add_character("Worker", "D", "T")
    db.execute_db("UPDATE characters SET ambition = 10")
    
    engine = agency_engine.AgencyEngine()
    with patch('llm.async_generate_full_response', side_effect=Exception("Err")):
        actions = await engine.run_tick(1)
        assert "focused on" in actions[0]['description']
