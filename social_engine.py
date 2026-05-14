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

Reply ONLY with a JSON object.
EXAMPLE STRUCTURE (Do not use these specific values):
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


# Cache for characters currently being refined to avoid redundant LLM calls
PENDING_REFINEMENTS = set()

async def refine_character(name, context_text, original_tag=None):
    """
    Background task to refine character details and generate a portrait.
    """
    try:
        if name.lower() in ["stranger", "mysterious figure", "figure", "someone", "person"]:
            print(f"Social: Discovered placeholder '{name}', generating creative name...")
            new_name = await director.generate_creative_name("character", context_text)
            # Update the pre-registered name
            db.execute_db("UPDATE characters SET name = ? WHERE name = ?", (new_name, original_tag or name))
            name = new_name

        print(f"Social: Refining character details for: {name}")
        
        # Use LLM to get a quick description and traits
        prompt = f"""
[SYSTEM: You are the Character Architect. A new character named '{name}' has appeared in the story.
Based on this context, provide a brief description and their likely voice profile.

CONTEXT:
{context_text}

AVAILABLE VOICE PROFILES:
- "Deep Male": Authoritative, deep, older.
- "Melodic Female": Clear, expressive, younger.
- "Natural Female": Balanced, steady, common.
- "Upbeat Male": Friendly, conversational, younger.
- "Energetic Female": High-pitched, fast-paced, child or excitable.
- "British Male": Sophisticated, mature, scholarly.
- "British Female": Calm, noble, wise.
- "Scottish Female": Hearty, rough, regional.

Reply ONLY with a JSON object.
EXAMPLE STRUCTURE:
{{
    "description": "Short bio",
    "traits": "Comma separated traits",
    "voice_profile": "Deep Male"
}}
]
"""
        response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        data = utils.safe_parse_json(response)
        
        if data:
            profile = data.get("voice_profile", "Natural Female")
            v_id = config.VOICE_PROFILES.get(profile, config.DEFAULT_VOICE)
            
            # Update the character record
            db.execute_db("""
                UPDATE characters 
                SET description = ?, traits = ?, voice_id = ? 
                WHERE name = ?
            """, (data.get("description", "A mysterious figure."), 
                data.get("traits", "Unknown"), 
                v_id, 
                name))
            
            print(f"Social: Refined character '{name}' with profile '{profile}' -> voice {v_id}")
            # Portrait generation is already its own background task
            asyncio.create_task(vision.generate_portrait(name, data.get("description", ""), data.get("traits", "")))
            
    except Exception as e:
        print(f"Social: Error refining character '{name}': {e}")
    finally:
        if name.lower() in PENDING_REFINEMENTS:
            PENDING_REFINEMENTS.remove(name.lower())
        if original_tag and original_tag.lower() in PENDING_REFINEMENTS:
            PENDING_REFINEMENTS.remove(original_tag.lower())

async def register_new_character(name, context_text):
    """
    Automatically adds a new character to the database with a fitting voice
    based on the story context.
    """
    if name.lower() in PENDING_REFINEMENTS:
        return

    # 1. Immediate Registration with a random voice to prevent TTS fallback
    # This ensures that even if the refinement LLM is slow, the first block has a voice.
    print(f"Social: Pre-registering character '{name}'...")
    db.add_character(name, "A newly discovered figure.", "Unknown", voice_id=None)
    
    # 2. Spawn Refinement in background
    PENDING_REFINEMENTS.add(name.lower())
    asyncio.create_task(refine_character(name, context_text, original_tag=name))

async def discover_new_characters(response_text):
    """
    Scans the response for new character names and registers them in the DB.
    Uses a more permissive regex and case-insensitive checks.
    """
    known_chars = [c['name'].lower() for c in db.get_all_characters()]
    
    # Stricter name extraction: requires [Name]:
    # Supports names with spaces, numbers, and common punctuation
    import re
    potential_names = re.findall(r'\[([A-Za-z0-9 _-]+)\]:', response_text)
    
    if potential_names:
        print(f"Social: Scanned text, found potential speakers: {potential_names}")

    for name in potential_names:
        name_clean = name.strip()
        if not parser.is_valid_name(name_clean):
            continue
            
        if name_clean.lower() not in known_chars and name_clean.lower() != "narrator":
            print(f"Social: Character '{name_clean}' not in DB. Registering...")
            await register_new_character(name_clean, response_text)
            known_chars.append(name_clean.lower())

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
