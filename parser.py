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
    pattern = r'(?:\[?([A-Za-z0-9 ]+)\]?:\s*(.+))'
    
    matches = re.findall(pattern, text)
    if not matches:
        return [("Narrator", text.strip())]
    
    return [(speaker.strip(), content.strip()) for speaker, content in matches]

class StreamParser:
    """
    Stateful parser for streaming LLM output. 
    Identifies completed dialogue blocks as they arrive.
    """
    def __init__(self):
        self.buffer = ""
        self.processed_index = 0
        # Matches [Speaker]: Text until a newline or next speaker tag
        self.tag_pattern = re.compile(r'\[?([A-Za-z0-9 ]+)\]?:\s*(.*?)(?=\n|\[?[A-Za-z0-9 ]+\]?:|$)', re.DOTALL)

    def feed(self, chunk):
        self.buffer += chunk
        lines = self.buffer.split('\n')
        
        # We only process full lines (except the last one which might be incomplete)
        completed_blocks = []
        
        # If we have multiple lines, the ones before the last are definitely "done"
        if len(lines) > 1:
            for i in range(len(lines) - 1):
                line = lines[i].strip()
                if not line: continue
                
                # Check for tag
                match = self.tag_pattern.match(line)
                if match:
                    speaker, content = match.groups()
                    completed_blocks.append((speaker.strip(), content.strip()))
                else:
                    # Assume narrator if no tag
                    completed_blocks.append(("Narrator", line))
            
            # Keep only the last (potentially incomplete) line in the buffer
            self.buffer = lines[-1]
            
        return completed_blocks

    def flush(self):
        """Processes whatever is left in the buffer."""
        final_blocks = []
        line = self.buffer.strip()
        if line:
            match = self.tag_pattern.match(line)
            if match:
                speaker, content = match.groups()
                final_blocks.append((speaker.strip(), content.strip()))
            else:
                final_blocks.append(("Narrator", line))
        self.buffer = ""
        return final_blocks

if __name__ == "__main__":
    test_text = "[Elara]: Look out! The beast is coming!\nMalakar: I see it. It's hideous."
    print("Testing parser...")
    for speaker, content in parse_dialogue(test_text):
        print(f"Speaker: {speaker}, Dialogue: {content}")