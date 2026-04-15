# Cinematic Experience Implementation Plan

## Phase 1: Literary Character Upgrades
- [ ] Add `signature_tic` and `narrative_role` to the `characters` table in `schema.sql` and `db.py`.
- [ ] Update the `add_character` logic to prompt the LLM for a recognizable tic.
- [ ] Update `director.py` to track "turns since last seen" for characters.
- [ ] Add logic: If an old character reappears, inject a Director Instruction: `Re-introduce [Character] using their signature trait: [Tic].`

## Phase 2: Cinematic Audio Layering
- [ ] Update `atmosphere_engine.py` to select layered audio: one base ambiance track, one mood music track.
- [ ] Modify `static/app.js` to support multiple parallel audio elements (Voice, Music, Ambiance).
- [ ] Implement Character Leitmotifs: Assign specific audio tracks or moods to major NPCs and trigger them when they enter a scene.

## Phase 3: Dynamic Visuals (Ken Burns & Impacts)
- [ ] Add CSS animations for the "Ken Burns" effect to `style.css` (slow pan and zoom).
- [ ] Update `static/app.js` to apply the Ken Burns class to `.environment-image` and `.portrait`.
- [ ] Add visual punctuation classes (e.g., `.shake`, `.flash-red`) triggered by combat or high-tension events detected by the Director.