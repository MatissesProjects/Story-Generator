# Logic Validation Plan

## Objective
Build a pre-generation interception layer to enforce world rules.

## Implementation Steps
1. **Validator Module**: Create `validator.py`.
2. **Fast LLM Check**: Use a fast, strictly prompted LLM call (or a secondary logic model if available) that takes the `user_input` and `context_facts`. The prompt asks: `Given the context, is this action possible? Reply ONLY with YES or NO, followed by a brief reason.`
3. **Loop Integration**: In `main.py` and `server.py`, run `validator.check_action()` before `llm.generate_story_segment()`.
4. **Failure Routing**: If `NO`, send a quick "action failed" message back to the client (e.g., "You try to do that, but realize you can't because...") instead of generating a full scene.

## Verification
- Create a scenario where a player is in an empty room.
- Player inputs: "I shoot the goblin with my laser."
- Verify the validator intercepts with a `NO` (no goblin, no laser) and prevents the main LLM from hallucinating a successful attack.s added to the database, and the tag is hidden from the user's view.