# 🗺️ Implementation Plan: Multimodal Atmosphere

## Phase 1: Atmosphere Definition & Engine 💡
- [ ] Create `atmosphere_engine.py` with a registry of supported atmosphere types.
- [ ] Define the `AtmosphereCode` schema.
- [ ] Implement `get_current_atmosphere()` and `set_current_atmosphere()` in `db.py`.

## Phase 2: LLM Detection & Extraction 🔍
- [ ] Update `llm.py` or create a post-processing step to extract atmosphere changes from AI responses.
- [ ] Implement an "Atmosphere Detector" prompt that maps story text to structured codes.
- [ ] Hook into the turn loop in `server.py`.

## Phase 3: Dynamic Soundscapes (Ambiance) 🔊
- [ ] Extend `music_orchestrator.py` or add logic to `atmosphere_engine.py` to handle looping background ambiance (wind, rain, etc).
- [ ] Integrate with the local `AudioSequencer` paths for ambient assets.

## Phase 4: Frontend Signal Protocol 📡
- [ ] Standardize the `atmosphere_update` WebSocket message.
- [ ] (Optional) Update the static `app.js` (if it exists) to show how to handle these signals.

## Phase 5: Verification 🧪
- [ ] Create `test_atmosphere.py`.
- [ ] Ensure atmosphere persistence across turns.
