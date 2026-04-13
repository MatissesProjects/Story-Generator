# Product Guidelines

## Non-Negotiables
- **100% Local Processing**: No external API calls to proprietary cloud LLMs. The data stays on the local network.
- **Privacy and Control**: Full control over character voices and world lore.
- **Resource Efficiency**: Use RAG-like context filtering to avoid sending the entire story history to Ollama on every turn.
- **Robustness**: Implement fallback mechanisms if TTS fails, ensuring the text stream continues uninterrupted.

## Code Quality
- Follow standard Python styling (PEP 8).
- Keep modules clean and independent.
- Document database schemas and API endpoints.