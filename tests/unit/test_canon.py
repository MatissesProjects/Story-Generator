import pytest
import canon_checker
import db
import llm
import json
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_extract_claims():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"claims": ["The island floats."]}'
        
        res = await canon_checker.extract_claims("Text")
        assert res == ["The island floats."]

@pytest.mark.asyncio
async def test_check_for_contradictions_none():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"contradictions": []}'
        
        res = await canon_checker.check_for_contradictions(["Claim"], ["Lore"])
        assert res == []

@pytest.mark.asyncio
async def test_check_for_contradictions_found():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"contradictions": [{"claim": "C", "violation": "V"}]}'
        
        res = await canon_checker.check_for_contradictions(["C"], ["V"])
        assert len(res) == 1
        assert res[0]['claim'] == "C"

@pytest.mark.asyncio
async def test_resolve_contradiction_world_change():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"resolution_type": "World Change", "explanation": "E", "new_lore": "NL"}'
        
        res = await canon_checker.resolve_contradiction({"claim": "C", "violation": "V"}, ["L"])
        assert res['resolution_type'] == "World Change"
        
        # Check DB
        lore = db.query_db("SELECT * FROM lore WHERE topic = 'Resolved Canon Shift'")
        assert len(lore) == 1
        assert lore[0]['description'] == "NL"

@pytest.mark.asyncio
async def test_resolve_contradiction_unreliable():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"resolution_type": "Unreliable Narrator", "explanation": "Character was lying."}'
        
        res = await canon_checker.resolve_contradiction({"claim": "C", "violation": "V"}, ["L"])
        assert res['resolution_type'] == "Unreliable Narrator"

@pytest.mark.asyncio
async def test_check_for_contradictions_empty_claims():
    assert await canon_checker.check_for_contradictions([], ["Lore"]) == []

@pytest.mark.asyncio
async def test_errors():
    with patch("llm.async_generate_full_response", side_effect=Exception("Err")):
        assert await canon_checker.extract_claims("T") == []
        assert await canon_checker.check_for_contradictions(["C"], ["L"]) == []
        assert await canon_checker.resolve_contradiction({}, []) is None
