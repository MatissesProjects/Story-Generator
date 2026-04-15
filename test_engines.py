import pytest
import asyncio
import json
import db
import social_engine
import music_orchestrator
import world_engine
import summarizer
import llm
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.fixture(autouse=True)
def setup_test_db():
    import uuid
    import os
    old_path = db.DB_PATH
    test_db = f"test_engines_{uuid.uuid4()}.db"
    db.DB_PATH = test_db
    db.init_db()
    yield
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except:
            pass
    db.DB_PATH = old_path

@pytest.mark.asyncio
async def test_social_engine_analysis():
    # Mock LLM for social analysis
    mock_social_resp = json.dumps({
        "trust": 3,
        "fear": -1,
        "affection": 2,
        "description": "The player helped Elara."
    })
    
    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_social_resp
        
        dt, df, da, desc = await social_engine.analyze_interaction("I give her a herb", "Elara smiles.", "Elara")
        assert dt == 3
        assert da == 2
        assert desc == "The player helped Elara."

@pytest.mark.asyncio
async def test_social_engine_update():
    # Setup character
    db.add_character("Elara", "Healer", "Kind")
    
    mock_social_resp = json.dumps({
        "trust": 5, "fear": 0, "affection": 0, "description": "Gave medicine."
    })
    
    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_social_resp
        
        # This will identify Elara from the names and update her
        await social_engine.update_social_state("I give Elara medicine", "Elara is happy.")
        
        rel = db.get_relationship(0, 1) # Player (0) and first char (1)
        assert rel['trust'] == 5

@pytest.mark.asyncio
async def test_music_mood_detection():
    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Combat"
        
        orchestrator = music_orchestrator.MusicOrchestrator()
        mood = await orchestrator.detect_mood("The dragon roars and attacks!")
        assert mood == "Combat"

@pytest.mark.asyncio
async def test_world_engine_properties():
    mock_props = json.dumps({
        "biome": "Mountain",
        "elevation": 500,
        "climate": "Arctic",
        "connectivity_score": 0.3
    })
    
    we = world_engine.WorldEngine()
    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_props
        
        props = await we.detect_physical_properties("Peak of Doom", "A snowy summit", 0)
        assert props['biome'] == "Mountain"
        assert props['elevation'] == 500
        assert props['climate'] == "Arctic"

@pytest.mark.asyncio
async def test_summarizer_incremental():
    # Log some history
    db.log_history("Hello", "Hi there.")
    db.set_story_state("narrative_seed", "The beginning.")
    
    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "The story continues with a greeting."
        
        await summarizer.update_narrative_seed()
        seed = db.get_story_state("narrative_seed")
        assert seed == "The story continues with a greeting."
