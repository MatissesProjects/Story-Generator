import llm
import db
import config

async def perform_research_injection(theme, context=""):
    """
    Uses the LLM to generate fresh, interesting lore or plot ideas based on a theme.
    Automatically adds it to the database to inspire future turns.
    """
    prompt = f"""
[SYSTEM: You are the Lead Researcher. The story needs fresh inspiration regarding the theme: '{theme}'.
Analyze the current story context and provide a single, compelling factual claim or a new mysterious element that could be introduced.

STORY CONTEXT:
"{context}"

Reply ONLY with the new lore/fact. Be specific, evocative, and consistent with the tone.
Example: "The Order of the Sun actually worships the eclipse, and their temples are built to mirror the alignment of the planets."]
"""
    new_fact = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
    
    if new_fact:
        # Add to lore as a 'research_injection'
        db.add_lore(f"Research: {theme}", new_fact)
        print(f"Researcher: Injected new lore for '{theme}': {new_fact}")
        return new_fact
        
    return None

async def identify_research_topics(history_text):
    """
    Analyzes the story for missing details that could be fleshed out.
    """
    prompt = f"""
[SYSTEM: You are the Research Director. Analyze the following story and identify one interesting concept, location, or group that hasn't been fully explained yet.

STORY:
"{history_text}"

Reply with ONLY the name/theme of the topic.
Example: "The history of the Crimson Keep"]
"""
    return await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)

if __name__ == "__main__":
    import asyncio
    async def test():
        print("Testing Researcher...")
        fact = await perform_research_injection("Ancient ruins", "The player is exploring a desert.")
        print(f"Fact: {fact}")
    
    asyncio.run(test())
