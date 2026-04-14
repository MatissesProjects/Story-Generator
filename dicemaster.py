import random
import llm
import json

def roll_d20():
    return random.randint(1, 20)

def determine_dc(action, context_facts):
    """
    Uses the LLM to set a Difficulty Class (DC) for an action.
    """
    facts_str = "\n".join([f"- {f}" for f in context_facts])
    
    prompt = f"""
[SYSTEM: You are the Game Master. Determine the Difficulty Class (DC) for the following player action based on the established lore and context.

CONTEXT:
{facts_str}

PLAYER ACTION:
"{action}"

DC GUIDELINES:
- 5: Very Easy (Walking a tightrope, basic recall)
- 10: Easy (Opening a locked wooden door)
- 15: Moderate (Sneaking past alert guards)
- 20: Hard (Convincing a king to give up his crown)
- 25: Very Hard (Casting a spell in an anti-magic field)

Reply ONLY with a JSON object: {{"dc": 15, "reason": "Brief explanation of difficulty"}}
]
"""
    response = ""
    for chunk in llm.generate_story_segment(prompt):
        response += chunk
        
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        return result.get("dc", 10), result.get("reason", "Default difficulty")
    except Exception as e:
        print(f"DiceMaster Error (determine_dc): {e}. Raw: {response}")
        return 10, "Standard difficulty"

def perform_hidden_check(action, context_facts):
    """
    Executes a full hidden roll against a procedurally determined DC.
    Returns (success, roll, dc, reason)
    """
    dc, reason = determine_dc(action, context_facts)
    roll = roll_d20()
    success = roll >= dc
    
    return success, roll, dc, reason

if __name__ == "__main__":
    # Test
    print("Testing DiceMaster...")
    ctx = ["LORE: The castle guards are highly trained and wearing heavy armor."]
    act = "I try to sneak past the guards through the main gate."
    success, roll, dc, reason = perform_hidden_check(act, ctx)
    print(f"Action: {act}")
    print(f"Reasoning: {reason}")
    print(f"Result: {'SUCCESS' if success else 'FAILURE'} (Roll: {roll} vs DC: {dc})")
