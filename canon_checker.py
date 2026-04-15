import db
import llm
import json
import config

async def extract_claims(text):
    """
    Uses the LLM to extract factual world-building claims from a story segment.
    """
    prompt = f"""
[SYSTEM: You are the Chronicler. Analyze the following story segment and extract any new factual claims about the world, its history, geography, or characters.

STORY SEGMENT:
"{text}"

Reply ONLY with a JSON object containing a list of claims:
{{
    "claims": [
        "The city of Aethelgard was built on a floating island.",
        "The King has a secret twin brother."
    ]
}}

If no specific lore claims are made, return an empty list.
REPLY ONLY IN JSON.]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        return result.get("claims", [])
    except Exception as e:
        print(f"CanonChecker Error (extract_claims): {e}. Raw: {response}")
        return []

async def check_for_contradictions(claims, context_lore):
    """
    Compares extracted claims against existing lore to find contradictions.
    """
    if not claims:
        return []
        
    lore_text = "\n".join(context_lore)
    claims_text = "\n".join([f"- {c}" for c in claims])
    
    prompt = f"""
[SYSTEM: You are the Keeper of Canon. Compare the following NEW CLAIMS against the EXISTING LORE and identify any direct contradictions.

EXISTING LORE:
{lore_text}

NEW CLAIMS:
{claims_text}

Reply ONLY with a JSON object:
{{
    "contradictions": [
        {{
            "claim": "The city of Aethelgard is underground.",
            "violation": "Existing lore states Aethelgard is a floating island."
        }}
    ]
}}

If there are no contradictions, return an empty list.
REPLY ONLY IN JSON.]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        return result.get("contradictions", [])
    except Exception as e:
        print(f"CanonChecker Error (check_for_contradictions): {e}. Raw: {response}")
        return []

if __name__ == "__main__":
    # Test
    import asyncio
    async def test():
        print("Testing Canon Checker...")
        claims = await extract_claims("The mountain of Karak is home to the last dragon, who sleeps in a bed of gold.")
        print(f"Claims: {claims}")
        
    asyncio.run(test())
