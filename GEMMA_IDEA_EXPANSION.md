## 🧠 The System Architecture Blueprint

Your tool will operate in a **Loop**: **State Update $\rightarrow$ Context Creation $\rightarrow$ Generation $\rightarrow$ State Update/Output.**

### 1. The Core Engine: Ollama (The Brain)

This is where the LLM logic resides. You will be interacting with Ollama via its local API endpoint.

*   **Prompt Engineering is Key:** Do not treat this as a single prompt. You must build a sophisticated, multi-part system prompt that defines *its persona* as a story co-writer, given the rules of the world.
*   **System Prompt Example:** "You are a collaborative storyteller. You must maintain consistency with the established lore, character sheets, and previously agreed-upon plot points. Only write the *next segment* of dialogue/action. Adhere strictly to the character voice guidelines provided."

### 2. Memory and Consistency Layer (The External Database)

This is the most critical piece for managing state *outside* the LLM context window. You need a structured place to dump facts that the LLM might forget.

**Recommended Technology:** A simple, local **JSON file** or a **SQLite database** is perfect for this proof-of-concept.

**Data Structure to Track (The "Knowledge Base"):**

| Element | What to Store | How It Helps |
| :--- | :--- | :--- |
| **Character Sheets** | Name, Appearance (visual description), Personality Traits (e.g., "Sarcastic," "Cautious"), Voice Profile (if specific dialogue patterns apply). | Ensures consistent dialogue and physical description. |
| **World Lore/Canon** | Key rules of the world (e.g., "Magic requires sacrifice," "The city floats on residual energy"). | Prevents plot holes or magic system breaks. |
| **Plot Tracker** | List of major unresolved plot threads (e.g., "The King's secret identity," "The MacGuffin's location"). | Acts as a checklist to keep the story moving toward an intended climax. |
| **Timeline/State Log** | A chronological log of major events that *must* be referenced later (e.g., "Chapter 1: Elara lost the silver locket to the goblin king"). | Prevents characters from forgetting crucial past actions. |

### 3. Context Management Layer (The Efficiency Filter)

This solves your problem of not sending the whole story. This logic acts as a **"Context Curator."**

**The Logic Flow:**

1.  **Input:** The current Knowledge Base (from Step 2) + The Last 1-2 Turns of Dialogue.
2.  **Retrieval (RAG Concept):** You need a function that queries the Knowledge Base *based on the current prompt's focus*.
    *   *Example:* If the current scene involves "a confrontation with the guard," the Curator only pulls: 1) The Guard's profile, and 2) Any lore points related to guards or authority. It ignores the subplot about the lost locket.
3.  **Summarization:** You feed this filtered set of data, along with the last turns, into the LLM's prompt, prefaced with instructions like: **"CONSIDER THESE FACTS: [Inject relevant Lore/Character Data Here]. NOW, continue the story..."**

### 4. Audio & Character Voice (The Polish)

This requires a dedicated, local TTS engine. Sending audio through Ollama is not standard; you need a separate process.

**Recommended Technologies:**

*   **Piper TTS:** Excellent, relatively lightweight, and highly customizable for local use.
*   **Coqui TTS:** A more feature-rich, but potentially heavier, option.

**The Workflow:**

1.  **Identify Speaker:** The LLM output must clearly denote who is speaking (e.g., `[Character Name]: Dialogue text`).
2.  **Parse:** Your Python script parses this output, recognizing the speaker.
3.  **Generate:** For each line, the script calls the TTS engine, specifying the speaker (if the engine supports voice cloning/selection) and the text.
4.  **Output:** The TTS engine returns an audio file (e.g., `.mp3`) associated with that character/speaker, which you can then play back sequentially.

---

## 🛠️ Recommended Technology Stack Summary

| Component | Purpose | Recommended Tool/Library | Why? |
| :--- | :--- | :--- | :--- |
| **Orchestration/Glue** | Manages the entire loop, reading/writing state. | **Python** | Best ecosystem for combining file I/O, APIs, and external libraries. |
| **LLM Interaction** | Generating the text narrative. | **`requests` library** calling your local `http://localhost:11434/api/...` endpoint. | Direct control over the API calls. |
| **State Management** | Storing lore, characters, and plot points. | **SQLite** (for structured data) or **JSON** (for simplicity). | Persistent, local, and easy to read/write programmatically. |
| **Text-to-Speech** | Converting text to spoken audio. | **Piper TTS** (or similar local implementation). | Ensures the process is entirely offline and gives you character voice control. |

## 🚀 Actionable Implementation Plan (MVP Approach)

Do not try to build everything at once. Follow these steps sequentially:

**Phase 1: The Text MVP (Focus on Memory)**
1.  Set up Python to connect to your local Ollama instance.
2.  Create a simple `story_state.json` file.
3.  Write a loop: Generate text $\rightarrow$ Manually read the output $\rightarrow$ Manually update the JSON state file with key takeaways. *Do not worry about audio yet.*

**Phase 2: Smart Context Integration (Focus on Efficiency)**
1.  Implement the **Context Curator** logic (Section 3).
2.  Modify your script so that before calling Ollama, it reads the JSON state, generates a summary prompt, and sends only that summary + the last turn.

**Phase 3: Audio Polish (Focus on Output)**
1.  Install and test your chosen local TTS engine (e.g., Piper).
2.  Modify the loop: After receiving the text from Ollama, pass the text segments *along with the designated speaker* to the TTS engine to generate audio files.
