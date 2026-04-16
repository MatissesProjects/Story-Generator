import pytest
import db
import validator

@pytest.mark.asyncio
async def test_inventory_depletion_hallucination_risk(mock_llm):
    """
    ADVERSARIAL: Verify that the validator currently depends on LLM honesty.
    If the LLM hallucinates that a player HAS an item, the engine allows it.
    """
    # 1. Player has NO gold
    inventory = []
    
    # 2. Player tries to buy a legendary sword
    user_input = "I buy the Dragon Slayer sword for 500 gold."
    context_facts = ["The shopkeeper sells the Dragon Slayer for 500 gold."]
    
    # Mock LLM to INCORRECTLY validate (simulating a hallucination)
    mock_llm['full'].return_value = '{"is_valid": true, "reason": "The shopkeeper is happy to sell it."}'
    
    is_valid, reason = await validator.validate_action(user_input, context_facts, inventory=inventory)
    
    # This currently returns True, which is a known dependency on LLM performance.
    # We want to acknowledge this as a "Soft Spot" rather than a hard bug for now.
    assert is_valid is True

@pytest.mark.asyncio
async def test_validator_fail_closed_verified(mock_llm):
    """
    ADVERSARIAL: Verify that the validator 'fails-closed' (returns False) on garbage LLM output.
    """
    # 1. Mock LLM to return absolute garbage
    mock_llm['full'].return_value = "I am a teapot and cannot return JSON."
    
    user_input = "I do something impossible."
    
    is_valid, reason = await validator.validate_action(user_input, ["Lore"])
    
    # Verify it now fails-closed
    assert is_valid is False
    assert "clear" in reason.lower()
