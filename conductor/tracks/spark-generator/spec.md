# Spark Generator Specification

## Objective
Provide a mechanism to generate story prompts, world seeds, or character concepts when the user doesn't have an initial idea, ensuring the project can "help tell stories" independently.

## Requirements
- A module that requests Ollama to generate a random genre, setting, or conflict.
- Options to randomize or specify parameters (e.g., "Give me a Sci-Fi seed").
- Output should be easily ingestible into the `Core Engine` to start a new story session.