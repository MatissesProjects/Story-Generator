import pytest
import validator
import llm
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_validate_action_success():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"is_valid": true, "reason": "Possible"}'
        
        is_valid, reason = await validator.validate_action("I walk", ["World is flat"])
        assert is_valid is True
        assert reason == "Possible"

@pytest.mark.asyncio
async def test_validate_action_invalid():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"is_valid": false, "reason": "Impossible"}'
        
        is_valid, reason = await validator.validate_action("I fly", ["No magic"])
        assert is_valid is False
        assert reason == "Impossible"

@pytest.mark.asyncio
async def test_validate_action_error_fallback():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.side_effect = Exception("LLM Down")
        
        # Should fallback to True (Fail-Open)
        is_valid, reason = await validator.validate_action("I walk", [])
        assert is_valid is True
        assert "unexpected error" in reason

@pytest.mark.asyncio
async def test_validate_action_malformed_json():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "This is not JSON"
        
        # Should fallback to True
        is_valid, reason = await validator.validate_action("I walk", [])
        assert is_valid is True
        assert "unclear" in reason
