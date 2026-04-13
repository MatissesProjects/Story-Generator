import re

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