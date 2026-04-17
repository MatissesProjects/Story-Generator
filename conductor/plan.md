# Plot Thread Management: Dynamic Story Evolution

## Objective
Fix the persistent "goblin locket" story element and enable the story to genuinely build on itself by dynamically identifying new plot threads and resolving old ones based on the narrative history.

## Key Files & Context
- `director.py`: Contains the hardcoded string and will house the new analysis logic.
- `db.py`: Needs a new function to update the status of existing plot threads.
- `server.py` & `main.py`: The main execution loops where the new analysis function will be integrated.

## Implementation Steps
1. **Remove Hardcoded Thread:**
   - Remove `db.add_plot_thread("The silver locket was stolen by a goblin.")` from the `if __name__ == "__main__":` block in `director.py` to prevent it from ever being accidentally added to the database again.

2. **Database Update Function:**
   - Add a new function `update_plot_thread_status(thread_id, status)` in `db.py` to allow the system to mark plot threads as 'resolved' or 'inactive'.

3. **Dynamic Thread Analysis (`director.py`):**
   - Create a new asynchronous function `analyze_plot_threads(recent_history, active_threads)`.
   - This function will use the LLM to analyze the recent narrative context against the currently active plot threads.
   - It will return a structured JSON response indicating if any existing threads should be resolved and detailing any newly emerged plot threads.

4. **Integration into the Story Loop:**
   - Update `server.py` and `main.py` to call `analyze_plot_threads` periodically (e.g., every 3 turns, similar to how long-term memory summaries are handled).
   - Handle the returned JSON by resolving old threads via the new `db.py` function and adding new threads via `db.add_plot_thread()`.

5. **Database Wipe:**
   - Provide a brief script or instruction to safely delete the existing `story_memory.db` file so you can start completely fresh without the goblin locket polluting the context.

## Verification & Testing
- Start a new session (after wiping the database) and verify no hardcoded threads appear.
- Play through several turns and observe the system automatically creating new plot threads based on your actions.
- Confirm that resolved storylines correctly change their status in the database.
