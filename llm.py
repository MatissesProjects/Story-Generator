import requests
import json
import config

OLLAMA_URL = config.OLLAMA_URL

def generate_story_segment(prompt, model=config.OLLAMA_MODEL, context_facts=None, director_instructions=None, persona_blocks=None, narrative_seed=None, mechanical_result=None):
    full_prompt = prompt
    
    # Build up system/context block
    context_blocks = []
    
    if narrative_seed:
        context_blocks.append(f"STORY SO FAR:\n{narrative_seed}")
        
    if persona_blocks:
        persona_text = "CHARACTER PERSONAS:\n" + "\n".join(persona_blocks)
        context_blocks.append(persona_text)
        
    if context_facts:
        facts_block = "LORE/FACTS:\n" + "\n".join([f"- {f}" for f in context_facts])
        context_blocks.append(facts_block)
        
    if director_instructions:
        context_blocks.append(f"DIRECTIVE: {director_instructions}")

    if mechanical_result:
        context_blocks.append(f"MECHANICS: {mechanical_result}")
        
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