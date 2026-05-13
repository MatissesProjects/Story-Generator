# Plan: Fix Image Display and Story Continuation

## Objective
- Fix images not displaying in "localmode" due to frontend crashes and missing handshake.
- Implement story continuation via a "Continue" button and by allowing empty input in the main text field.

## Key Files & Context
- `static/index.html`: Contains the UI structure.
- `static/app.js`: Handles WebSocket communication and UI updates.
- `static/style.css`: Styles the UI elements.
- `server.py`: The backend WebSocket endpoint that expects a handshake.

## Proposed Changes

### 1. Frontend: UI Enhancements (`static/index.html`)
- Add a "Continue" button next to the "Send" button in the input form.
- Ensure the `visual-stack` is properly utilized.

### 2. Frontend: Logic Fixes (`static/app.js`)
- **Handshake**: Send a `handshake` message immediately after the WebSocket connection is opened. This informs the server of client capabilities and prevents fallback logic issues.
- **Image Display Fix**: 
    - Remove the redundant and non-existent `backgroundVisualEl` reference.
    - Update `scene_update` and `state_update` handlers to use `layers['environment']` (which corresponds to `layer-environment` in the DOM) for background images.
- **Story Continuation**:
    - Remove the `if (!text) return;` check in the form submission handler to allow empty inputs (which the server interprets as a "continue" intent).
    - Add an event listener for the new "Continue" button that sends an empty string or a "continue" message.

### 3. Frontend: Styling (`static/style.css`)
- Add styles for the "Continue" button to ensure it fits the UI theme.

## Verification Plan

### Automated Tests
- N/A (Frontend issues are best verified manually in this context, but I will check if any integration tests are affected).

### Manual Verification
1. **Handshake Verification**:
    - Open the browser and check the "Debug Console" in the UI.
    - Confirm the message "Handshake verified. Orchestrating for Local Browser." appears.
2. **Image Display Verification**:
    - Start a new story or trigger a "Spark".
    - Wait for the first character or location to be mentioned.
    - Verify that the background image and character portraits appear in the `visual-stack`.
    - Check the browser's Network tab to confirm that `/asset/` or `/static/` image requests are being made.
3. **Story Continuation Verification**:
    - After the first segment of the story is generated, press Enter without typing anything.
    - Confirm that the story continues (new text appears).
    - Click the "Continue" button and confirm that the story continues.

## Implementation Details

### `static/index.html`
```html
<form id="input-form">
    <input type="text" id="user-input" placeholder="Type your action or 'continue'..." autocomplete="off">
    <button type="submit">Send</button>
    <button type="button" id="continue-btn" style="background-color: #4ade80; color: #000;">Continue</button>
</form>
```

### `static/app.js`
- Update `socket.onopen` to send `handshake`.
- Replace `backgroundVisualEl` usages with `document.getElementById('layer-environment')`.
- Update `inputForm.onsubmit` to allow empty `text`.
- Add `continueBtn.onclick`.

### `static/style.css`
- Add margins and hover effects for `#continue-btn`.
