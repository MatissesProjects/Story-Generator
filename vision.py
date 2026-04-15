import torch
from diffusers import AutoPipelineForText2Image
import config
import os
from PIL import Image
import llm

# Initialize the pipeline
# We'll use SDXL Turbo for speed, or falling back to CPU if no GPU is found
device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if device == "cuda" else torch.float32

print(f"Vision Engine: Initializing model {config.VISION_MODEL} on {device}...")
pipe = AutoPipelineForText2Image.from_pretrained(
    config.VISION_MODEL, 
    torch_dtype=torch_dtype, 
    variant="fp16" if device == "cuda" else None
)
pipe.to(device)

if not os.path.exists(config.PORTRAITS_DIR):
    os.makedirs(config.PORTRAITS_DIR)

if not os.path.exists(config.ENVIRONMENTS_DIR):
    os.makedirs(config.ENVIRONMENTS_DIR)

if not os.path.exists(config.MAP_TILES_DIR):
    os.makedirs(config.MAP_TILES_DIR)

async def stylize_prompt(character_name, description, traits):
    """
    Uses the LLM to turn raw character details into a high-quality SD prompt.
    """
    prompt = f"""
[SYSTEM: You are an expert AI Art Prompt Engineer. Your goal is to take character details and turn them into a high-quality, professional digital art portrait prompt for Stable Diffusion.

CHARACTER: {character_name}
DESCRIPTION: {description}
TRAITS: {traits}

FORMAT: Provide a single comma-separated list of descriptive keywords. Focus on: lighting, art style (e.g., hyperrealistic digital painting), specific clothing, facial features, and a clear background.
Avoid: "and", "the", "a", complete sentences.

Example: "Hyperrealistic digital portrait, battle-worn knight, scarred face, glowing blue eyes, ornate silver armor, dark forest background, cinematic lighting, 8k resolution"

Provide ONLY the prompt string.]
"""
    return await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)

async def generate_portrait(name, description, traits):
    """
    Generates a portrait for a character and saves it to the static directory.
    Returns the URL path of the generated image.
    """
    safe_name = "".join([c for c in name if c.isalnum()]).lower()
    output_path = os.path.join(config.PORTRAITS_DIR, f"{safe_name}.png")
    
    # Check if we already have it
    if os.path.exists(output_path):
        return f"/static/portraits/{safe_name}.png"

    print(f"Vision Engine: Generating portrait for {name}...")
    
    # Get a good prompt
    final_prompt = await stylize_prompt(name, description, traits)
    print(f"Vision Engine: Final Prompt: {final_prompt}")
    
    # Generate
    # SDXL Turbo is best at 1-4 steps
    image = pipe(prompt=final_prompt, num_inference_steps=4, guidance_scale=0.0).images[0]
    
    # Save
    image.save(output_path)
    print(f"Vision Engine: Saved portrait to {output_path}")
    
    return f"/static/portraits/{safe_name}.png"

async def stylize_environment_prompt(location_name, description):
    """
    Uses the LLM to turn location details into a high-quality SD prompt.
    """
    prompt = f"""
[SYSTEM: You are an expert AI Art Prompt Engineer. Your goal is to take location details and turn them into a high-quality, professional digital art landscape prompt for Stable Diffusion.

LOCATION: {location_name}
DESCRIPTION: {description}

FORMAT: Provide a single comma-separated list of descriptive keywords. Focus on: lighting, atmosphere, art style (e.g., epic concept art, digital landscape painting), specific architectural or natural features, and a sense of scale.
Avoid: "and", "the", "a", complete sentences.

Example: "Epic concept art, ancient stone ruins, overgrown with glowing vines, massive mountain range in background, sunset lighting, mystical atmosphere, 8k resolution, cinematic"

Provide ONLY the prompt string.]
"""
    return await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)

async def generate_environment(location_name, description):
    """
    Generates an environment image and saves it to the static directory.
    Returns the URL path.
    """
    safe_name = "".join([c for c in location_name if c.isalnum()]).lower()
    output_path = os.path.join(config.ENVIRONMENTS_DIR, f"{safe_name}.png")
    
    # Check if we already have it
    if os.path.exists(output_path):
        return f"/static/environments/{safe_name}.png"

    print(f"Vision Engine: Generating environment for {location_name}...")
    
    final_prompt = await stylize_environment_prompt(location_name, description)
    print(f"Vision Engine: Final Environment Prompt: {final_prompt}")
    
    # Generate (landscape-ish if possible, though SDXL Turbo likes 512x512 or 1024x1024)
    # We'll stick to default for now to ensure speed and quality
    image = pipe(prompt=final_prompt, num_inference_steps=4, guidance_scale=0.0).images[0]
    
    image.save(output_path)
    print(f"Vision Engine: Saved environment to {output_path}")
    
    return f"/static/environments/{safe_name}.png"

async def stylize_map_tile_prompt(biome_type):
    """
    Uses the LLM to turn a biome type into a high-quality SD map tile prompt.
    """
    prompt = f"""
[SYSTEM: You are an expert AI Art Prompt Engineer. Your goal is to create a prompt for a top-down, square "Map Tile" visual.

BIOME: {biome_type}

FORMAT: Provide a single comma-separated list of descriptive keywords. Focus on: top-down perspective, cartography style, vibrant colors, clear natural features (e.g., specific trees for forest, rocky peaks for mountains), and a clean square composition.
Avoid: "and", "the", "a", complete sentences.

Example: "Top-down cartography map tile, lush temperate forest, dense green canopy, winding dirt path, vibrant textures, hand-painted digital art style, clean edges, high detail"

Provide ONLY the prompt string.]
"""
    return await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)

async def generate_map_tile(biome_type):
    """
    Generates a map tile image and saves it to the static directory.
    Returns the URL path.
    """
    safe_name = "".join([c for c in biome_type if c.isalnum()]).lower()
    output_path = os.path.join(config.MAP_TILES_DIR, f"{safe_name}_tile.png")
    
    # Check if we already have it
    if os.path.exists(output_path):
        return f"/static/map_tiles/{safe_name}_tile.png"

    print(f"Vision Engine: Generating map tile for {biome_type}...")
    
    final_prompt = await stylize_map_tile_prompt(biome_type)
    print(f"Vision Engine: Final Tile Prompt: {final_prompt}")
    
    # Generate
    image = pipe(prompt=final_prompt, num_inference_steps=4, guidance_scale=0.0).images[0]
    
    image.save(output_path)
    print(f"Vision Engine: Saved map tile to {output_path}")
    
    return f"/static/map_tiles/{safe_name}_tile.png"

if __name__ == "__main__":
    # Test
    print("Testing Vision Engine...")
    test_portrait = generate_portrait("Malakar", "A shadowy assassin in a dark cloak", "Swift, Ruthless, Glowing Eyes")
    print(f"Portrait generated at: {test_portrait}")
    
    test_env = generate_environment("The Whispering Woods", "A forest where the trees share secrets of the ancient kings. It is known for its eerie, rustling sounds.")
    print(f"Environment generated at: {test_env}")
