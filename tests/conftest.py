import pytest
import sqlite3
import os
import db
import memory_engine
import config
import asyncio
from unittest.mock import AsyncMock, patch

@pytest.fixture(autouse=True, scope="function")
def test_db(tmp_path):
    """
    Creates a temporary database and vector DB for each test and points paths to them.
    """
    test_db_path = tmp_path / "test_story_memory.db"
    test_vector_path = tmp_path / "test_vector_db"
    
    # Store original paths
    original_db_path = db.DB_PATH
    original_vector_path = config.VECTOR_DB_PATH
    
    # Ensure any existing connection is closed
    db.close_db()
    memory_engine.reset_memory_engine()
    
    db.DB_PATH = str(test_db_path)
    config.VECTOR_DB_PATH = str(test_vector_path)
    
    # Initialize the test database with schema
    db.init_db()
    
    yield db.DB_PATH
    
    # Clean up and restore
    db.close_db()
    memory_engine.reset_memory_engine()
    
    db.DB_PATH = original_db_path
    config.VECTOR_DB_PATH = original_vector_path
    
    if test_db_path.exists():
        try:
            os.remove(test_db_path)
        except PermissionError:
            pass
    db.close_db()

@pytest.fixture
def mock_llm():
    """
    Fixture to mock LLM responses with a smart side_effect that returns
    valid JSON based on the module requesting it.
    """
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_full, \
         patch("llm.async_generate_story_segment") as mock_stream:
        
        async def mock_full_response(prompt, **kwargs):
            # Check if return_value was manually overridden from the default
            # Note: mock_full.return_value is an AsyncMock object by default
            if not isinstance(mock_full.return_value, AsyncMock):
                return mock_full.return_value

            p = prompt.lower()
            if "logic gatekeeper" in p or "is this action logically possible" in p:
                return '{"is_valid": true, "reason": "Action is possible."}'
            if "narrative architect" in p or "needs_research" in p:
                return '{"needs_research": false, "suggested_theme": ""}'
            if "quest arbiter" in p:
                return '{"updates": []}'
            if "milestone arbiter" in p:
                return '{"completed": false}'
            if "scene parser" in p or '"location":' in p:
                return '{"location": null, "description": null, "relative_to": null, "direction": null}'
            if "social layer engine" in p:
                return '{"trust": 1, "fear": 0, "affection": 1, "description": "Interaction analyzed"}'
            if "foreshadowing architect" in p:
                return '{"seeds": []}'
            if "narrative weaver" in p or "pending seeds" in p:
                return '{"selected_seed_id": null, "reasoning": "None", "action_type": "none"}'
            if "physical world architect" in p:
                return '{"biome": "Plain", "elevation": 0, "climate": "Temperate", "connectivity_score": 0.5}'
            if "canon consistency" in p or "contradictions" in p:
                return '{"contradictions": []}'
            if "character architect" in p:
                return '{"description": "A newly discovered figure.", "traits": "Mysterious, Unknown", "voice_id": "en_US-amy-medium.onnx"}'
            
            # Default for creative generation or unrecognized prompts
            return "Mocked response content."

        # Setup mock_stream as an async generator
        async def mock_stream_gen(*args, **kwargs):
            yield "Mocked "
            yield "response"
        
        mock_stream.side_effect = mock_stream_gen
        mock_full.side_effect = mock_full_response
        
        yield {"full": mock_full, "stream": mock_stream}

@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest-asyncio's event_loop fixture to ensure it stays open for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
