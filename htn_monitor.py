import llm
import config
import utils

async def verify_task_completion(task_description, recent_history_text):
    """
    Uses the LLM to judge if a specific HTN primitive task was successfully 
    accomplished based on the most recent narrative developments.
    """
    prompt = f"""
[SYSTEM: You are the Narrative Auditor. Your goal is to determine if a specific plot task was successfully accomplished in the story.

TASK:
"{task_description}"

RECENT STORY DEVELOPMENTS:
"{recent_history_text}"

Reply ONLY with a JSON object.
EXAMPLE STRUCTURE (Do not use these specific values):
{{
    "accomplished": true,
    "explanation": "The player successfully interrogated the suspect and got the confession."
}}

REPLY ONLY IN JSON.]
"""
    try:
        response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        result = utils.safe_parse_json(response, default={})
        return result.get("accomplished", False), result.get("explanation", "No explanation provided.")
    except Exception as e:
        print(f"HTN Monitor Error: {e}")
        return False, f"Error verifying task: {e}"
