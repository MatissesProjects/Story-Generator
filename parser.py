import re

# System tags and metadata headers that should NEVER be spoken by TTS
IGNORED_TAGS = [
    "Script", "System", "Director", "Logic", "Objective", "Status", 
    "Sequence Update", "MECHANICAL RESULT", "MECHANICS", "FORESHADOWING",
    "STORY SO FAR", "CHARACTER PERSONAS", "LORE/FACTS", "DIRECTIVE", "PACING",
    "DiceMaster", "SUDDEN EVENT", "VISUAL", "IMAGE", "ENVIRONMENT", "ATMOSPHERE",
    "LIGHTING", "HAPTIC", "TINT", "SCENE"
]

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

def is_valid_name(name):
    """
    Validates if a string is likely a character name.
    Ignores strings that are too long, have too many words, or look like narrative.
    """
    name = name.strip()
    if not name:
        return False
    
    # Names should be reasonable length (e.g., max 30 chars)
    if len(name) > 30:
        return False
        
    # Names shouldn't have too many words (e.g., max 4)
    words = name.split()
    if len(words) > 4:
        return False
        
    # Ignore names that look like descriptive text or have multiple punctuation marks
    # but allow spaces, dashes, and underscores
    if any(p in name for p in [".", ",", "!", "?", ";"]):
        return False
        
    return True

def parse_dialogue(text):
    """
    Parses text for dialogue tags like [Character]: Dialogue.
    Returns a list of (speaker, content) tuples.
    """
    # Matches [Speaker]: Text until the next speaker tag or end of string
    tag_pattern = re.compile(r'\[([A-Za-z0-9 _-]+)\]:\s*(.*?)(?=\[[A-Za-z0-9 _-]+\]:|$)', re.DOTALL)
    
    matches = list(tag_pattern.finditer(text))
    if not matches:
        # Check if it's an ignored system line (starts with [TAG])
        clean_text = text.strip().lower()
        if any(clean_text.startswith(f"[{tag.lower()}") for tag in IGNORED_TAGS) or clean_text == "***":
            return []
        return [("Narrator", text.strip())]
    
    results = []
    # Process text BEFORE first tag
    pre_text = text[:matches[0].start()].strip()
    if pre_text:
        results.append(("Narrator", pre_text))
        
    for match in matches:
        speaker, content = match.groups()
        speaker = speaker.strip()
        if speaker.lower() in [t.lower() for t in IGNORED_TAGS]:
            continue
            
        if not is_valid_name(speaker):
            results.append(("Narrator", f"[{speaker}]: {content}".strip()))
            continue

        if content.strip():
            results.append((speaker, content.strip()))
    
    return results

class StreamParser:
    """
    Stateful parser for streaming LLM output. 
    Identifies completed dialogue blocks as they arrive.
    """
    def __init__(self):
        self.buffer = ""
        # Matches [Speaker]: Text until a newline or next speaker tag
        self.tag_pattern = re.compile(r'\[([A-Za-z0-9 _-]+)\]:\s*(.*?)(?=\n|\[[A-Za-z0-9 _-]+\]:|$)', re.DOTALL)

    def feed(self, chunk):
        self.buffer += chunk
        lines = self.buffer.split('\n')
        completed_blocks = []
        
        if len(lines) > 1:
            for i in range(len(lines) - 1):
                line = lines[i]
                completed_blocks.extend(parse_dialogue(line))

            self.buffer = lines[-1]
            
        return completed_blocks

    def flush(self):
        """Processes whatever is left in the buffer."""
        blocks = parse_dialogue(self.buffer)
        self.buffer = ""
        return blocks

if __name__ == "__main__":
    test_text = "[Elara]: Look out! [Narrator]: The beast is coming!\nMalakar: I see it."
    print("Testing parser...")
    for speaker, content in parse_dialogue(test_text):
        print(f"Speaker: {speaker}, Dialogue: {content}")
