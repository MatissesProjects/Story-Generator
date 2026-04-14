# Environment Art Implementation Plan

## Phase 1: Scene Detection
- [ ] Implement `identify_location()` in `director.py` to track the current setting.
- [ ] Add a `current_location` key to the `story_state` table in SQLite.

## Phase 2: Generation Engine Update
- [ ] Extend `vision.py` to support landscape/environment aspect ratios (e.g., 16:9).
- [ ] Build the "Environment Stylizer" prompt in `vision.py`.
- [ ] Implement a `generate_environment(location_name, description)` function.

## Phase 3: Frontend & Server Integration
- [ ] Create a cinematic background container in `index.html`.
- [ ] Update `server.py` to trigger environment generation on location changes.
- [ ] Implement a `scene_update` WebSocket message to push new visuals to the client.
