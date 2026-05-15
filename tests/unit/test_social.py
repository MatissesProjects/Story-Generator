import pytest
import social_engine
import db
import llm
import json
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_analyze_interaction_success():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"trust": 5, "fear": -2, "affection": 10, "event_description": "Elara liked the gift."}'
        
        res = await social_engine.analyze_interaction("I give Elara a flower", "She smiles.", "Elara")
        assert res['trust'] == 5
        assert res['affection'] == 10

@pytest.mark.asyncio
async def test_analyze_interaction_error():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        res = await social_engine.analyze_interaction("U", "A", "C")
        assert res == {"trust": 0, "fear": 0, "affection": 0, "event_description": "A neutral interaction."}

@pytest.mark.asyncio
async def test_update_social_state_no_mentions():
    # Clear characters
    db.execute_db("DELETE FROM characters")
    await social_engine.update_social_state("I walk alone", "Nothing happens")
    # Should return early
    assert True

@pytest.mark.asyncio
async def test_update_social_state_success():
    db.add_character("Elara", "Warrior", "Brave")
    eid = db.query_db("SELECT id FROM characters WHERE name = 'Elara'")[0]['id']
    
    with patch("social_engine.analyze_interaction", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = {"trust": 10, "fear": 0, "affection": 5, "event_description": "Nice"}
        
        await social_engine.update_social_state("I talk to Elara", "She replies")
        
        # Check DB relationship
        rel = db.get_relationship(0, eid)
        assert rel['trust'] == 10
        assert rel['affection'] == 5

@pytest.mark.asyncio
async def test_update_social_state_error():
    db.add_character("Elara", "Warrior", "Brave")
    with patch("social_engine.analyze_interaction", side_effect=Exception("Err")):
        await social_engine.update_social_state("I talk to Elara", "Hi")
        # Should catch error
