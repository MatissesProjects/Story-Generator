import pytest
import sqlite3
import os
import db
import asyncio
from unittest.mock import AsyncMock, patch

@pytest.fixture(autouse=True, scope="function")
def test_db(tmp_path):
    """
    Creates a temporary database for each test and points db.DB_PATH to it.
    """
    test_db_path = tmp_path / "test_story_memory.db"
    
    # Store original path
    original_db_path = db.DB_PATH
    db.DB_PATH = str(test_db_path)
    
    # Initialize the test database with schema
    db.init_db()
    
    yield db.DB_PATH
    
    # Clean up and restore
    db.DB_PATH = original_db_path
    if test_db_path.exists():
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass

@pytest.fixture
def mock_llm():
    """
    Fixture to mock LLM responses.
    """
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_full, \
         patch("llm.async_generate_story_segment") as mock_stream:
        
        # Setup mock_stream as an async generator
        async def mock_stream_gen(*args, **kwargs):
            yield "Mocked "
            yield "response"
        
        mock_stream.side_effect = mock_stream_gen
        mock_full.return_value = "Mocked response"
        
        yield {"full": mock_full, "stream": mock_stream}

@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest-asyncio's event_loop fixture to ensure it stays open for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
