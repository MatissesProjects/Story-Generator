import db
import llm
import json
import asyncio
import config
import utils
import vision
import director
import parser


async def analyze_interaction(user_input, response_text, character_name):
    """
    Uses the LLM to analyze the social impact of an interaction with a specific character.
    Returns delta_trust, delta_fear, delta_affection, and event_description.
    """
    prompt = f"""
[SYSTEM: You are the Social Dynamics Engine. Analyze the following interaction between the Player and {character_name}.
Determine the impact on their relationship based on the player's actions and the character's reaction.

PLAYER INPUT: "{user_input}"
CHARACTER REACTION: "{response_text}"

Reply ONLY with a JSON object.
EXAMPLE STRUCTURE (Do not use these specific values):
{{
    "trust": 5, 
    "fear": -2, 
    "affection": 10,
    "event_description": "The player was kind and respectful, strengthening the bond."
}}

REPLY ONLY IN JSON.]
"""
    try:
        response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        result = utils.safe_parse_json(response, default={})
        return {
            "trust": result.get("trust", 0),
            "fear": result.get("fear", 0),
            "affection": result.get("affection", 0),
            "event_description": result.get("event_description", "A neutral interaction.")
        }
    except Exception as e:
        print(f"Social Engine Error (analyze_interaction): {e}")
        return {"trust": 0, "fear": 0, "affection": 0, "event_description": "A neutral interaction."}


async def update_social_state(user_input, response_text):
    """
    Scans the interaction for character mentions and updates relationships.
    """
    try:
        all_chars = db.get_all_characters()
        char_names = [c['name'] for c in all_chars]
        
        # Identify who was involved
        characters_involved = utils.extract_character_mentions(user_input + " " + response_text, char_names)
        
        if not characters_involved:
            return
            
        print(f"Social Engine: Characters detected: {characters_involved}")
        
        for name in characters_involved:
            impact = await analyze_interaction(user_input, response_text, name)
            
            char_data = db.search_characters(name)[0]
            db.update_relationship(
                0, char_data['id'], 
                impact['trust'], impact['fear'], impact['affection'], 
                impact['event_description']
            )
            print(f"Social Engine: Updated relationship with {name}: {impact['event_description']}")
            
    except Exception as e:
        print(f"Social Engine Error (update_social_state): {e}")

if __name__ == "__main__":
    # Test
    import asyncio
    async def test():
        print("Testing Social Engine...")
        db.init_db()
        db.add_character("Elara", "A kind healer", "Empathetic, Observant")
        await update_social_state("I give Elara a rare medicinal herb I found.", "Elara smiles warmly. 'This will save many lives, thank you.'")
    
    asyncio.run(test())
