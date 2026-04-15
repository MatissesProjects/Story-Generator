import pytest
import asyncio
import json
import db
import entropy_engine
import canon_checker
from unittest.mock import AsyncMock, patch

@pytest.fixture(autouse=True)
def setup_test_db():
    import uuid
    import os
    old_path = db.DB_PATH
    test_db = f"test_entropy_{uuid.uuid4()}.db"
    db.DB_PATH = test_db
    db.init_db()
    
    # Add test characters and relationships
    db.add_character("CharA", "A", "A")
    db.add_character("CharB", "B", "B")
    chars = db.get_all_characters()
    id_a = chars[0]['id']
    id_b = chars[1]['id']
    
    # Set relationship to positive values
    db.update_relationship(id_a, id_b, 10, -10, 20, "Initial meeting")
    
    # Add lore
    db.add_lore("The Sun", "It is yellow and bright.")
    
    yield
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except:
            pass
    db.DB_PATH = old_path

@pytest.mark.asyncio
async def test_relationship_decay():
    engine = entropy_engine.EntropyEngine()
    
    # Run tick, which triggers decay
    with patch('random.random', return_value=0.99): # Prevent lore mutation
        await engine.run_tick(1)
        
    rels = db.get_all_relationships()
    assert len(rels) == 1
    rel = rels[0]
    
    # Initial was 10, -10, 20. Decay rate is 0.1
    # 10 decays by max(1, 1) -> 9
    # -10 decays by max(1, 1) -> -9
    # 20 decays by max(1, 2) -> 18
    assert rel['trust'] == 9
    assert rel['fear'] == -9
    assert rel['affection'] == 18

@pytest.mark.asyncio
async def test_canon_lore_duel_retcon():
    # Mock LLM to return a Retcon
    mock_resp = json.dumps({
        "resolution_type": "Retcon",
        "explanation": "The sun is actually blue.",
        "new_lore": "The sun is a giant blue sapphire."
    })
    
    contradiction = {
        "claim": "The sun is blue.",
        "violation": "The sun was yellow."
    }
    
    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_resp
        
        result = await canon_checker.resolve_contradiction(contradiction, ["The sun is yellow."])
        assert result['resolution_type'] == "Retcon"
        
        # Check if new lore was added
        lore = db.search_lore("Resolved Canon Shift")
        assert len(lore) > 0
        assert "sapphire" in lore[0]['description']

@pytest.mark.asyncio
async def test_lore_volatility():
    engine = entropy_engine.EntropyEngine()
    
    # Mock LLM for rumor generation
    with patch('random.random', return_value=0.01): # Force mutation
        with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "Rumor says the sun is actually a giant glowing cheese wheel."
            
            await engine.mutate_lore()
            
            lore = db.search_lore("The Sun")
            assert "cheese" in lore[0]['description']
