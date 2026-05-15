import pytest
import summarizer
import db
import llm
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_update_narrative_seed_success():
    # Setup history
    db.execute_db("INSERT INTO history (user_input, assistant_response) VALUES (?, ?)", ("U1", "A1"))
    
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Summary of the story"
        
        await summarizer.update_narrative_seed()
        
        # Check DB
        seed = db.get_story_state("narrative_seed")
        assert seed == "Summary of the story"

@pytest.mark.asyncio
async def test_update_narrative_seed_no_history():
    db.execute_db("DELETE FROM history")
    # Set to something else first
    db.set_story_state("narrative_seed", "Existing")
    
    await summarizer.update_narrative_seed()
    
    # Should not have changed because it returns early
    assert db.get_story_state("narrative_seed") == "Existing"

@pytest.mark.asyncio
async def test_update_narrative_seed_error():
    db.execute_db("INSERT INTO history (user_input, assistant_response) VALUES (?, ?)", ("U1", "A1"))
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        await summarizer.update_narrative_seed()
        # Should catch error and not crash
