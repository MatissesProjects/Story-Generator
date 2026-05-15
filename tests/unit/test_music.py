import pytest
import music_orchestrator
import db
import llm
import os
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_detect_mood_success():
    mo = music_orchestrator.MusicOrchestrator()
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Combat"
        mood = await mo.detect_mood("Swords clashing!")
        assert mood == "Combat"

@pytest.mark.asyncio
async def test_detect_mood_error():
    mo = music_orchestrator.MusicOrchestrator()
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        mood = await mo.detect_mood("Text")
        assert mood == "Suspense" # Default fallback

def test_select_track_exact_match():
    mo = music_orchestrator.MusicOrchestrator()
    # Mock some tracks in mo.tracks
    mo.tracks = [{"filename": "battle.wav", "mood": "Combat", "intensity": 5}]
    
    track = mo.select_track("Combat")
    assert track['filename'] == "battle.wav"

def test_select_track_partial_match():
    mo = music_orchestrator.MusicOrchestrator()
    mo.tracks = [{"filename": "creepy.wav", "mood": "Horror", "intensity": 3}]
    
    # "Spooky" should match "Horror" if we implement mapping? 
    # Current implementation uses 'if mood in track['mood']'
    track = mo.select_track("Horror")
    assert track['filename'] == "creepy.wav"

def test_select_track_none():
    mo = music_orchestrator.MusicOrchestrator()
    mo.tracks = []
    assert mo.select_track("Any") is None

def test_get_ambiance_filename():
    mo = music_orchestrator.MusicOrchestrator()
    assert "rain" in mo.get_ambiance_filename("heavy rain")
    assert mo.get_ambiance_filename("silence") is None
    assert mo.get_ambiance_filename("unknown") is None
