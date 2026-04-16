import pytest
import db
from world_engine import WorldEngine

@pytest.mark.asyncio
async def test_coordinate_collision(mock_llm):
    """
    ADVERSARIAL: Verify if the system allows two distinct locations at the same (x, y).
    """
    engine = WorldEngine()
    
    # 1. Create first location
    db.add_location("Town Square", "The heart of the city", 0, 0, "urban")
    
    # 2. Attempt to create another location at the same coordinates
    # This might happen if the LLM isn't aware of existing geometry
    db.add_location("Secret Basement", "Hidden under the square", 0, 0, "dungeon")
    
    locations = db.get_all_locations()
    # If the system doesn't prevent this, we'll have two locations at (0, 0)
    # This is a 'weakness' in the current spatial integrity
    coords = [(l['x'], l['y']) for l in locations]
    assert len(coords) == len(set(coords)), "BUG CONFIRMED: Spatial collision! Two locations at (0, 0)"

@pytest.mark.asyncio
async def test_orphaned_relative_location(mock_llm):
    """
    ADVERSARIAL: Verify what happens when placing a location relative to a non-existent anchor.
    """
    engine = WorldEngine()
    
    # 1. Start with an empty world
    # 2. Try to resolve a location relative to something that doesn't exist
    # Current behavior: should default to (0,0) or some anchor
    await engine.resolve_new_location(
        "Ghost Town", 
        "A town that shouldn't be here", 
        relative_to_name="NonExistentCity", 
        direction="north"
    )
    
    ghost = db.get_location_by_name("Ghost Town")
    assert ghost is not None
    assert ghost['x'] == 0 and ghost['y'] == 0, "Should default to origin if anchor is missing"
