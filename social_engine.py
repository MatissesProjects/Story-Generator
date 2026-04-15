import db
import llm
import json

def analyze_interaction(user_input, response_text, character_name):
    """
    Uses the LLM to analyze the social impact of an interaction on a specific character.
    Returns (delta_trust, delta_fear, delta_affection, event_description)
    """
    prompt = f"""
[SYSTEM: You are the Social Analyst. Analyze the following interaction between the Player and {character_name}.
Determine how this interaction affects {character_name}'s view of the player.

PLAYER ACTION/DIALOGUE:
"{user_input}"

STORY RESPONSE:
"{response_text}"

SCORING RULES:
- Trust: Does the player seem reliable, honest, or helpful? (-5 to +5)
- Fear: Does the player seem dangerous, powerful, or threatening? (-5 to +5)
- Affection: Does the player seem kind, likable, or charming? (-5 to +5)

Reply ONLY with a JSON object:
{{
    "trust": 2,
    "fear": 0,
    "affection": 1,
    "description": "Short summary of why the scores changed"
}}
]
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
        return (
            result.get("trust", 0), 
            result.get("fear", 0), 
            result.get("affection", 0), 
            result.get("description", "Interaction analyzed.")
        )
    except Exception as e:
        print(f"SocialEngine Error (analyze_interaction): {e}. Raw: {response}")
        return 0, 0, 0, "Analysis failed."

def update_social_state(user_input, response_text):
    """
    Identifies involved characters and updates their relationships with the player.
    """
    all_entities = db.get_all_entities()
    # Simple check: if a character name is in the response, analyze them
    for entity in all_entities:
        if entity.lower() in response_text.lower() or entity.lower() in user_input.lower():
            # Get character ID
            char_results = db.search_characters(entity)
            if char_results:
                char = char_results[0]
                char_id = char['id']
                
                dt, df, da, desc = analyze_interaction(user_input, response_text, entity)
                if dt != 0 or df != 0 or da != 0:
                    db.update_relationship(0, char_id, dt, df, da, desc)
                    print(f"Social: Updated relationship with {entity}. Trust: {dt}, Fear: {df}, Affection: {da}")

if __name__ == "__main__":
    # Test
    print("Testing Social Engine...")
    db.init_db()
    db.add_character("Elara", "A kind healer", "Empathetic, Observant")
    update_social_state("I give Elara a rare medicinal herb I found.", "Elara smiles warmly. 'This will save many lives, thank you.'")
