# Core Engine & Memory Plan

## Objective
Implement the basic Python backend connecting to Ollama and managing the SQLite database.

## Implementation Steps
1.  **Database Setup**: Create `schema.sql` defining `Characters` (id, name, description, traits), `Lore` (id, topic, description), `Plot_Threads` (id, description, status), and `Timeline` (id, event_description).
2.  **Database Interface**: Write a Python module (`db.py`) to handle SQLite connections and queries.
3.  **LLM Interface**: Write a Python module (`llm.py`) using `requests` or `aiohttp` to send prompts to `http://localhost:11434/api/generate` and receive the streaming response.
4.  **Basic Loop**: Create a `main.py` that ties these together, taking user input, querying the LLM, and allowing manual updates to the database.

## Verification
- Test database insertion and retrieval for all tables.
- Verify the LLM can generate text based on a simple prompt and return it to the script.