import pytest
import db
import validator

@pytest.mark.asyncio
async def test_inventory_depletion_bypass(mock_llm):
    """
    ADVERSARIAL: Verify if the validator incorrectly allows using items the player doesn't have.
    """
    # 1. Player has NO gold
    inventory = []
    
    # 2. Player tries to buy a legendary sword
    user_input = "I buy the Dragon Slayer sword for 500 gold."
    context_facts = ["The shopkeeper sells the Dragon Slayer for 500 gold."]
    
    # Mock LLM to INCORRECTLY validate (simulating a hallucination or lazy check)
    mock_llm['full'].return_value = '{"is_valid": true, "reason": "The shopkeeper is happy to sell it."}'
    
    is_valid, reason = await validator.validate_action(user_input, context_facts, inventory=inventory)
    
    # If this is True, our logical consistency is compromised
    assert is_valid is False, "BUG CONFIRMED: Validator allowed purchase without gold!"

@pytest.mark.asyncio
async def test_lore_violation_bypass(mock_llm):
    """
    ADVERSARIAL: Verify if the validator allows actions that contradict established lore.
    """
    # 1. Established Lore: Magic is impossible in this dead zone.
    context_facts = ["The Dead Zone completely nullifies all magical energy. Spellcasting is impossible here."]
    
    # 2. Player tries to cast a fireball
    user_input = "I cast a massive fireball to incinerate the goblins."
    
    # Mock LLM to INCORRECTLY validate
    mock_llm['full'].return_value = '{"is_valid": true, "reason": "You are a powerful wizard."}'
    
    is_valid, reason = await validator.validate_action(user_input, context_facts)
    
    assert is_valid is False, "BUG CONFIRMED: Validator allowed magic in a dead zone!"

@pytest.mark.asyncio
async def test_validator_fail_open_audit(mock_llm):
    """
    ADVERSARIAL: Verify if the validator 'fails-open' (returns True) on garbage LLM output.
    This is a critical security/integrity risk.
    """
    # 1. Mock LLM to return absolute garbage
    mock_llm['full'].return_value = "I am a teapot and cannot return JSON."
    
    user_input = "I do something impossible."
    
    is_valid, reason = await validator.validate_action(user_input, ["Lore"])
    
    # Current behavior: returns True on exception. We want to CONFIRM this weakness.
    assert is_valid is False, "RISK CONFIRMED: Validator fails-open on malformed LLM output!"
