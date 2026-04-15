# 🗺️ Implementation Plan: VJ Visual Curation

## Phase 1: Frontend Layering 🏗️
- [ ] Update `index.html` and `style.css` to support multiple visual layers with blending modes.
- [ ] Implement `updateVisualStack(layers)` in `app.js`.

## Phase 2: Visual Curator Module 🎨
- [ ] Create `visual_curator.py`.
- [ ] Implement asset selection logic based on `current_location` and `active_entities`.
- [ ] Define "Mood Overlays" (e.g., scanlines for tech, grunge for dark fantasy).

## Phase 3: Atmosphere Integration ⚡
- [ ] Link `atmosphere_engine.py` cues to visual layer effects (e.g., a "Rumble" cue triggers a specific glitch layer).
- [ ] Implement "Visual Beats": Minor shifts in texture/blending on every tick or turn.

## Phase 4: Library Expansion 📚
- [ ] Add a way to register pre-existing "Visual Packs" (folders of textures/backgrounds).
- [ ] Update `vision.py` to optionally generate "Visual Overlays" or "Alpha-channel Portraits".

## Phase 5: Verification 🧪
- [ ] Create `test_visual_curator.py`.
- [ ] Ensure smooth transitions between layered states.
