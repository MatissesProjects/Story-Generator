import pytest
import director
import db
import llm
import json
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

def test_evaluate_state_sync():
    # Setup DB state
    db.add_plot_thread("Find the sword")
    db.add_quest("Main Quest", "Description", 5)
    db.execute_db("INSERT INTO simulation_history (tick_number, event_type, description) VALUES (1, 'NPC', 'Zork moved')")
    
    instruction = director.evaluate_state("I walk", recent_history=[])
    assert "Find the sword" in instruction
    assert "Main Quest" in instruction
    assert "Zork moved" in instruction
    assert "PROACTIVE" in instruction

@pytest.mark.asyncio
async def test_evaluate_quest_progress():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"updates": [{"objective_id": 1, "status": "completed"}]}'
        
        # Setup quest and objective
        qid = db.add_quest("Q", "D", 1)
        oid = db.add_quest_objective(qid, "O")
        
        # We need to make sure the mocked ID matches or just check the list length
        updates = await director.evaluate_quest_progress("I did the thing")
        assert len(updates) == 1
        assert updates[0]['status'] == "completed"

@pytest.mark.asyncio
async def test_evaluate_milestone_progress():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"completed": true}'
        
        # Mock DB get_active_arc
        with patch("db.get_active_arc", return_value={"milestones": [{"name": "M1", "description": "D", "completion_criteria": "C"}]}), \
             patch("db.get_current_milestone_index", return_value=0):
            
            completed = await director.evaluate_milestone_progress("History")
            assert completed is True

def test_get_persona_blocks():
    db.add_character("Elara", "Warrior", "Brave")
    db.update_character_last_seen(1, 0) # Elara id 1
    
    blocks = director.get_persona_blocks("I talk to Elara", current_turn=1)
    assert len(blocks) == 1
    assert "Elara" in blocks[0]
    assert "Warrior" in blocks[0]

@pytest.mark.asyncio
async def test_check_narrative_gaps():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"needs_research": true, "suggested_theme": "caves"}'
        
        needs, theme = await director.check_narrative_gaps([], [])
        assert needs is True
        assert theme == "caves"

@pytest.mark.asyncio
async def test_identify_location():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"location": "Dark Cave", "description": "Spooky", "relative_to": "Field", "direction": "north"}'
        
        loc, desc, rel, dir = await director.identify_location("I enter the cave", [], current_location="Field")
        assert loc == "Dark Cave"
        assert dir == "north"

@pytest.mark.asyncio
async def test_generate_creative_name():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Xyloth-Ra"
        
        name = await director.generate_creative_name("character", "Context")
        assert name == "Xyloth-Ra"

@pytest.mark.asyncio
async def test_generate_action_plan():
    # Mock all the sub-calls
    with patch("director.check_narrative_gaps", new_callable=AsyncMock) as m1, \
         patch("director.evaluate_quest_progress", new_callable=AsyncMock) as m2, \
         patch("director.evaluate_milestone_progress", new_callable=AsyncMock) as m3, \
         patch("director.identify_location", new_callable=AsyncMock) as m4:
         
         m1.return_value = (True, "theme")
         m2.return_value = [{"obj_id": 1}]
         m3.return_value = True
         m4.return_value = ("Loc", "Desc", "Rel", "Dir")
         
         plan = await director.generate_action_plan("input", [], [], [])
         assert plan['needs_research'] is True
         assert plan['quest_updates'] == [{"obj_id": 1}]
         assert plan['new_location']['name'] == "Loc"

@pytest.mark.asyncio
async def test_generate_initiative():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "A dragon lands!"
        
        event = await director.generate_initiative([], [])
        assert "dragon" in event

@pytest.mark.asyncio
async def test_generate_character_tic():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Clicks tongue."
        
        tic = await director.generate_character_tic("Name", "Desc", "Traits")
        assert tic == "Clicks tongue."

def test_evaluate_state_empty():
    instruction = director.evaluate_state("Action", recent_history=[])
    assert "No specific plot threads active" in instruction

def test_get_persona_blocks_reunion():
    db.add_character("Elara", "Warrior", "Brave")
    db.update_character_last_seen(1, 0)
    # Turn 20, last seen 0 -> Diff 20 > 15
    blocks = director.get_persona_blocks("Elara", current_turn=20)
    assert "REUNION EVENT" in blocks[0]

@pytest.mark.asyncio
async def test_evaluate_quest_progress_no_quests():
    # Clear quests
    db.execute_db("DELETE FROM quest_objectives")
    db.execute_db("DELETE FROM quests")
    res = await director.evaluate_quest_progress("H")
    assert res == []

@pytest.mark.asyncio
async def test_evaluate_quest_progress_error():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        db.add_quest("Q", "D", 1)
        res = await director.evaluate_quest_progress("History")
        assert res == []

@pytest.mark.asyncio
async def test_evaluate_milestone_progress_error():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        with patch("db.get_active_arc", return_value={"milestones": [{"name": "M1", "description": "D", "completion_criteria": "C"}]}), \
             patch("db.get_current_milestone_index", return_value=0):
            res = await director.evaluate_milestone_progress("History")
            assert res is False

@pytest.mark.asyncio
async def test_check_narrative_gaps_error():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        res, theme = await director.check_narrative_gaps([], [])
        assert res is False

@pytest.mark.asyncio
async def test_identify_location_error():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        res = await director.identify_location("in", [])
        assert res == (None, None, None, None)

@pytest.mark.asyncio
async def test_generate_creative_name_error():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        res = await director.generate_creative_name("cat", "ctx")
        assert "Unknown" in res

@pytest.mark.asyncio
async def test_generate_initiative_error():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        res = await director.generate_initiative([], [])
        assert res == ""

@pytest.mark.asyncio
async def test_generate_character_tic_error():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        res = await director.generate_character_tic("n", "d", "t")
        assert "watching" in res

@pytest.mark.asyncio
async def test_analyze_plot_threads():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"resolved_ids": [1], "new_threads": ["T2"]}'
        
        res = await director.analyze_plot_threads([], [])
        assert 1 in res['resolved_ids']
        assert "T2" in res['new_threads']

@pytest.mark.asyncio
async def test_analyze_plot_threads_error():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        res = await director.analyze_plot_threads([], [])
        assert res == {"resolved_ids": [], "new_threads": []}

@pytest.mark.asyncio
async def test_evaluate_milestone_progress_edge_cases():
    # No arc
    with patch("db.get_active_arc", return_value=None):
        assert await director.evaluate_milestone_progress("H") is False
    
    # Invalid index
    with patch("db.get_active_arc", return_value={"milestones": []}), \
         patch("db.get_current_milestone_index", return_value=99):
        assert await director.evaluate_milestone_progress("H") is False
