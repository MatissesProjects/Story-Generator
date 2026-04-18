import db
import llm
import json
import config
import asyncio
import utils

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
        {
            "name": "Faded Map Fragment",
            "impact": "Could lead to a hidden mountain pass.",
            "category": "Item"
        }
    ]

}}
If no good seeds are found, return {{"seeds": []}}. REPLY ONLY IN JSON.]
"""
    response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
    result = utils.safe_parse_json(response)
    
    if result:
        seeds = result.get("seeds", [])
        for s in seeds:
            # DB now accepts category and initializes stage=1 (Planted)
            db.add_foreshadowed_element(s.get('name', 'Unknown'), current_location, s.get('impact', 'Unknown'))
            print(f"🌱 Planted [{s.get('category', 'General')}]: '{s.get('name', 'Unknown')}'")
    else:
        print(f"Foreshadowing Error: Failed to parse LLM response. Raw: {response}")


async def check_for_payoff(recent_history):
    """
    Wrapper for server.py to process recent history and evaluate for payoffs.
    """
    if not recent_history:
        return None
        
    # Format the last few turns into a single string for context
    context_str = "\n".join([f"User: {h['user_input']}\nAI: {h['assistant_response']}" for h in recent_history[-3:]])
    return await evaluate_context_for_payoff(context_str)


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
    decision = utils.safe_parse_json(response)
    
    if decision:
        if decision.get("selected_seed_id") is not None:
            # Fetch full seed data from DB
            seed_id = decision["selected_seed_id"]
            seed_data = next((s for s in pending if s["id"] == seed_id), None)
            
            if seed_data:
                action = decision.get('action_type', 'none')
                reasoning = decision.get('reasoning', 'None')
                instruction = (
                    f"NARRATIVE {action.upper()}: Organically weave the '{seed_data['element_name']}' "
                    f"(originally found in {seed_data['discovery_location']}) into the upcoming response. "
                    f"Context/Impact to consider: {seed_data['potential_impact']}. "
                    f"Reasoning: {reasoning}"
                )
                
                # In a real app, you'd update the DB state here (e.g., stage 1 -> 2, or mark as resolved)
                return seed_id, seed_data['element_name'], instruction
    else:
        print(f"Payoff Evaluation Error: Failed to parse LLM response. Raw: {response}")
        
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
    instruction = await evaluate_context_for_payoff("A massive stone golem rises from the desert sands, blocking your path!")
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
