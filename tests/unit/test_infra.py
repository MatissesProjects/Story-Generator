import pytest
import db
import llm
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_database_isolation():
    """Verify that each test gets a fresh, isolated database."""
    # Add something to the DB
    db.add_plot_thread("Initial Thread")
    threads = db.get_active_plot_threads()
    assert len(threads) == 1
    assert threads[0]['description'] == "Initial Thread"

@pytest.mark.asyncio
async def test_database_isolation_again():
    """Verify that this test starts with an empty database (isolation)."""
    threads = db.get_active_plot_threads()
    # Should be 0 if isolation works
    assert len(threads) == 0

@pytest.mark.asyncio
async def test_llm_mocking(mock_llm):
    """Verify that LLM mocking works correctly."""
    response = await llm.async_generate_full_response("Hello")
    assert response == "Mocked response"
    mock_llm['full'].assert_called_once()

    # Test streaming
    collected = ""
    async for chunk in llm.async_generate_story_segment("Hello"):
        collected += chunk
    assert collected == "Mocked response"
    mock_llm['stream'].assert_called_once()
