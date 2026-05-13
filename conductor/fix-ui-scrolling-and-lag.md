# Plan: Fix UI Scrolling and Optimize TTS/Discovery Lag

## Objective
- Ensure the text currently being read is scrolled into view in both the history and the dialogue box.
- Remove narrative flow lag caused by blocking TTS generation and character discovery tasks.
- Improve the "hiding" of image creation by ensuring intensive tasks don't block the main event loop.

## Key Files & Context
- `static/app.js`: Handles UI scrolling logic.
- `server.py`: The main loop where text is streamed and TTS/Discovery is triggered.
- `social_engine.py`: Handles character registration, which involves slow LLM calls.
- `tts.py`: Handles audio generation, which is a CPU/GPU intensive synchronous task.

## Proposed Changes

### 1. Frontend: Scrolling Sync (`static/app.js`)
- Update `scrollStory()` to scroll both `#history-container` and `#vn-dialogue-box`.
- Ensure `scrollStory()` is called more frequently or specifically during audio events.

### 2. Backend: De-blocking the Main Loop (`server.py`)
- **Non-blocking Character Discovery**: Use `asyncio.create_task` for aggressive character discovery scanning during the story generation stream.
- **Asynchronous TTS Generation**: Wrap the synchronous `tts.generate_audio()` call in `asyncio.to_thread()` to prevent it from blocking the websocket text stream.
- **Deduplication**: Use a set in `social_engine.py` to track characters currently being registered to avoid redundant LLM tasks for the same character name within a single story segment.

### 3. Backend: Image Creation Optimization (`social_engine.py`)
- Ensure that the "pre-registration" (database entry without description/portrait) is done immediately, while the slow "refinement" (LLM description + Portrait generation) is done in the background.

### 4. Parser: Tightening Name Detection (`parser.py` & `social_engine.py`)
- **Limit Name Complexity**: Update regex in `parser.py` to be less "greedy" with spaces and limit the total length of a detected "name" (e.g., max 30 characters or 4 words).
- **Validation**: Add a check in `social_engine.discover_new_characters` to ignore names that look like full sentences or image prompts.
- **Narrator Protection**: Ensure that if a line starts with `[` and ends with `]:`, it's strictly validated against a whitelist or length limit.

## Verification Plan

### Manual Verification
1. **UI Check**: Verify scrolling sync in both history and dialogue box.
2. **Parser Check**: Verify that strings like "[A mysterious shadow falls over the valley]: ..." are processed as Narrator text, not as a character named "A mysterious shadow falls over the valley".
3. **Lag Check**: Ensure smooth flow during character introductions.
