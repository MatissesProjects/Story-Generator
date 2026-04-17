# 🎬 Track: Cinematic Experience V2

## Overview
Transform the Story Generator into a professional-grade Visual Novel and Cinematic experience. This version focuses on high-fidelity visual staging, on-demand asset requests, and a reactive, narrative-driven UI.

## Core Objectives
- **Layered Staging UI**: Move beyond a simple background to a 3-layer VN setup:
  - **Backdrop**: Dynamic environment (with Ken Burns effect).
  - **Middle**: 3 Character Slots (Left, Center, Right) for active NPCs.
  - **Front**: Dialogue Box, UI Overlays, and VJ Textures.
- **On-Demand Asset Pipeline**:
  - Implement a `GET /asset/{type}/{name}` endpoint.
  - If an image doesn't exist, the server triggers `vision.py` to generate it immediately and returns it.
- **Cinematic Camera System**:
  - Automated "Camera Cues" (Zoom, Pan, Shake) sent via WebSocket.
- **Character Staging Logic**:
  - The `VisualCurator` decides which characters are "on stage" and in which slots based on the dialogue.
- **Reactive UI**:
  - Dialogue boxes that change style based on the speaker's mood or traits.

## Functional Requirements
1. **The Staging Engine**: `visual_curator.py` expansion to handle character slots.
2. **Asset Request Middleware**: Logic in `server.py` to intercept missing asset requests.
3. **Frontend V2**: Overhaul `app.js` and `index.html` to support the 3-layer slot system.

## Dependencies
- `vision.py`: For real-time generation.
- `atmosphere_engine.py`: For environmental cues.
- `server.py`: For asset serving and generation coordination.
