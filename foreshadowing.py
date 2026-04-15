import db
import llm
import json
import config
import asyncio

async def extract_seeds(assistant_response: str, current_location: str = "Unknown"):
    """
    Analyzes the AI response for minor details and categorizes them.
    """
    prompt = f"""
[SYSTEM: You are the Foreshadowing Architect. Analyze the following story segment and identify 1-2 minor, unresolved details. 

STORY SEGMENT:
"{assistant_response}"

LOCATION: {current_location}

Categorize the seed as: 'Item', 'Character', 'Lore', or 'Environment'.

Reply ONLY with a JSON object:
{{
    "seeds": [
        {{
            "name": "Strange Silver Coin",
            "impact": "Could be a key to a specific vault.",
            "category": "Item"
        }}
    ]
}}
If no good seeds are found, return {{"seeds": []}}. REPLY ONLY IN JSON.]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            
        result = json.loads(clean_json)
        seeds = result.get("seeds", [])
        
        for s in seeds:
            # DB now accepts category and initializes stage=1 (Planted)
            db.add_foreshadowed_element(s['name'], current_location, s['impact'])
            print(f"🌱 Planted [{s['category']}]: '{s['name']}'")
            
    except Exception as e:
        print(f"Foreshadowing Error: {e}")


async def evaluate_context_for_payoff(current_scene_context: str):
    """
    Passes pending seeds and current context to an LLM to find an organic fit.
    """
    pending = db.get_pending_foreshadowing()
    if not pending:
        return None

    # Optional: Filter out seeds that were planted too recently (e.g., check turn counts)
    
    # Create a simplified list for the LLM to save tokens
    # element_name, discovery_location, potential_impact
    seed_menu = [{"id": s["id"], "name": s["element_name"]} for s in pending]

    prompt = f"""
[SYSTEM: You are the Narrative Weaver. Evaluate the CURRENT SCENE against a list of PENDING SEEDS.
Your goal is to decide if any of the seeds naturally fit into the current scene for a callback or payoff.

CURRENT SCENE:
"{current_scene_context}"

PENDING SEEDS:
{json.dumps(seed_menu, indent=2)}

Decide if ONE seed is a perfect fit. If so, choose an action:
- "escalate": Bring the seed up again to raise mystery/tension without fully explaining it.
- "payoff": Reveal the true nature or impact of the seed.

If no seeds fit naturally, return null for selected_seed_id.

Reply ONLY with a JSON object:
{{
    "selected_seed_id": 12,
    "reasoning": "The characters are entering a dark cave, a perfect time for the glowing moss (Environment) to return.",
    "action_type": "escalate" 
}}
]"""

    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
    
    try:
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            
        decision = json.loads(clean_json)
        
        if decision.get("selected_seed_id") is not None:
            # Fetch full seed data from DB
            seed_id = decision["selected_seed_id"]
            seed_data = next((s for s in pending if s["id"] == seed_id), None)
            
            if seed_data:
                instruction = (
                    f"NARRATIVE {decision['action_type'].upper()}: Organically weave the '{seed_data['name']}' "
                    f"(originally found in {seed_data['location']}) into the upcoming response. "
                    f"Context/Impact to consider: {seed_data['impact']}. "
                    f"Reasoning: {decision['reasoning']}"
                )
                
                # In a real app, you'd update the DB state here (e.g., stage 1 -> 2, or mark as resolved)
                return seed_id, seed_data['name'], instruction

    except Exception as e:
        print(f"Payoff Evaluation Error: {e}")
        
    return None

async def main():
    print("--- Testing Foreshadowing Engine ---\n")
    
    # 1. Plant a seed
    await extract_seeds(
        "As you walk through the marketplace, an old man drops a strange silver coin with a hole in it. He doesn't notice and keeps walking.", 
        "The Marketplace"
    )
    
    # 2. Evaluate an unrelated scene (LLM should ideally reject this in reality)
    print("\nEvaluating action scene...")
    instruction = await evaluate_context_for_payoff("The goblin swings his rusty sword at your head as the tavern erupts into a brawl!")
    if instruction:
        print(f"🔥 Triggered: {instruction[2]}")
    else:
        print("⏸️ No fit found for current scene.")

    # 3. Evaluate a related scene
    print("\nEvaluating relevant scene...")
    instruction = await evaluate_context_for_payoff("You approach the massive stone door of the vault. There is no handle, only a small, perfectly circular slot in the center.")
    if instruction:
         print(f"🔥 Triggered: {instruction[2]}")

if __name__ == "__main__":
    asyncio.run(main())
