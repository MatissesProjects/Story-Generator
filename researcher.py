from duckduckgo_search import DDGS
import llm
import db
import config
import random

async def optimize_query(theme, context=""):
    """
    Uses the LLM to transform a broad theme into a high-signal search query.
    """
    prompt = f"""
[SYSTEM: You are the Research Optimizer. Your goal is to turn a simple story theme or concept into a high-signal search query that will find "weird facts," "niche lore," or "obscure science" to inspire a unique narrative turn.

THEME: {theme}
STORY CONTEXT: {context}

Example Query: "weirdest bioluminescent survival strategies in extreme environments"
Example Query: "obscure medieval laws regarding inheritance and ghosts"

Provide ONLY the search query string. No quotes or extra text.]
"""
    optimized = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
    return optimized.strip().strip('"').strip("'")

def search_inspiration(theme_query):
    """
    Performs a web search to find weird facts, niche lore, or science for inspiration.
    """
    print(f"Researcher: Searching for inspiration on '{theme_query}'...")
    with DDGS() as ddgs:
        # Search for weird facts or obscure trivia
        results = ddgs.text(f"weird obscure facts about {theme_query}", max_results=5)
        
    search_text = ""
    for r in results:
        search_text += f"Title: {r['title']}\nSnippet: {r['body']}\n\n"
        
    return search_text

async def extract_narrative_hooks(search_results, current_context=""):
    """
    Uses the LLM to extract crazy narrative ideas from search results.
    """
    prompt = f"""
I have found the following research results about a theme. 
Your goal is to extract 2-3 "Unexpected Narrative Hooks" that are crazy, unique, and would make a story more interesting. 

CURRENT STORY CONTEXT:
{current_context}

RESEARCH RESULTS:
{search_results}

FORMAT EACH HOOK AS:
[HOOK]: A concise description of the idea and how it could be used.
"""
    
    return await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)

async def perform_research_injection(theme, context=""):
    """
    The full pipeline: Search -> Extract -> Save to Lore/Plots.
    """
    optimized_query = await optimize_query(theme, context)
    print(f"Researcher: Optimized query: {optimized_query}")
    
    results = search_inspiration(optimized_query)
    hooks = await extract_narrative_hooks(results, context)
    
    # Simple parsing of the hooks (look for [HOOK])
    hook_list = [h.strip() for h in hooks.split("[HOOK]:") if h.strip()]
    
    for hook in hook_list:
        # Add to Lore
        db.add_lore(f"Research: {theme}", hook)
        # Also add as a plot thread for the Director to pick up
        db.add_plot_thread(f"DEVELOP THIS IDEA: {hook}")
        
    return hook_list

if __name__ == "__main__":
    # Test
    print("Testing Researcher...")
    ideas = perform_research_injection("deep sea bioluminescence")
    for i in ideas:
        print(f"Found Idea: {i}")
