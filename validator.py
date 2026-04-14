import llm
import config
import json

def validate_action(user_input, context_facts, inventory=None, stats=None):
    """
    Validates if the user's action is logically possible within the story's world context.
    Returns (is_valid, reason)
    """
    if not user_input.strip():
        return True, ""

    # Prepare a prompt for the 'Logic Validator'
    context_str = "\n".join([f"- {f}" for f in context_facts])
    
    inv_str = "None"
    if inventory:
        inv_str = ", ".join([f"{i['item_name']} (x{i['quantity']})" for i in inventory])
        
    stats_str = "None"
    if stats:
        stats_str = ", ".join([f"{s['stat_name']}: {s['stat_value']}" for s in stats])

    prompt = f"""
[SYSTEM: You are the Logic Validator for an interactive story. Your job is to ensure player actions are consistent with the established world lore, character abilities, and current inventory/stats.

WORLD CONTEXT/LORE:
{context_str}

CHARACTER INVENTORY:
{inv_str}

CHARACTER STATS:
{stats_str}

PLAYER ACTION:
"{user_input}"

RULES:
1. If the action is possible given the lore and character state, reply with JSON: {{"valid": true, "reason": ""}}
2. If the action is impossible (e.g., using an item you don't have, flying without wings, interacting with non-existent objects), reply with JSON: {{"valid": false, "reason": "A brief, immersive explanation of why it failed."}}
3. Be firm but fair. If the lore is silent, assume it's possible.

REPLY ONLY IN JSON.]
"""

    # We want a non-streaming, fast response
    response_text = ""
    for chunk in llm.generate_story_segment(prompt):
        response_text += chunk
        
    try:
        # Attempt to parse the JSON from the LLM output
        # Sometimes models wrap JSON in code blocks
        clean_json = response_text.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        return result.get("valid", True), result.get("reason", "")
    except Exception as e:
        print(f"Validator Error (parsing JSON): {e}. Raw response: {response_text}")
        # Fallback to true if validation fails to avoid blocking the story
        return True, ""

if __name__ == "__main__":
    # Test
    print("Testing Logic Validator...")
    test_context = [
        "LORE: This world has no magic. Magic is a myth.",
        "CHARACTER: Player is a normal human with no special powers."
    ]
    
    # Test impossible action
    is_valid, reason = validate_action("I cast a fireball at the guard.", test_context)
    print(f"Action: 'I cast a fireball' -> Valid: {is_valid}, Reason: {reason}")
    
    # Test possible action
    is_valid, reason = validate_action("I try to talk to the guard.", test_context)
    print(f"Action: 'I talk to the guard' -> Valid: {is_valid}, Reason: {reason}")
