import pytest
import db
from world_engine import WorldEngine

@pytest.mark.asyncio
async def test_coordinate_collision(mock_llm):
    """
    ADVERSARIAL: Verify if the system prevents two distinct locations at the same (x, y).
    """
    # 1. Create first location
    id1 = db.add_location("Town Square", "The heart of the city", 0, 0, "urban")
    assert id1 is not None
    
    # 2. Attempt to create another location at the same coordinates
    # DB should now block this via UNIQUE constraint
    id2 = db.add_location("Secret Basement", "Hidden under the square", 0, 0, "dungeon")
    
    assert id2 is None, "BUG CONFIRMED: Spatial collision! db.add_location allowed duplicate coords."

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
