import pytest
import os
import visual_curator
import config

def test_visual_stack_generation():
    curator = visual_curator.VisualCurator()
    
    # Mock some existing environment and portrait paths if they don't exist
    # (In a real test we might want to create temp files)
    
    atmosphere = {"weather": "Heavy Rain"}
    involved = ["Malakar"]
    location = "The Neon City"
    
    # We can't easily test file existence without real files, 
    # but we can test the logic for textures and overlays.
    
    stack = curator.get_visual_stack(location, involved, atmosphere)
    
    # Test Texture selection logic
    assert stack['texture'] == curator.textures["Cyberpunk"]
    
    # Test Overlay selection logic
    assert stack['overlay'] == curator.overlays["Rain"]

def test_visual_stack_fallback():
    curator = visual_curator.VisualCurator()
    stack = curator.get_visual_stack("Unknown Wilderness", [], {"weather": "Clear"})
    
    assert stack['texture'] == curator.textures["Default"]
    assert stack['overlay'] is None
    assert stack['entity'] is None
