# Plan: Fix UI Collapse and Voice Fallbacks

## Objective
- Fix the UI collapse caused by the `join-overlay` pushing the layout down, restoring visibility of the `input-form`.
- Ensure characters never use the Narrator's voice by excluding it from random assignment and fallback logic.
- Ensure background images render correctly.

## Key Files & Context
- `static/style.css`: Contains the `#join-overlay` definition which seems to be behaving as `position: static` instead of `fixed`.
- `config.py`: Contains voice lists where `NARRATOR_VOICE` might overlap with character voices.
- `db.py`: Contains the `add_character` and `get_character_voice` logic where voices are assigned and fallbacks occur.

## Proposed Changes

### 1. CSS Fix (`static/style.css`)
- **Overlay Position**: Move the `#join-overlay` CSS to the top of the file to ensure it's not affected by any potential unclosed blocks above it. Force it to be `position: fixed !important;`.
- **Hiding Logic**: Add a `.hidden` class to properly hide the overlay completely (`display: none`) instead of just relying on `visibility: hidden` which might still take up space in some edge cases.

### 2. JS Fix (`static/app.js`)
- Update the `joinBtn.onclick` to completely remove or set `display: none` on the `join-overlay` after the transition to guarantee it stops affecting layout.

### 3. Voice Logic (`config.py` & `db.py`)
- **Config**: Ensure `NARRATOR_VOICE` is explicitly separated from `MALE_VOICES` or `FEMALE_VOICES` so random assignment never picks it for a character.
- **Database Assignment**: In `add_character`, if a random voice is picked, explicitly filter out `config.NARRATOR_VOICE`.
- **Database Fallback**: In `get_character_voice`, if a character is truly not found, assign them a random voice from the non-narrator lists instead of the narrator voice.

## Verification Plan

### Manual Verification
1. **UI Check**: Load the application. Verify the "Join Adventure" screen covers the whole viewport. Click it. Verify it disappears completely and the main UI is visible, including the input box at the bottom.
2. **Voice Check**: Trigger a spark or new character. Check the server logs to ensure the assigned voice is NOT the narrator voice (`en_US-ryan-high.onnx`). Verify that the narrator uses its designated voice without fallback warnings.

## Implementation Details

### `config.py` (Example Check)
Ensure `en_US-ryan-high.onnx` is not in `MALE_VOICES` if it's the narrator.

### `static/style.css`
```css
#join-overlay {
    position: fixed !important;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    display: flex;
    /* ... */
}
```

### `static/app.js`
```javascript
        joinOverlay.style.opacity = '0';
        setTimeout(() => {
            joinOverlay.style.display = 'none'; // Use display none to remove from flow completely
            console.log("Overlay hidden");
        }, 1000);
```