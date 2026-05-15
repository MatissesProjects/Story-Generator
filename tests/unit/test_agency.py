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
    # Setup character
    db.add_character("TestNPC", "A loner", "Quiet")
    # Set all needs high
    db.execute_db("UPDATE characters SET social=90, ambition=90, safety=90, resources=90")
    
    engine = agency_engine.AgencyEngine()
    
    # Mock random.random to return 0.5 (above the 0.3 threshold for Move)
    with patch('random.random', return_value=0.5):
        actions = await engine.run_tick(2)
        assert actions[0]['action'] == "Idle"
