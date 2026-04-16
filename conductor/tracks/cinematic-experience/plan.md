# Cinematic Experience Implementation Plan

## Phase 1: Visual & Audio Polish (The YouTuber Approach)
- [x] Add CSS `@keyframes` for "Ken Burns" (slow pan/zoom) to `static/style.css`.
- [x] Update `static/app.js` to toggle Ken Burns animations on environment and portrait changes.
- [x] Implement **Audio Ducking** in `static/app.js`: Music/Ambiance volume should dip when TTS is playing.
- [x] Add visual punctuation triggers (flash, shake) to the frontend event handler.

## Phase 2: Character Anchors & Depth (The Literary Approach)
- [x] Add `signature_tic`, `narrative_role`, and `last_seen_turn` to `characters` table in `schema.sql`.
- [x] Update `db.py` character methods to handle these new fields.
- [x] Update `director.py` prompt logic to enforce character tics and detect "relevance decay."
- [x] Implement "Reunion Event" logic in `social_engine.py` when a decayed character returns.

## Phase 3: Leitmotifs & Advanced Mixing
- [ ] Add a `leitmotif_path` to the `characters` table in `db.py`.
- [ ] Update `music_orchestrator.py` to allow character-specific theme overrides.
- [ ] Update `static/app.js` to handle cross-fading between generic mood music and character leitmotifs.
