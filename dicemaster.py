import random
import llm
import json

def roll_dice(sides=20):
    return random.randint(1, sides)

async def determine_dc(action, context_facts):
    """
    Uses the LLM to set a Difficulty Class (DC) and decide which dice to use.
    """
    facts_str = "\n".join([f"- {f}" for f in context_facts])
    
    prompt = f"""
[SYSTEM: You are the Game Master. Determine the Difficulty Class (DC) and the most appropriate Dice Type for the following player action.

CONTEXT:
{facts_str}

PLAYER ACTION:
"{action}"

DICE TYPES:
- 4: Quick, low-stakes tests (Quick reflexes, minor recall)
- 6: Standard simple tasks
- 10: Significant effort or specialized skill
- 20: Major life-or-death moments, complex social maneuvers, or legendary feats

DC GUIDELINES:
- Range from 2 to [Dice Sides]. 
- Example: DC 15 on a D20 is Moderate. DC 3 on a D4 is Moderate.

Reply ONLY with a JSON object: {{"dc": 15, "sides": 20, "reason": "Brief explanation"}}
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
        return result.get("dc", 10), result.get("sides", 20), result.get("reason", "Default difficulty")
    except Exception as e:
        print(f"DiceMaster Error (determine_dc): {e}. Raw: {response}")
        return 10, 20, "Standard difficulty"

async def perform_hidden_check(action, context_facts):
    """
    Executes a full hidden roll against a procedurally determined DC and dice type.
    Returns (success, roll, dc, sides, reason)
    """
    dc, sides, reason = await determine_dc(action, context_facts)
    roll = roll_dice(sides)
    success = roll >= dc
    
    return success, roll, dc, sides, reason

if __name__ == "__main__":
    # Test
    print("Testing DiceMaster...")
    ctx = ["LORE: The castle guards are highly trained and wearing heavy armor."]
    act = "I try to sneak past the guards through the main gate."
    success, roll, dc, reason = perform_hidden_check(act, ctx)
    print(f"Action: {act}")
    print(f"Reasoning: {reason}")
    print(f"Result: {'SUCCESS' if success else 'FAILURE'} (Roll: {roll} vs DC: {dc})")
