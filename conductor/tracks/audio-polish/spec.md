# Audio Polish Specification

## Objective
Integrate Piper TTS to generate local character voices, parsing the LLM output to identify speakers and trigger corresponding audio generation.

## Requirements
- Local installation and configuration of Piper TTS.
- A Python module to parse LLM text output (e.g., `[Character]: dialogue`) in real-time.
- Audio generation pipelines mapping specific characters to specific Piper voice models.