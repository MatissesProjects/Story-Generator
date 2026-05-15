import pytest
import asyncio
import os
import db
import curator
import director
import llm
import json
from unittest.mock import AsyncMock, patch

def test_db_basic_ops():
    # Test character adding/retrieval
    with patch('memory_engine.add_character_vector'):
        db.add_character("TestChar", "Test Desc", "Trait1")
    
    char = db.search_characters("TestChar")
    assert len(char) == 1
    assert char[0]['name'] == "TestChar"
    
    # Test story state
    db.set_story_state("test_key", "test_value")
    assert db.get_story_state("test_key") == "test_value"

def test_db_inventory_stats():
    db.add_inventory_item("player", 0, "Silver Sword", "Shiny", 1)
    inv = db.get_inventory("player", 0)
    assert len(inv) == 1
    assert inv[0]['item_name'] == "Silver Sword"
    
    db.set_entity_stat("player", 0, "Strength", 10)
    stats = db.get_entity_stats("player", 0)
    assert len(stats) == 1
    assert stats[0]['stat_value'] == "10"

@pytest.mark.asyncio
async def test_curator_context():
    db.add_character("Malakar", "Assassin", "Dark")
    db.add_lore("The Void", "Dark realm")
    
    with patch('memory_engine.search_semantic_with_scores', return_value=[]):
        facts = curator.get_relevant_context("Malakar entered the Void")
        assert any("CHARACTER: Malakar" in f for f in facts)
        assert any("LORE: The Void" in f for f in facts)

@pytest.mark.asyncio
async def test_director_plan():
    # Mock LLM calls with side effects based on prompt content
    async def llm_side_effect(prompt, model=None, **kwargs):
        if "Scene Parser" in prompt:
            return json.dumps({"location": "The Cave", "description": "Dark", "relative_to": None, "direction": None})
        if "Narrative Architect" in prompt:
            return json.dumps({"needs_research": False, "suggested_theme": ""})
        if "Quest Arbiter" in prompt:
            return json.dumps({"updates": []})
        if "Narrative Milestone Arbiter" in prompt:
            return json.dumps({"completed": False})
        return "{}"

    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = llm_side_effect
        
        plan = await director.generate_action_plan("I go to the cave", [], [], [])
        assert plan['new_location'] is not None
        assert plan['new_location']['name'] == "The Cave"

@pytest.mark.asyncio
async def test_llm_async_generation():
    # Test the prompt builder
    prompt = llm._build_full_prompt("Hello", narrative_seed="Once upon a time")
    assert "STORY SO FAR" in prompt
    assert "Once upon a time" in prompt
    
    # Mock httpx for async_generate_story_segment
    # This is a bit complex due to stream, so we'll mock the high level utility
    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "This is a story."
        resp = await llm.async_generate_full_response("Write a story")
        assert resp == "This is a story."

def test_db_quest_system():
    quest_id = db.add_quest("Test Quest", "Description", 5)
    db.add_quest_objective(quest_id, "Objective 1")
    
    active = db.get_active_quests()
    assert len(active) == 1
    assert active[0]['title'] == "Test Quest"
    assert len(active[0]['objectives']) == 1
    
    db.update_objective_status(active[0]['objectives'][0]['id'], 'completed')
    active_updated = db.get_active_quests()
    assert len(active_updated[0]['objectives']) == 0 # Objectives filtered by active status
