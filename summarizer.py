import db
import llm
import config

async def update_narrative_seed():
    """
    Summarizes the recent history and updates the 'narrative_seed' in story_state.
    """
    try:
        # Get recent history to build the incremental summary
        history = db.get_recent_history(limit=10)
        if not history:
            return
            
        history_text = ""
        for turn in reversed(history): # get_recent_history returns newest first
            history_text += f"Player: {turn['user_input']}\nStory: {turn['assistant_response']}\n\n"
            
        current_seed = db.get_story_state("narrative_seed") or "The story has just begun."
        
        prompt = f"""
[SYSTEM: You are the Narrative Summarizer. Your goal is to maintain a concise, high-level summary of the story's progress so far.

CURRENT SUMMARY:
{current_seed}

RECENT EVENTS:
{history_text}

Provide the updated summary as a concise list or paragraph.
Include key plot developments, discovered locations, and major character changes.
REPLY ONLY WITH THE UPDATED SUMMARY.]
"""
        
        # Use a direct, non-streaming call for the summary
        full_summary = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
            
        if full_summary:
            db.set_story_state("narrative_seed", full_summary.strip())
            print(f"Updated Narrative Seed: {full_summary.strip()[:100]}...")
            
    except Exception as e:
        print(f"Summarizer Error: {e}")

if __name__ == "__main__":
    import asyncio
    async def test():
        print("Testing Summarizer...")
        db.init_db()
        await update_narrative_seed()
    
    asyncio.run(test())
