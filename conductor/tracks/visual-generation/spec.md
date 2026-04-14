# Visual Generation Specification

## Objective
Enable the story engine to generate and display visual portraits for characters. This brings the narrative to life by providing a face to the names and descriptions stored in the database.

## Requirements
- **Local Image Engine**: Integrate a local image generation tool. 
    - *Option A*: **Stable Diffusion** via a local API (e.g., AUTOMATIC1111 or ComfyUI).
    - *Option B*: A lightweight Python library like `diffusers` (if hardware allows).
- **Portrait Generation Pipeline**:
    1. Extract character physical descriptions from the `Characters` table.
    2. Use an LLM-powered "Prompt Stylizer" to convert raw descriptions into high-quality Stable Diffusion prompts.
    3. Generate the image and save it to a `static/portraits/` directory.
- **Frontend Integration**:
    - Update the character sidebar to display the generated portrait next to the name.
    - Implement a "Generate Portrait" button for existing characters.
- **Dynamic Scene Visualization (Future)**: Optionally generate landscapes or item visuals based on story events.

## Strategic Value
Visuals significantly increase immersion. By generating unique portraits for every character (including those found via Autonomous Research), the world feels truly unique and "persistent."
