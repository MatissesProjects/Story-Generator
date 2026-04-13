import requests
import json
import config

OLLAMA_URL = config.OLLAMA_URL

def generate_story_segment(prompt, model=config.OLLAMA_MODEL, context_facts=None):
    full_prompt = prompt
    if context_facts:
        facts_block = "\n".join([f"- {f}" for f in context_facts])
        full_prompt = f"[SYSTEM: Consider these facts:\n{facts_block}]\n\n{prompt}"
    
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