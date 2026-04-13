# Audio Polish Plan

## Objective
Implement local Text-to-Speech using Piper.

## Implementation Steps
1.  **Piper Setup**: Download and configure the Piper TTS binary and a set of distinct voice models.
2.  **Parser**: Create a parser in `main.py` or a new `parser.py` module to identify the speaker in the LLM's text stream.
3.  **TTS Integration**: Write a `tts.py` module that takes the parsed text and speaker ID, calls the Piper executable via `subprocess` (or Python bindings if available), and generates an audio file.
4.  **Playback**: Implement a simple playback queue to play the generated audio files sequentially.

## Verification
- Verify the parser correctly identifies different speakers in a dialogue.
- Test that Piper generates distinct, correct audio for each speaker line.