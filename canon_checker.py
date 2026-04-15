import db
import llm
import json

def extract_claims(text):
    """
    Uses the LLM to extract factual world-building claims from a story segment.
    """
    prompt = f"""
[SYSTEM: You are the Canon Auditor. Your task is to identify and extract any new "World-Building Facts" or "Lore Assertions" made in the following text. 

A "Lore Assertion" is a statement that establishes a rule, a property of a species, a historical event, or a law of magic/physics.

TEXT:
"{text}"

Reply ONLY with a JSON object containing a list of claims:
{{
    "claims": [
        "Dragons are immune to fire.",
        "The Silver Order was founded 200 years ago.",
        "Casting magic requires a focus crystal."
    ]
}}

If no specific lore claims are made, return an empty list.
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
        return result.get("claims", [])
    except Exception as e:
        print(f"CanonChecker Error (extract_claims): {e}. Raw: {response}")
        return []

def check_for_contradictions(claims, context_lore):
    """
    Compares extracted claims against existing lore to find contradictions.
    """
    if not claims or not context_lore:
        return []

    lore_str = "\n".join([f"- {l}" for l in context_lore])
    claims_str = "\n".join([f"- {c}" for c in claims])

    prompt = f"""
[SYSTEM: You are the Lore Arbiter. Compare the "NEW CLAIMS" against the "ESTABLISHED CANON" and identify any direct contradictions.

ESTABLISHED CANON:
{lore_str}

NEW CLAIMS:
{claims_str}

If a new claim contradicts established canon, explain why.
Reply ONLY with a JSON object:
{{
    "contradictions": [
        {{"claim": "Dragons are immortal", "violation": "Established canon states dragons die after 500 years."}}
    ]
}}

If there are no contradictions, return an empty list.
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
        return result.get("contradictions", [])
    except Exception as e:
        print(f"CanonChecker Error (check_contradictions): {e}. Raw: {response}")
        return []

if __name__ == "__main__":
    # Test
    print("Testing Canon Checker...")
    text = "The Dragon King, being immortal, watched the centuries pass without aging."
    lore = ["LORE: Dragons are powerful but finite; they usually live for about 500 years before passing away."]
    
    claims = extract_claims(text)
    print(f"Extracted Claims: {claims}")
    
    violations = check_for_contradictions(claims, lore)
    print(f"Violations: {violations}")
