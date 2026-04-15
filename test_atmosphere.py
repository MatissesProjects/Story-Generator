import pytest
import asyncio
import json
import atmosphere_engine
import llm
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_atmosphere_detection():
    # Mock LLM for atmosphere detection
    mock_atmos_resp = json.dumps({
        "lighting": "flickering_torchlight",
        "weather": "misty",
        "haptic": "low_rumble",
        "tint": "rgba(255, 100, 0, 0.1)",
        "ambiance": "wind_howl"
    })
    
    engine = atmosphere_engine.AtmosphereEngine()
    with patch('llm.async_generate_full_response', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_atmos_resp
        
        atmos = await engine.detect_atmosphere("The cave was dark and cold.", "Ancient Ruins")
        assert atmos['lighting'] == "flickering_torchlight"
        assert atmos['weather'] == "misty"
        assert atmos['tint'] == "rgba(255, 100, 0, 0.1)"

def test_atmosphere_css_helper():
    engine = atmosphere_engine.AtmosphereEngine()
    atmos = {"tint": "rgba(255, 0, 0, 0.5)"}
    css = engine.get_atmosphere_style_css(atmos)
    assert "background-color: rgba(255, 0, 0, 0.5)" in css

def test_ambiance_mapping():
    engine = atmosphere_engine.AtmosphereEngine()
    assert engine.get_ambiance_filename("heavy rain") == "ambient_rain_heavy.wav"
    assert engine.get_ambiance_filename("spooky wind") == "ambient_wind_loop.wav"
    assert engine.get_ambiance_filename("silence") is None
