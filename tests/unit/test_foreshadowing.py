import pytest
import foreshadowing
import db
import llm
import json
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_extract_seeds_success():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"seeds": [{"name": "Rusty Key", "impact": "Opens a door", "category": "Item"}]}'
        
        await foreshadowing.extract_seeds("AI response", "Tavern")
        
        # Check DB
        seeds = db.get_pending_foreshadowing()
        assert len(seeds) == 1
        assert seeds[0]['element_name'] == "Rusty Key"
        assert seeds[0]['discovery_location'] == "Tavern"

@pytest.mark.asyncio
async def test_extract_seeds_error():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        await foreshadowing.extract_seeds("Text")
        # Should catch error and return

@pytest.mark.asyncio
async def test_evaluate_context_for_payoff_triggered():
    # Setup a seed
    db.add_foreshadowed_element("Rusty Key", "Tavern", "Opens vault")
    
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        # We need the correct ID from DB
        seeds = db.get_pending_foreshadowing()
        sid = seeds[0]['id']
        
        mock_llm.return_value = json.dumps({
            "selected_seed_id": sid, 
            "reasoning": "Fits well", 
            "action_type": "payoff"
        })
        
        res = await foreshadowing.evaluate_context_for_payoff("You find a vault.")
        assert res[0] == sid
        assert res[1] == "Rusty Key"
        assert "NARRATIVE PAYOFF" in res[2]

@pytest.mark.asyncio
async def test_evaluate_context_for_payoff_none():
    db.execute_db("DELETE FROM foreshadowed_elements")
    res = await foreshadowing.evaluate_context_for_payoff("Text")
    assert res is None

@pytest.mark.asyncio
async def test_check_for_payoff_wrapper():
    # Setup history
    history = [{"user_input": "U", "assistant_response": "A"}]
    
    with patch("foreshadowing.evaluate_context_for_payoff", new_callable=AsyncMock) as mock_eval:
        mock_llm_res = (1, "Name", "Instruction")
        mock_eval.return_value = mock_llm_res
        
        res = await foreshadowing.check_for_payoff(history)
        assert res == mock_llm_res
        mock_eval.assert_called_once()

@pytest.mark.asyncio
async def test_check_for_payoff_empty():
    res = await foreshadowing.check_for_payoff([])
    assert res is None

@pytest.mark.asyncio
async def test_evaluate_context_for_payoff_error():
    db.add_foreshadowed_element("Key", "L", "I")
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        res = await foreshadowing.evaluate_context_for_payoff("Ctx")
        assert res is None
