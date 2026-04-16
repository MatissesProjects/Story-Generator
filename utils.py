import json
import re

def safe_parse_json(text, default=None):
    """
    Safely extracts and parses JSON from LLM output, handling markdown blocks and garbage.
    """
    if not text:
        return default
        
    try:
        # 1. Try direct parse
        return json.loads(text.strip())
    except json.JSONDecodeError:
        # 2. Try extracting from markdown code blocks
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass
        
        # 3. Last ditch: find first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
                
    return default

def extract_character_mentions(text, character_names):
    """
    Extracts character names from text using word boundaries to prevent substring collisions
    (e.g., 'Alice' triggering 'Al').
    """
    found = []
    for name in character_names:
        # Use regex with word boundaries \b
        # We escape the name in case it has special characters
        pattern = r'\b' + re.escape(name) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found.append(name)
    return found
