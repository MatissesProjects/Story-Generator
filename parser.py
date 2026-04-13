import re

def detect_intent(text):
    """
    Categorizes the user's input intent.
    Returns one of: 'CONTINUE', 'ACTION', 'DIALOGUE', 'SPARK', 'EMPTY'
    """
    text = text.strip().lower()
    
    if not text:
        return 'EMPTY'
        
    if text == "spark":
        return 'SPARK'
        
    # Keywords for continuation
    continue_keywords = [
        "continue", "more", "tell me more", "go on", "what happens next",
        "...", "next", "and then?"
    ]
    
    if text in continue_keywords:
        return 'CONTINUE'
        
    # Check if it looks like dialogue (starts with " or ')
    if text.startswith('"') or text.startswith("'"):
        return 'DIALOGUE'
        
    return 'ACTION'

def parse_dialogue(text):
    """
    Parses text for dialogue tags like [Character]: Dialogue or Character: "Dialogue".
    Returns a list of (speaker, content) tuples.
    """
    # Pattern to match [Name]: "text" or Name: "text" or [Name]: text
    # This is a basic regex and can be refined
    pattern = r'(?:\[?([A-Za-z0-9 ]+)\]?:\s*(.+))'
    
    matches = re.findall(pattern, text)
    if not matches:
        # If no specific tags, assume it's a general narrator
        return [("Narrator", text.strip())]
    
    return [(speaker.strip(), content.strip()) for speaker, content in matches]

if __name__ == "__main__":
    test_text = "[Elara]: Look out! The beast is coming!\nMalakar: I see it. It's hideous."
    print("Testing parser...")
    for speaker, content in parse_dialogue(test_text):
        print(f"Speaker: {speaker}, Dialogue: {content}")