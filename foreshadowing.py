import db
import llm
import json

def extract_seeds(assistant_response, current_location="Unknown"):
    """
    Analyzes the AI response for minor, interesting details that could be foreshadowing seeds.
    """
    prompt = f"""
[SYSTEM: You are the Foreshadowing Architect. Analyze the following story segment and identify 1-2 minor, unresolved details or mysterious elements that could be "seeds" for future payoffs. 

STORY SEGMENT:
"{assistant_response}"

LOCATION: {current_location}

EXAMPLES of seeds:
- A strange silver coin with a hole in it.
- A character mentioning a distant relative who disappeared.
- A weird clicking sound coming from behind a wall.
- A specific, unusual flower blooming out of season.

Reply ONLY with a JSON object:
{{
    "seeds": [
        {{
            "name": "Strange Silver Coin",
            "impact": "Could be a key to a specific vault or a mark of a secret society."
        }}
    ]
}}

If no good seeds are found, return an empty list.
REPLY ONLY IN JSON.]
"""
    response = ""
    for chunk in llm.generate_story_segment(prompt, model=config.FAST_MODEL):
        response += chunk
        
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        seeds = result.get("seeds", [])
        
        for s in seeds:
            db.add_foreshadowed_element(s['name'], current_location, s['impact'])
            print(f"Foreshadowing: Planted seed '{s['name']}'")
            
    except Exception as e:
        print(f"Foreshadowing Error (extract_seeds): {e}. Raw: {response}")

def check_for_payoff(recent_history):
    """
    Determines if it's a good time to pay off an existing seed.
    Returns (id, element_name, instruction) or None.
    """
    pending = db.get_pending_foreshadowing()
    if not pending:
        return None
        
    # We don't want to pay off seeds too often. 
    # Let's say 10% chance every turn if there are pending seeds.
    import random
    if random.random() > 0.1:
        return None
        
    seed = random.choice(pending)
    
    instruction = f"FORESHADOWING PAYOFF: Re-introduce the '{seed['element_name']}' which was first seen in '{seed['discovery_location']}'. Potential impact: {seed['potential_impact']}. Weave it into the current scene organically."
    
    return seed['id'], seed['element_name'], instruction

if __name__ == "__main__":
    # Test
    print("Testing Foreshadowing Engine...")
    extract_seeds("As you walk through the marketplace, an old man drops a strange silver coin with a hole in it. He doesn't notice and keeps walking.", "The Marketplace")
