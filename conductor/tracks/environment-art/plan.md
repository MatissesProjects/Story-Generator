# Environment Art Implementation Plan

## Phase 1: Scene Detection
- [x] Implement `identify_location()` in `director.py` to track the current setting.
- [x] Add a `current_location` key to the `story_state` table in SQLite.

## Phase 2: Generation Engine Update
- [x] Extend `vision.py` to support high-quality landscape art.
- [x] Build the "Environment Stylizer" prompt in `vision.py`.
- [x] Implement a `generate_environment(location_name, description)` function.

## Phase 3: Frontend & Server Integration
- [x] Create a cinematic background container in `index.html`.
- [x] Update `server.py` to trigger environment generation on location changes.
- [x] Implement a `scene_update` WebSocket message to push new visuals to the client.
