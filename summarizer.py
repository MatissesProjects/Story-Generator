import db
import llm
import config

def update_narrative_seed():
    """
    Summarizes the recent history and updates the 'narrative_seed' in story_state.
    """
    # Get all history to build the full summary
    history = db.query_db("SELECT user_input, assistant_response FROM history ORDER BY id ASC")
    if not history:
        return
        
    history_text = ""
    for turn in history:
        history_text += f"Player: {turn['user_input']}\nStory: {turn['assistant_response']}\n\n"
        
    current_seed = db.get_story_state("narrative_seed") or "The story has just begun."
    
    prompt = f"""
Summarize the following story interaction into 3-5 key plot points that MUST be remembered for consistency. 
Focus on major events, character changes, and discovered items. 
Integrate these new points with the existing summary.

EXISTING SUMMARY:
{current_seed}

NEW INTERACTION:
{history_text}

Provide the updated summary as a concise list or paragraph.
"""
    
    # Use a direct, non-streaming call for the summary
    full_summary = ""
    for chunk in llm.generate_story_segment(prompt):
        full_summary += chunk
        
    db.set_story_state("narrative_seed", full_summary.strip())
    print(f"Updated Narrative Seed: {full_summary.strip()[:100]}...")

if __name__ == "__main__":
    print("Testing Summarizer...")
    # Add some dummy history if needed, then run
    update_narrative_seed()
