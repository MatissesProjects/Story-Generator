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
        lines = self.buffer.split('\n')
        
        # We only process full lines (except the last one which might be incomplete)
        completed_blocks = []
        
        # If we have multiple lines, the ones before the last are definitely "done"
        if len(lines) > 1:
            for i in range(len(lines) - 1):
                line = lines[i].strip()
                if not line or line == "***": continue
                
                # Check for tag
                match = self.tag_pattern.match(line)
                if match:
                    speaker, content = match.groups()
                    speaker = speaker.strip()
                    if speaker.lower() in [t.lower() for t in IGNORED_TAGS]:
                        continue
                    completed_blocks.append((speaker, content.strip()))
                else:
                    # Check for system blocks without colon
                    clean_line = line.lower()
                    if any(clean_line.startswith(f"[{tag.lower()}") for tag in IGNORED_TAGS):
                        continue
                        
                    # Assume narrator if no tag
                    completed_blocks.append(("Narrator", line))
            
            # Keep only the last (potentially incomplete) line in the buffer
            self.buffer = lines[-1]
            
        return completed_blocks

    def flush(self):
        """Processes whatever is left in the buffer."""
        final_blocks = []
        line = self.buffer.strip()
        if not line or line == "***":
             self.buffer = ""
             return []

        match = self.tag_pattern.match(line)
        if match:
            speaker, content = match.groups()
            speaker = speaker.strip()
            if speaker.lower() in [t.lower() for t in IGNORED_TAGS]:
                self.buffer = ""
                return []
            final_blocks.append((speaker, content.strip()))
        else:
            # Check for system blocks without colon
            clean_line = line.lower()
            if any(clean_line.startswith(f"[{tag.lower()}") for tag in IGNORED_TAGS):
                self.buffer = ""
                return []
            final_blocks.append(("Narrator", line))
            
        self.buffer = ""
        return final_blocks

if __name__ == "__main__":
    test_text = "[Elara]: Look out! The beast is coming!\nMalakar: I see it. It's hideous."
    print("Testing parser...")
    for speaker, content in parse_dialogue(test_text):
        print(f"Speaker: {speaker}, Dialogue: {content}")