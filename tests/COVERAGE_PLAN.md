# Test Coverage Plan (Target: 100%)

Current Coverage: **62%**
Status: **Stable (34/34 passing)**

## Phase 1: Core Utilities & Robustness (Target: 90%+)
Focus on the foundational modules that others depend on.

- [ ] **llm.py** (Current: 36%): Test error handling, timeouts, and fallback logic. Mock `httpx` to simulate network failures.
- [ ] **utils.py** (Current: 69%): Test edge cases for `safe_parse_json` with malformed LLM outputs.
- [ ] **validator.py** (Current: 65%): Test complex logic validation prompts and parsing failures.
- [ ] **db.py** (Current: 66%): Test all unused query functions and error paths (sqlite3 exceptions).

## Phase 2: Narrative & Plot Logic (Target: 90%+)
Test the "brains" of the story generation.

- [ ] **director.py** (Current: 58%): Test diverse action plan scenarios, character introductions, and location transitions.
- [ ] **foreshadowing.py** (Current: 31%): Test seed extraction, payoff triggers, and tracking logic.
- [ ] **canon_checker.py** (Current: 51%): Test contradiction detection and various resolution types (Retcon vs. Adjustment).
- [ ] **summarizer.py** (Current: 68%): Test incremental summarization with large history blocks.

## Phase 3: World Simulation (Target: 90%+)
Test the background mechanics.

- [ ] **social_engine.py** (Current: 44%): Test multi-character interactions and relationship evolution.
- [ ] **agency_engine.py** (Current: 69%): Test NPC need decay, goal selection, and travel mechanics.
- [ ] **world_engine.py** (Current: 63%): Test location resolution, coordinate collisions, and property detection.
- [ ] **simulation_manager.py** (Current: 74%): Test tick coordination and background event generation.

## Phase 4: Perception & Output (Target: 90%+)
Test the sensory layers.

- [ ] **parser.py** (Current: 9%): **CRITICAL GAP**. Test dialogue parsing, system tag filtering, and complex narrative block extraction.
- [ ] **tts.py** (Current: 16%): Test Piper integration, audio caching, and voice selection.
- [ ] **vision.py** (Current: 19%): Test image generation triggers, caching, and multi-threaded offloading.
- [ ] **music_orchestrator.py** (Current: 25%): Test mood detection and track selection logic.

## Technical Requirements for 100%
1. **Mock everything external**: Ollama API, Piper TTS, Stable Diffusion, and file system I/O.
2. **Branch Coverage**: Ensure all `if/else` and `try/except` paths are hit.
3. **Environment Isolation**: Maintain strict DB and Cache isolation (already implemented in `conftest.py`).
