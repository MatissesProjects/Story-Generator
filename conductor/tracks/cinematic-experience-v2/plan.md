# 🗺️ Implementation Plan: Cinematic Experience V2

## Phase 1: On-Demand Assets 🖼️
- [ ] Create `GET /asset/{type}/{name}` endpoint in `server.py`.
- [ ] If asset is missing, trigger async generation in `vision.py`.
- [ ] Update frontend to use these URLs instead of hardcoded paths.

## Phase 2: Layered Staging UI (The VN Setup) 🎭
- [ ] Update `index.html` with Slots: `slot-left`, `slot-center`, `slot-right`.
- [ ] Implement slot-aware rendering in `app.js`.
- [ ] Update `visual_curator.py` to assign characters to slots based on dialogue frequency.

## Phase 3: Camera & Transitions 🎥
- [ ] Add `camera_update` WebSocket message.
- [ ] Implement Ken Burns (zoom/pan) as a CSS class that can be targeted.
- [ ] Add "Visual Novel" dialogue box (centered at bottom, name tag).

## Phase 4: Reactive UI & Mood 🎨
- [ ] Dialogue box style shifts based on mood detected by `atmosphere_engine`.
- [ ] Implement "Visual Beats": Screen glitches on high-tension turns.

## Phase 5: Verification 🧪
- [ ] Test the "Request if not there" logic by deleting an asset and seeing if it regenerates.
- [ ] Verify slot positioning and transitions.
