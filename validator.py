import llm
import config
import json
import utils

async def validate_action(user_input, context_facts, inventory=None, stats=None):
    """
    Validates if the user's action is logically possible within the story's world context.
    Returns (is_valid, reason)
    """
    facts_text = "\n".join(context_facts)
    inv_text = ", ".join([f"{i['item_name']} (x{i['quantity']})" for i in inventory]) if inventory else "Empty"
    stats_text = ", ".join([f"{s['stat_name']}: {s['stat_value']}" for s in stats]) if stats else "None"

    prompt = f"""
[SYSTEM: You are the Logic Gatekeeper. Analyze the player's intended action against the known world lore and player state. 
Is this action logically possible? 

PLAYER ACTION:
"{user_input}"

KNOWN WORLD LORE:
{facts_text}

PLAYER INVENTORY:
{inv_text}

PLAYER STATS:
{stats_text}

Instructions:
1. If the action is possible, reply with JSON: {{"is_valid": true, "reason": ""}}
2. If the action is impossible (e.g. using an item they don't have, teleporting without magic), reply with JSON: {{"is_valid": false, "reason": "Short explanation of why"}}

REPLY ONLY IN JSON.]
"""

    # We want a non-streaming, fast response
    response_text = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        
    result = utils.safe_parse_json(response_text)
    if result:
        # We use .get(..., False) for Fail-Closed if the key is missing
        return result.get("is_valid", False), result.get("reason", "Logic check failed.")
    
    print(f"Validator Error: Failed to parse LLM response. Raw output: {response_text}")
    return False, "The logic of that action is unclear to the engine. Please try describing it differently."

if __name__ == "__main__":
    import asyncio
    async def test():
        print("Testing Validator...")
        is_valid, reason = await validate_action("I fly to the moon using my sandals.", ["The world has no magic."])
        print(f"Valid: {is_valid}, Reason: {reason}")
    
    asyncio.run(test())
