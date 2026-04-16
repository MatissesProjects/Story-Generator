# Network Orchestration Implementation Plan

## Phase 1: Handshake Implementation
- [ ] Add `GPU_NAME` and `OFFLOAD_SUPPORT` to `config.py`.
- [ ] Implement `send_handshake` in `client.py` on connection.
- [ ] Implement `handle_handshake` in `server.py` to store client capabilities.

## Phase 2: Distributed Vision (3070 Offloading)
- [ ] Create `vision_client_stub.py` on the Runner/Client side to listen for generation requests.
- [ ] Modify `server.py` to check `client_capabilities` before calling `vision.generate_*`.
- [ ] Implement WebSocket message `vision_request` -> `vision_complete`.

## Phase 3: Memory Hardening
- [x] Add `enable_model_cpu_offload()` and `enable_vae_tiling()` to `vision.py`.
- [ ] Add `torch.cuda.empty_cache()` hooks to heavy generation paths.
- [ ] Implement optional `keep_alive: 0` for Ollama calls in `llm.py` during vision tasks.
