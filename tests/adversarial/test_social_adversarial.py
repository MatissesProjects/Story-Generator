import pytest
import db
import social_engine
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_substring_collision_bug(mock_llm):
    """
    ADVERSARIAL: Verify if 'Al' is incorrectly updated when 'Alice' is mentioned.
    This is a known risk in the current substring-based detection.
    """
    # 1. Setup characters with colliding names
    db.add_character("Al", "A short name", "Quiet")
    db.add_character("Alice", "A longer name", "Talkative")
    
    # 2. Trigger an interaction that ONLY mentions Alice
    user_input = "I talk to Alice."
    response_text = "Alice smiles and says hello."
    
    # Mock LLM to return valid JSON
    mock_llm['full'].return_value = '{"trust": 1, "fear": 0, "affection": 1, "description": "Alice is happy"}'
    
    # We expect the LLM to be called for the social analysis
    # If the bug exists, it will identify BOTH Al and Alice because 'Al' is in 'Alice'
    await social_engine.update_social_state(user_input, response_text)
    
    # 3. Check relationships
    # Alice should have an interaction logged
    alice_rels = db.get_character_relationships(2) # Alice is ID 2
    assert any(r['other_name'] == 'Player' for r in alice_rels)
    
    # Al should NOT have an interaction logged
    al_rels = db.get_character_relationships(1) # Al is ID 1
    # If this fails, it means Al was incorrectly caught in the substring match
    player_rel_with_al = next((r for r in al_rels if r['other_name'] == 'Player'), None)
    
    # In the current buggy state, this might fail (meaning Al WAS updated)
    assert player_rel_with_al is None or (player_rel_with_al['trust'] == 0 and player_rel_with_al['fear'] == 0), \
        "BUG CONFIRMED: 'Al' was updated even though only 'Alice' was mentioned!"

@pytest.mark.asyncio
async def test_multi_character_betrayal(mock_llm):
    """
    ADVERSARIAL: Verify handling of complex multi-character interactions.
    """
    db.add_character("Elara", "A healer", "Kind")
    db.add_character("Borin", "A rogue", "Shifty")
    
    # Context: Helping Elara but also plotting with Borin
    user_input = "I give Elara the herbs, but I wink at Borin so he knows where the stash is."
    response_text = "Elara thanks you profusely. Borin watches from the shadows, nodding slowly."
    
    # Mock LLM to return different scores for each character
    # Since social_engine calls analyze_interaction in parallel, we need to handle multiple calls
    mock_llm['full'].side_effect = [
        '{"trust": 5, "fear": 0, "affection": 3, "description": "Gave herbs to Elara"}', # For Elara
        '{"trust": 2, "fear": 0, "affection": 2, "description": "Shared secret with Borin"}'  # For Borin
    ]
    
    await social_engine.update_social_state(user_input, response_text)
    
    # Verify both were updated
    elara_rel = db.get_relationship(0, 1) # Player to Elara
    borin_rel = db.get_relationship(0, 2) # Player to Borin
    
    assert elara_rel['trust'] == 5
    assert borin_rel['trust'] == 2
