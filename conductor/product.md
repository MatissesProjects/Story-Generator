# Product Definition: Story Generator

## Vision
A completely local, multi-PC story generation tool that co-writes interactive fiction. It leverages a local LLM (Ollama) to generate narratives, maintaining persistent world states and character voices using local TTS.

## Key Features
- **Local Generation**: Uses Ollama for LLM inference, ensuring privacy and offline capability.
- **Persistent Memory**: SQLite database stores character sheets, world lore, and plot timelines, preventing the LLM from forgetting crucial facts.
- **Context Management**: Dynamically filters and injects only relevant lore/history into the prompt, avoiding massive context windows.
- **Character Voices**: Uses Piper TTS to generate distinct, localized voice audio for different characters.
- **Multi-PC Architecture**: A WebSocket-based push architecture allows a "Generator PC" to do the heavy lifting while streaming text and triggering audio on a "Player PC".
- **Spark Generator**: Helps kickstart narratives even without an initial user idea by generating story prompts or world seeds.