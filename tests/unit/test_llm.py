import pytest
import llm
import config
import httpx
import json
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_llm_build_full_prompt_all_options():
    # Test all components of build_full_prompt
    prompt = "Action"
    context = ["Fact 1"]
    instructions = "Director Instruction"
    persona = ["Persona Block"]
    seed = "Narrative Seed"
    mech = "Mechanical Result"
    payoff = "Foreshadowing Payoff"
    pacing = "Introspective"
    
    full = llm._build_full_prompt(
        prompt, 
        context_facts=context, 
        director_instructions=instructions, 
        persona_blocks=persona, 
        narrative_seed=seed, 
        mechanical_result=mech,
        foreshadowing_payoff=payoff,
        pacing_directive=pacing
    )
    
    assert "Action" in full
    assert "LORE/FACTS:\n- Fact 1" in full
    assert "DIRECTIVE: Director Instruction" in full
    assert "CHARACTER PERSONAS:\nPersona Block" in full
    assert "STORY SO FAR:\nNarrative Seed" in full
    assert "MECHANICS: Mechanical Result" in full
    assert "FORESHADOWING: Foreshadowing Payoff" in full
    assert "PACING: Introspective" in full
    assert "protagonist's internal thoughts" in full

@pytest.mark.asyncio
async def test_llm_build_full_prompt_no_options():
    full = llm._build_full_prompt("Hello")
    assert "CORE DIRECTIVE" in full
    assert "Hello" in full

@pytest.mark.asyncio
async def test_async_generate_full_response_success():
    async def mock_generator(*args, **kwargs):
        yield "The "
        yield "output"

    with patch("llm.async_generate_story_segment", side_effect=mock_generator) as mock_stream:
        resp = await llm.async_generate_full_response("Hello", model="test-model")
        assert resp == "The output"
        mock_stream.assert_called_once()

@pytest.mark.asyncio
async def test_async_generate_story_segment_streaming_with_malformed_json():
    async def mock_line_generator():
        yield json.dumps({"response": "Good", "done": False}).encode() + b"\n"
        yield b"NOT JSON\n"
        yield json.dumps({"response": " Done", "done": True}).encode() + b"\n"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.aiter_lines.return_value = mock_line_generator()
    mock_response.raise_for_status = MagicMock()
    
    with patch("httpx.AsyncClient.stream") as mock_stream_ctx:
        mock_stream_ctx.return_value.__aenter__.return_value = mock_response
        
        collected = []
        async for chunk in llm.async_generate_story_segment("Hello"):
            collected.append(chunk)
            
        assert collected == ["Good", " Done"]

@pytest.mark.asyncio
async def test_async_generate_story_segment_http_error():
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("404", request=MagicMock(), response=mock_response)
    
    with patch("httpx.AsyncClient.stream") as mock_stream_ctx:
        mock_stream_ctx.return_value.__aenter__.return_value = mock_response
        
        collected = []
        async for chunk in llm.async_generate_story_segment("Hello"):
            collected.append(chunk)
            
        assert collected == []

@pytest.mark.asyncio
async def test_async_generate_story_segment_request_error():
    with patch("httpx.AsyncClient.stream") as mock_stream_ctx:
        mock_stream_ctx.side_effect = httpx.RequestError("Connection failed")
        
        collected = []
        async for chunk in llm.async_generate_story_segment("Hello"):
            collected.append(chunk)
            
        assert collected == []

@pytest.mark.asyncio
async def test_async_generate_story_segment_unexpected_error():
    with patch("httpx.AsyncClient.stream") as mock_stream_ctx:
        mock_stream_ctx.side_effect = Exception("Chaos")
        
        collected = []
        async for chunk in llm.async_generate_story_segment("Hello"):
            collected.append(chunk)
            
        assert collected == []

@pytest.mark.asyncio
async def test_legacy_generate_story_segment():
    async def mock_generator(*args, **kwargs):
        yield "Chunk"

    with patch("llm.async_generate_story_segment", side_effect=mock_generator):
        collected = []
        async for chunk in llm.generate_story_segment("Hello"):
            collected.append(chunk)
        assert collected == ["Chunk"]
