# Frontend UI Implementation Plan

## Phase 1: Scaffolding & Connection
- [x] Create `static/index.html`, `static/style.css`, and `static/app.js`.
- [x] Implement WebSocket connection logic in `app.js`.
- [x] Update `server.py` to serve static files and the root `index.html`.

## Phase 2: Narrative Display & Audio
- [x] Build the chat/story display area with real-time streaming support.
- [x] Implement an audio manager in `app.js` to play `/audio/` files from `audio_event` messages.
- [x] Add a "Spark" button to trigger story ideas.

## Phase 3: Dashboard & Controls
- [x] Create a sidebar to show "Story So Far," "Plot Threads," and "Research Log."
- [x] Implement forms for adding Characters, Lore, and Plot Threads.
- [x] Add a "Debug Toggle" to show/hide the backend context facts.

## Phase 4: Aesthetic Polish
- [ ] Apply a "Narrative-First" theme with elegant typography and interactive feedback.
- [ ] Ensure the UI is responsive and provides clear states (e.g., "Thinking...", "Speaking...").
