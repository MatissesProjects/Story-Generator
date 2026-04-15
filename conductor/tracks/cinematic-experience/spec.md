# Cinematic Experience Engine Specification

## Objective
Elevate the Story Generator from a text-based game into a dynamic, cinematic experience similar to how professional YouTubers or visual novels present static media, while implementing professional literary techniques for managing sprawling casts of characters.

## 1. The Literary Approach: Deep Character Management
Epic fantasy authors (like George R.R. Martin or Brandon Sanderson) use structural techniques to handle massive casts without confusing the reader. We will implement these mechanically:

*   **Character Anchors / Tags**: In literature, characters are given a specific, recognizable physical or behavioral tic (e.g., "tugs braid", "smells of lilac"). 
    *   *Implementation*: The DB and Vector memory will store a `signature_tic` for each character. When a character hasn't been seen in >10 turns, the LLM will be instructed to reintroduce them *using* their specific anchor, ensuring the reader remembers them instantly.
*   **The "Role" Classification**: Characters aren't just "people," they have narrative roles (Foil, Mentor, Comic Relief). 
    *   *Implementation*: The `social_engine.py` will assign dynamic roles. If the party needs a Foil, the Director will pull a character that fits the Foil archetype from memory.
*   **Decay & Reunion Mechanics**: Characters have a "relevance score." If a character fades from relevance, they aren't deleted—they are archived in ChromaDB. The Director can trigger a "Reunion Event" pulling a low-relevance character back into the spotlight.

## 2. The YouTuber Approach: Cinematic Delivery
Storytellers on YouTube use specific audio-visual techniques to make static images feel like a movie.

*   **The Ken Burns Effect (Dynamic Motion)**: Static images feel dead. Panning and zooming add life.
    *   *Implementation*: Update `static/style.css` and `static/app.js` to apply slow CSS `transform: scale(1.1) translate(X, Y)` animations to environment and portrait images. When a character speaks, their portrait slowly zooms in to simulate a camera pushing in.
*   **Leitmotifs (Character Themes)**: Music should be tied to identity.
    *   *Implementation*: `music_orchestrator.py` can assign specific musical stems or moods to key characters. When the antagonist enters, their specific "theme" plays instead of generic tension music.
*   **Layered Audio Design (The "Room Tone")**: Cinematic audio relies on a foundation of ambiance.
    *   *Implementation*: Enhance `atmosphere_engine.py` to layer audio. Instead of just playing music, the client should play a continuous background ambient loop (e.g., wind, tavern chatter) *underneath* the mood music and TTS.
*   **Visual Punctuation (The Smash Cut)**: YouTubers use sudden cuts or visual changes to emphasize a point.
    *   *Implementation*: Add CSS classes for screen shakes, flashes, or sudden full-screen color tints (e.g., the screen flashes red when damage is taken).

## Strategic Value
By combining deep literary mechanics (anchors, roles) with dynamic cinematic presentation (Ken Burns, layered audio, leitmotifs), the application will feel incredibly polished, memorable, and "alive," transcending standard text generation.