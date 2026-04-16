# Network Orchestration Specification

## Objective
Enable a distributed multi-PC architecture where a high-end "Generator" (e.g., 4090) and a secondary "Runner" (e.g., 3070) coordinate to balance VRAM usage and prevent OOM errors.

## 1. Handshake Protocol
When the `client.py` connects to `server.py`, it will send a `client_handshake` message containing its hardware capabilities.
- **Capabilities**: GPU model, VRAM capacity, Local AI Support (TTS/Vision/LLM).
- **Server Response**: The server acknowledges and decides which tasks (if any) to offload to the client.

## 2. Distributed Task Allocation
- **Heavy LLM (26b)**: Always stays on the 4090 (Generator).
- **Vision (SDXL)**: Can be offloaded to the 3070 (Runner) if the Generator is at high VRAM pressure.
- **TTS (Piper)**: Highly efficient, can run on either, but offloading to Runner reduces CPU/IO load on the Generator.

## 3. Dynamic Memory Management
- **Keep-Alive Management**: The server can instruct Ollama to unload models (`keep_alive: 0`) if an image generation task is about to start.
- **Explicit Cache Clearing**: Integration of `torch.cuda.empty_cache()` before and after heavy vision tasks.

## 4. Offloading Flow
1. Server receives user input.
2. Server determines if offloading is active for the current client.
3. If offloading Vision: Server sends a `generate_vision_request` to the client.
4. Client generates the image locally using its 3070 and notifies the server when complete.
