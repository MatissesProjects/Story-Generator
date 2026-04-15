import db
import llm
import random
import config
import json

async def perform_hidden_check(user_input, context_facts):
    """
    Uses the LLM to decide if a hidden skill check is needed and its difficulty.
    Then performs a random roll and returns the result.
    """
    facts_text = "\n".join(context_facts)
    
    prompt = f"""
[SYSTEM: You are the DiceMaster. Analyze the player's action and decide if it requires a skill check (chance of failure).

PLAYER ACTION:
"{user_input}"

RELEVANT CONTEXT:
{facts_text}

Reply ONLY with a JSON object:
{{
    "requires_check": true/false,
    "dc": 1-20 (Difficulty Class),
    "sides": 20 (Standard),
    "reason": "Short explanation of the check"
}}
]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
    
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        
        if result.get("requires_check", False):
            sides = result.get("sides", 20)
            dc = result.get("dc", 10)
            roll = random.randint(1, sides)
            return (roll >= dc), roll, dc, sides, result.get("reason", "Action performed.")
        else:
            return True, 0, 0, 0, "No check required."
            
    except Exception as e:
        print(f"DiceMaster Error: {e}. Raw: {response}")
        return True, 0, 0, 0, "Error in DiceMaster."

if __name__ == "__main__":
    import asyncio
    async def test():
        print("Testing DiceMaster...")
        success, roll, dc, sides, reason = await perform_hidden_check("I try to pick the lock on the heavy stone door.", ["The door is ancient and reinforced with iron."])
        print(f"Result: {success} (Rolled {roll} vs DC {dc}) - {reason}")

    asyncio.run(test())
