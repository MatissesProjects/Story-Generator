# Visual Generation Implementation Plan

## Phase 1: Engine Selection & Setup
- [x] Research and select the best local image generation method (Diffusers with SDXL Turbo).
- [x] Implement `vision.py` to handle the generation requests.
- [x] Update `config.py` with image generation settings.

## Phase 2: Portrait Pipeline
- [x] Build the "Prompt Stylizer" in `llm.py` (Implemented in `vision.py`) to create high-quality art prompts.
- [x] Implement a system to cache generated images so we don't re-generate them unnecessarily.
- [x] Update `server.py` to handle image paths for each character.

## Phase 3: Frontend Integration
- [x] Add portrait display to the character sidebar in `index.html`.
- [x] Update `app.js` to handle image loading and display.
- [x] Implement an "Auto-Generate" trigger for new characters.
