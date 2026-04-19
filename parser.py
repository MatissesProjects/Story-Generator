import re

# System tags and metadata headers that should NEVER be spoken by TTS
IGNORED_TAGS = [
    "Script", "System", "Director", "Logic", "Objective", "Status", 
    "Sequence Update", "MECHANICAL RESULT", "MECHANICS", "FORESHADOWING",
    "STORY SO FAR", "CHARACTER PERSONAS", "LORE/FACTS", "DIRECTIVE", "PACING",
    "DiceMaster", "SUDDEN EVENT"
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

def parse_dialogue(text):
    """
    Parses text for dialogue tags like [Character]: Dialogue or Character: "Dialogue".
    Returns a list of (speaker, content) tuples.
    """
    # Pattern to match [Name]: "text" or Name: "text" or [Name]: text
    # Support for characters like - and _ in names
    pattern = r'(?:\[?([A-Za-z0-9 _-]+)\]?:\s*(.+))'
    
    matches = re.findall(pattern, text)
    if not matches:
        # Check if the text itself should be ignored (e.g. metadata)
        # More flexible check: see if it starts with [TAG
        clean_text = text.strip().lower()
        if any(clean_text.startswith(f"[{tag.lower()}") for tag in IGNORED_TAGS) or clean_text == "***":
            return []
        return [("Narrator", text.strip())]
    
    results = []
    for speaker, content in matches:
        speaker = speaker.strip()
        if speaker.lower() in [t.lower() for t in IGNORED_TAGS]:
            continue
        results.append((speaker, content.strip()))
    
    return results

class StreamParser:
    """
    Stateful parser for streaming LLM output. 
    Identifies completed dialogue blocks as they arrive.
    """
    def __init__(self):
        self.buffer = ""
        self.processed_index = 0
        # Matches [Speaker]: Text until a newline or next speaker tag
        self.tag_pattern = re.compile(r'\[?([A-Za-z0-9 _-]+)\]?:\s*(.*?)(?=\n|\[?[A-Za-z0-9 _-]+\]?:|$)', re.DOTALL)

    def feed(self, chunk):
        self.buffer += chunk
        
        # We process by lines, but we look for tags WITHIN lines now.
        lines = self.buffer.split('\n')
        completed_blocks = []
        
        if len(lines) > 1:
            for i in range(len(lines) - 1):
                line = lines[i].strip()
                if not line or line == "***": continue
                
                # Use finditer to find ALL tags in the line, and the text between them
                # This handles cases like: "Narrator text. [Character]: Dialogue"
                matches = list(self.tag_pattern.finditer(line))
                
                if not matches:
                    # No tags at all, check if it's an ignored system tag
                    clean_line = line.lower()
                    if any(clean_line.startswith(f"[{tag.lower()}") for tag in IGNORED_TAGS):
                        continue
                    completed_blocks.append(("Narrator", line))
                else:
                    # Process the text BEFORE the first tag as Narrator
                    first_match_start = matches[0].start()
                    pre_text = line[:first_match_start].strip()
                    if pre_text:
                        completed_blocks.append(("Narrator", pre_text))
                    
                    # Process each matched block
                    for match in matches:
                        speaker, content = match.groups()
                        speaker = speaker.strip()
                        if speaker.lower() in [t.lower() for t in IGNORED_TAGS]:
                            continue
                        
                        # Normalize "Narrator"
                        if speaker.lower() == "narrator":
                            speaker = "Narrator"
                            
                        if content.strip():
                            completed_blocks.append((speaker, content.strip()))

            self.buffer = lines[-1]
            
        return completed_blocks

    def flush(self):
        """Processes whatever is left in the buffer."""
        line = self.buffer.strip()
        self.buffer = ""
        
        if not line or line == "***":
             return []

        completed_blocks = []
        matches = list(self.tag_pattern.finditer(line))
        
        if not matches:
            clean_line = line.lower()
            if any(clean_line.startswith(f"[{tag.lower()}") for tag in IGNORED_TAGS):
                return []
            completed_blocks.append(("Narrator", line))
        else:
            first_match_start = matches[0].start()
            pre_text = line[:first_match_start].strip()
            if pre_text:
                completed_blocks.append(("Narrator", pre_text))
            
            for match in matches:
                speaker, content = match.groups()
                speaker = speaker.strip()
                if speaker.lower() in [t.lower() for t in IGNORED_TAGS]:
                    continue
                
                # Normalize "Narrator"
                if speaker.lower() == "narrator":
                    speaker = "Narrator"

                if content.strip():
                    completed_blocks.append((speaker, content.strip()))
            
        return completed_blocks

if __name__ == "__main__":
    test_text = "[Elara]: Look out! The beast is coming!\nMalakar: I see it. It's hideous."
    print("Testing parser...")
    for speaker, content in parse_dialogue(test_text):
        print(f"Speaker: {speaker}, Dialogue: {content}")