import db
import llm
import json
import config
import utils

async def extract_claims(text):
    """
    Uses the LLM to extract factual world-building claims from a story segment.
    """
    prompt = f"""
[SYSTEM: You are the Chronicler. Analyze the following story segment and extract any new factual claims about the world, its history, geography, or characters.

STORY SEGMENT:
"{text}"

Reply ONLY with a JSON object containing a list of claims.
EXAMPLE STRUCTURE (Do not use these specific values):
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
        result = utils.safe_parse_json(response, default={})
        return result.get("claims", [])
    except Exception as e:
        print(f"CanonChecker Error (extract_claims): {e}. Raw: {response}")
        return []

async def resolve_contradiction(contradiction, context_lore):
    """
    Automated 'Lore Duel' resolution for canon contradictions.
    Decides whether to Retcon, mark as Unreliable Narrator, or trigger a World Change.
    """
    claim = contradiction['claim']
    violation = contradiction['violation']
    lore_str = "\n".join([f"- {l}" for l in context_lore])
    
    prompt = f"""
[SYSTEM: You are the Canon Resolution Engine. A contradiction has occurred in the story.
ESTABLISHED CANON:
{lore_str}

NEW CLAIM:
"{claim}"

VIOLATION:
"{violation}"

Decide how to resolve this. Choose one of the following approaches:
1. "Unreliable Narrator": The character or narrator was simply wrong, lying, or exaggerating. (The world state does not change).
2. "World Change": Something in the world has fundamentally changed to make the new claim true. (Generate a new lore entry explaining the shift).
3. "Retcon": The old canon was actually a misconception, and the new claim is the true reality. (Replace the old canon).

Reply ONLY with a JSON object.
EXAMPLE STRUCTURE (Do not use these specific values):
{{
    "resolution_type": "Unreliable Narrator" | "World Change" | "Retcon",
    "explanation": "A brief explanation of why this happened.",
    "new_lore": "If World Change or Retcon, provide the new lore string. Else null."
}}
]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
    
    try:
        result = utils.safe_parse_json(response, default={})
        
        # Apply the resolution
        rtype = result.get("resolution_type")
        if rtype in ["World Change", "Retcon"] and result.get("new_lore"):
            db.add_lore("Resolved Canon Shift", result["new_lore"])
            print(f"Canon Checker: Resolved via {rtype}. Added new lore: {result['new_lore']}")
        else:
            print(f"Canon Checker: Resolved via {rtype}. Explanation: {result.get('explanation')}")
            
        return result
        
    except Exception as e:
        print(f"CanonChecker Error (resolve_contradiction): {e}. Raw: {response}")
        return None

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

Reply ONLY with a JSON object.
EXAMPLE STRUCTURE (Do not use these specific values):
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
        result = utils.safe_parse_json(response, default={})
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
