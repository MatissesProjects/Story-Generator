# 🏗️ Story Generator Architecture Map

This document serves as the foundational reference for the Story Generator's architecture. It maps out where logic resides, how data flows through the system, and how the "Brain" of the engine makes decisions.

---

## 🧭 System Overview
The system follows a **Modular Orchestration** pattern (an adaptation of MVC). It separates the **Source of Truth** (SQLite/ChromaDB) from the **Narrative Controller** (Director/Curator) and the **Generative View** (LLM/TTS/Vision).

- **Source of Truth (Model)**: `db.py`, `memory_engine.py`, `schema.sql`.
- **Narrative Controller (Controller)**: `director.py`, `curator.py`, `validator.py`.
- **Generative Engine (Service)**: `llm.py`, `tts.py`, `vision.py`, `summarizer.py`, `researcher.py`.
- **Orchestration Layer**: `server.py` (FastAPI + WebSockets).

---

## 📂 Logic Directory (File Responsibilities)

### 🧠 The Controllers (Decision Making)
| File | Responsibility | Key Logic |
| :--- | :--- | :--- |
| `director.py` | **Narrative DM** | Analyzes plot stagnation, identifies location changes, and generates hidden "Director Instructions" to nudge the story forward. |
| `curator.py` | **Context Manager** | Aggregates relevant facts from both SQLite (Keywords) and ChromaDB (Semantic) to build the prompt context. |
| `validator.py` | **Physics Engine** | Intercepts player actions before generation to ensure they are logically possible within the established world rules. |
| `foreshadowing.py` | **Narrative Seeds** | Extracts minor unresolved details from AI responses and triggers payoffs later in the story. |
| `canon_checker.py` | **Canon Auditor** | Validates LLM responses against established lore to prevent contradictions. |
| `inventory_stats` | **Entity State** | (Integrated in `db.py` and `validator.py`) Tracks player/NPC items and attributes, enforcing logic based on possession and power. |
| `pacing_director` | **Rhythm Control** | (Integrated in `server.py` and `llm.py`) Manages narrative tempo via directives like 'Action-Packed' or 'Introspective'. |
| `adventure_arcs` | **Milestone Manager** | (Integrated in `db.py` and `director.py`) Tracks multi-chapter story structures and handles milestone transitions. |

### 💾 The Persistence Layer (Memory)
| File | Responsibility | Key Logic |
| :--- | :--- | :--- |
| `db.py` | **Structured Memory** | Manages the SQLite connection. Stores characters, lore, plot threads, history, and key-value story states. |
| `memory_engine.py` | **Conceptual Memory** | Manages ChromaDB (Vector DB). Handles embedding generation and semantic similarity searches for "Atmospheric Recall." |
| `migrate_to_vector.py` | **Sync Utility** | Synchronizes existing SQLite data into the Vector Database. |

### 🎭 The Generative Services (Action)
| File | Responsibility | Key Logic |
| :--- | :--- | :--- |
| `llm.py` | **Core Intelligence** | Communicates with the local Ollama API. Routes tasks to the **CREATIVE_MODEL** (storytelling) or **FAST_MODEL** (logic/analysis). |
| `summarizer.py` | **Long-term Memory** | Periodically compresses story history into a "Narrative Seed" using the **FAST_MODEL**. |
| `researcher.py` | **Inspiration Engine** | Performs autonomous web searches (DuckDuckGo) to find "crazy new ideas" and injects them as new Lore/Plots. |
| `vision.py` | **Visual Engine** | Uses Stable Diffusion (SDXL Turbo) to generate character portraits and cinematic environment art. |
| `tts.py` | **Voice Engine** | Generates character-specific audio using local Piper TTS models. |

### 🔌 The Glue
| File | Responsibility | Key Logic |
| :--- | :--- | :--- |
| `server.py` | **Orchestrator** | The WebSocket server that coordinates every turn. It triggers validation, research, summarization, and media generation in sequence. |
| `parser.py` | **Text Processor** | Categorizes user intent (Continue vs Action) and parses LLM output for dialogue tags. |
| `config.py` | **Environment** | Centralized configuration for all model names, API URLs, and file paths. |

---

## 🌊 Data Lifecycle (The Turn Loop)

Every time a user sends a prompt, the system executes this sequence:

1.  **Intent Parsing**: `parser.py` decides if the user is acting, talking, or asking to "continue."
2.  **Validation**: `validator.py` checks if the action is legal. If `Invalid`, it returns a failure message immediately.
3.  **Context Gathering**:
    - `curator.py` pulls Lore/Characters from `db.py`.
    - `memory_engine.py` pulls thematic concepts from ChromaDB.
4.  **Narrative Direction**:
    - `director.py` evaluates plot threads and location.
    - `director.py` generates persona blocks for any characters involved.
5.  **Generation**: `llm.py` combines all the above into a massive "System Block" and generates the story text.
6.  **Media Generation**:
    - `parser.py` extracts dialogue.
    - `tts.py` generates audio files for each line.
    - `vision.py` (if applicable) generates a new scene or portrait.
7.  **Maintenance**:
    - `db.py` logs the history.
    - Every 10 turns: `summarizer.py` updates the "Story So Far" and `director.py` may trigger a `researcher.py` mission.

---

## 🛠️ Developer's Expansion Guide

### To Add a New Character Attribute:
1.  Update `schema.sql` and run `db.py`.
2.  Update `db.add_character()` and `memory_engine.add_character_vector()`.
3.  Update the Persona Block template in `director.get_persona_blocks()`.

### To Add a New Logic Rule:
1.  Update the prompt in `validator.validate_action()`.
2.  Add relevant "World Rules" to the `lore` table in the DB.

### To Change the Art Style:
1.  Modify the "Prompt Stylizer" functions in `vision.py`.

---

## 🚀 Key Architectural Strengths
- **Decoupled Media**: TTS and Vision are modular; the story generates even if they are slow or disabled.
- **Infinite Context**: The hierarchical memory (History -> Summary -> Semantic) prevents the AI from forgetting the past.
- **Proactive DM**: The Director Agent ensures the story doesn't just react to the user, but actively moves toward goals.
