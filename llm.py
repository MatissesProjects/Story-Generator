import requests
import json
import config

OLLAMA_URL = config.OLLAMA_URL

def generate_story_segment(prompt, model=config.OLLAMA_MODEL, context_facts=None, director_instructions=None):
    full_prompt = prompt
    
    # Build up system/context block
    context_blocks = []
    
    if context_facts:
        facts_block = "LORE/FACTS:\n" + "\n".join([f"- {f}" for f in context_facts])
        context_blocks.append(facts_block)
        
    if director_instructions:
        context_blocks.append(f"DIRECTIVE: {director_instructions}")
        
    if context_blocks:
        full_context = "\n\n".join(context_blocks)
        full_prompt = f"[SYSTEM: {full_context}]\n\n{prompt}"
    
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": True
    }
    
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            if "response" in chunk:
                yield chunk["response"]
            if chunk.get("done"):
                break

if __name__ == "__main__":
    # Simple test
    print("Testing Ollama connection...")
    try:
        for chunk in generate_story_segment("Write a one-sentence story about a cat in a space suit."):
            print(chunk, end="", flush=True)
        print("\nTest complete.")
    except Exception as e:
        print(f"\nError: {e}")