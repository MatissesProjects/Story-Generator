import llm
import config
import json

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
        
    try:
        # Attempt to parse the JSON from the LLM output
        clean_json = response_text.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        return result.get("is_valid", True), result.get("reason", "")
    except Exception as e:
        print(f"Validator Error: {e}. Raw output: {response_text}")
        return True, "" # Fail-safe: allow the action if parsing fails

if __name__ == "__main__":
    import asyncio
    async def test():
        print("Testing Validator...")
        is_valid, reason = await validate_action("I fly to the moon using my sandals.", ["The world has no magic."])
        print(f"Valid: {is_valid}, Reason: {reason}")
    
    asyncio.run(test())
