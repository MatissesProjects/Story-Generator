import db
import llm
import json
import asyncio
import config
import utils
import vision
import director

async def analyze_interaction(user_input, response_text, character_name):
    """
    Uses the LLM to analyze the social impact of an interaction on a specific character.
    Returns (delta_trust, delta_fear, delta_affection, event_description)
    """
    prompt = f"""
[SYSTEM: You are the Social Layer Engine. Analyze the following interaction between the PLAYER and the character '{character_name}'.
How did the player's input and the character's reaction affect their relationship?

PLAYER INPUT:
"{user_input}"

AI RESPONSE:
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
    # We want a non-streaming, fast response
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)

    result = utils.safe_parse_json(response)
    if result:
        return (
            result.get("trust", 0), 
            result.get("fear", 0), 
            result.get("affection", 0), 
            result.get("description", "Interaction analyzed.")
        )

    print(f"SocialEngine Error (analyze_interaction): Failed to parse LLM response. Raw: {response}")
    return 0, 0, 0, "Analysis failed."


async def register_new_character(name, context_text):
    """
    Automatically adds a new character to the database with a fitting voice
    based on the story context.
    """
    # If the name is a placeholder, generate a creative one
    if name.lower() in ["stranger", "mysterious figure", "figure", "someone"]:
        print(f"Social: Discovered placeholder '{name}', generating creative name...")
        name = await director.generate_creative_name("character", context_text)
        
    print(f"Social: Discovering new character: {name}")
    
    # Use LLM to get a quick description and traits
    prompt = f"""
[SYSTEM: You are the Character Architect. A new character named '{name}' has appeared in the story.
Based on this context, provide a brief description and their likely voice type.

CONTEXT:
{context_text}

AVAILABLE VOICES:
- en_US-ryan-high (Narrator / Deep, Strong Male)
- en_US-lessac-high (Clear, Expressive Female Lead)
- en_US-joe-medium (Conversational, Upbeat Younger Male)
- en_US-amy-medium (Energetic Younger Female)
- en_GB-alan-medium (Authoritative, Mature British Male)
- en_GB-jenny_dioco-medium (Polished, Steady British Female)
- en_GB-alba-medium (Scottish Lilt / Regional Female)

Reply ONLY with JSON:
{{
    "description": "Short bio",
    "traits": "Comma separated traits",
    "voice_id": "the_filename.onnx"
}}
]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
    data = utils.safe_parse_json(response)
    
    if data:
        db.add_character(
            name, 
            data.get("description", "A mysterious figure."), 
            data.get("traits", "Unknown"),
            voice_id=data.get("voice_id", "en_US-lessac-medium.onnx")
        )
        # Trigger generation in background - do NOT await, so the story keeps streaming
        asyncio.create_task(vision.generate_portrait(name, data.get("description", ""), data.get("traits", "")))

async def discover_new_characters(response_text):
    """
    Scans the response for new character names and registers them in the DB.
    """
    known_chars = [c['name'] for c in db.get_all_characters()]
    
    # Extract potential names using capitalized words preceding colons
    import re
    potential_names = re.findall(r'\[?([A-Z][a-z]+(?: [A-Z][a-z]+)*)\]?:', response_text)
    
    for name in potential_names:
        if name.lower() not in [k.lower() for k in known_chars] and name.lower() != "narrator":
            await register_new_character(name, response_text)
            known_chars.append(name) # Prevent double registration in same turn

async def update_social_state(user_input, response_text, current_turn=0):
    """
    Identifies involved characters and updates their relationships with the player.
    Also updates the 'last_seen_turn' for these characters.
    """
    # Now proceed with standard relationship updates only
    character_names = [c['name'] for c in db.get_all_characters()]
    involved_names = utils.extract_character_mentions(user_input + " " + response_text, character_names)
    
    analysis_tasks = []
    for name in involved_names:
        # Get character ID
        char_results = db.search_characters(name)
        if char_results:
            char = char_results[0]
            char_id = char['id']
            
            # Update last seen
            db.update_character_last_seen(char_id, current_turn)
            
            # Gather analysis tasks
            analysis_tasks.append((name, char_id, analyze_interaction(user_input, response_text, name)))

    if analysis_tasks:
        entities, char_ids, tasks = zip(*analysis_tasks)
        results = await asyncio.gather(*tasks)
        
        for i in range(len(results)):
            dt, df, da, desc = results[i]
            if dt != 0 or df != 0 or da != 0:
                db.update_relationship(0, char_ids[i], dt, df, da, desc)
                print(f"Social: Updated relationship with {entities[i]}. Trust: {dt}, Fear: {df}, Affection: {da}")

if __name__ == "__main__":
    # Test
    import asyncio
    async def test():
        print("Testing Social Engine...")
        db.init_db()
        db.add_character("Elara", "A kind healer", "Empathetic, Observant")
        await update_social_state("I give Elara a rare medicinal herb I found.", "Elara smiles warmly. 'This will save many lives, thank you.'")
    
    asyncio.run(test())
