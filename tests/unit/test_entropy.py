import pytest
import asyncio
import json
import db
import entropy_engine
import canon_checker
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_relationship_decay_anchored():
    # Setup
    db.add_character("CharA", "A", "A")
    db.add_character("CharB", "B", "B")
    chars = db.get_all_characters()
    id_a = chars[0]['id']
    id_b = chars[1]['id']
    db.update_relationship(id_a, id_b, 10, -10, 20, "Initial meeting")
    db.add_lore("The Sun", "It is yellow and bright.")

    engine = entropy_engine.EntropyEngine()
    
    chars = db.get_all_characters()
    id_a = chars[0]['id']
    id_b = chars[1]['id']
    
    # Set relationship with non-zero anchors (Best Friend style)
    # Current: 20, Anchor: 10 -> Should decay towards 10
    db.execute_db("UPDATE relationships SET trust=20, base_trust=10 WHERE char_a_id=? AND char_b_id=?", (id_a, id_b))
    
    with patch('random.random', return_value=0.99):
        await engine.run_tick(1)
        
    rels = db.get_all_relationships()
    rel = [r for r in rels if r['char_a_id'] == id_a and r['char_b_id'] == id_b][0]
    
    # Trust 20, Anchor 10, Diff 10. Decay 10% of 10 = 1. New = 19
    assert rel['trust'] == 19
    
    # Run many ticks to ensure it stops at anchor
    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Lore mutation ignored"
        with patch('random.random', return_value=0.99): # Still keep mutation chance low just in case
            for _ in range(50):
                await engine.run_tick(1)
        
    rel = db.get_all_relationships()[0]
    assert rel['trust'] == 10

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
    # Setup
    db.execute_db("DELETE FROM lore")
    db.add_lore("The Sun", "It is yellow and bright.")
    engine = entropy_engine.EntropyEngine()
    
    # Mock LLM for rumor generation
    with patch('random.random', return_value=0.01): # Force mutation
        with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "Rumor says the sun is actually a giant glowing cheese wheel."
            
            await engine.mutate_lore()
            
            lore = db.search_lore("The Sun")
            assert "cheese" in lore[0]['description']
