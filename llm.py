import httpx
import json
import config
import asyncio

OLLAMA_URL = config.OLLAMA_URL

def _build_full_prompt(prompt, context_facts=None, director_instructions=None, persona_blocks=None, narrative_seed=None, mechanical_result=None, foreshadowing_payoff=None, pacing_directive=None):
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

    if foreshadowing_payoff:
        context_blocks.append(f"FORESHADOWING: {foreshadowing_payoff}")

    if pacing_directive:
        pacing_instructions = {
            "Introspective": "Focus on the protagonist's internal thoughts, memories, and emotional reactions. Use evocative, sensory language.",
            "Action-Packed": "Use high-tempo verbs and short, punchy sentences. Focus on immediate physical threats, movement, and intensity.",
            "Mystery-Focused": "Focus on atmospheric detail, subtle clues, and lingering questions. Maintain a sense of uncertainty and intrigue.",
            "Dialogue-Heavy": "Focus on character subtext, verbal sparring, and the nuances of the conversation. Minimize physical description."
        }
        instr = pacing_instructions.get(pacing_directive, "")
        context_blocks.append(f"PACING: {pacing_directive}. {instr}")

    # CORE STORYTELLING DIRECTIVES
    core_directives = """
CORE DIRECTIVE: NEVER present the player with a numbered list of choices. Be PROACTIVE and narrate the world's reaction.

FORMATTING RULE: You MUST use character tags for ALL output.
- For character speech, use: [Character Name]: "Dialogue text"
- For actions, atmosphere, or descriptions, use: [Narrator]: Narrative text
- Example: 
  [Narrator]: The wind howls through the trees. 
  [Elara]: "We must hurry, the storm is coming."
"""
    context_blocks.append(core_directives)

    if context_blocks:
        full_context = "\n\n".join(context_blocks)
        full_prompt = f"[SYSTEM: {full_context}]\n\n{prompt}"
    
    return full_prompt

async def async_generate_story_segment(prompt, model=config.CREATIVE_MODEL, context_facts=None, director_instructions=None, persona_blocks=None, narrative_seed=None, mechanical_result=None, foreshadowing_payoff=None, pacing_directive=None):
    """
    Asynchronous version of generate_story_segment using httpx.
    """
    full_prompt = _build_full_prompt(prompt, context_facts, director_instructions, persona_blocks, narrative_seed, mechanical_result, foreshadowing_payoff, pacing_directive)
    
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": True,
        "options": {
            "keep_alive": config.OLLAMA_KEEP_ALIVE
        }
    }

    async with httpx.AsyncClient(timeout=config.OLLAMA_TIMEOUT) as client:
        async with client.stream("POST", OLLAMA_URL, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        yield chunk["response"]
                    if chunk.get("done"):
                        break

async def async_generate_full_response(prompt, model=config.CREATIVE_MODEL, **kwargs):
    """
    Utility to get a full non-streaming response asynchronously.
    """
    full_text = ""
    async for chunk in async_generate_story_segment(prompt, model=model, **kwargs):
        full_text += chunk
    return full_text

# For backward compatibility (legacy sync generator, but it's actually async now)
async def generate_story_segment(prompt, **kwargs):
    async for chunk in async_generate_story_segment(prompt, **kwargs):
        yield chunk

if __name__ == "__main__":
    # Simple test
    async def test():
        print("Testing Ollama connection...")
        try:
            async for chunk in async_generate_story_segment("Write a one-sentence story about a cat in a space suit."):
                print(chunk, end="", flush=True)
            print("\nTest complete.")
        except Exception as e:
            print(f"\nError: {e}")
    asyncio.run(test())
