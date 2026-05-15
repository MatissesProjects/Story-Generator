import pytest
import vision
import config
import os
import torch
from unittest.mock import MagicMock, patch, AsyncMock

@pytest.fixture
def mock_pipe_instance():
    instance = MagicMock()
    # Mocking the pipeline call
    instance.return_value = MagicMock(images=[MagicMock()])
    instance.to.return_value = instance
    instance.vae = MagicMock()
    return instance

@pytest.mark.asyncio
async def test_clean_vision_prompt():
    assert vision.clean_vision_prompt("[Narrator]: A cat.") == "A cat."
    assert vision.clean_vision_prompt('"A dog"') == "A dog"
    assert vision.clean_vision_prompt("'A bird'") == "A bird"

@pytest.mark.asyncio
async def test_stylize_prompt():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Detailed prompt"
        res = await vision.stylize_prompt("Name", "Desc", "Traits")
        assert res == "Detailed prompt"

@pytest.mark.asyncio
async def test_stylize_environment_prompt():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Env Prompt"
        res = await vision.stylize_environment_prompt("Loc", "Desc")
        assert res == "Env Prompt"

@pytest.mark.asyncio
async def test_stylize_map_tile_prompt():
    with patch("llm.async_generate_full_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Tile Prompt"
        res = await vision.stylize_map_tile_prompt("Biome")
        assert res == "Tile Prompt"

@pytest.mark.asyncio
async def test_generate_portrait_cached():
    with patch("os.path.exists", return_value=True), \
         patch("config.IMAGE_CACHE_ENABLED", True):
        url = await vision.generate_portrait("Elara", "Desc", "Traits")
        assert "/static/portraits/" in url

@pytest.mark.asyncio
async def test_generate_portrait_success(mock_pipe_instance):
    with patch("vision.stylize_prompt", new_callable=AsyncMock) as mock_style, \
         patch("vision.run_inference", new_callable=AsyncMock) as mock_inf, \
         patch("os.path.exists", return_value=False):
         
         mock_style.return_value = "Prompt"
         mock_image = MagicMock()
         mock_inf.return_value = mock_image
         
         url = await vision.generate_portrait("NewChar", "D", "T")
         assert url is not None
         mock_image.save.assert_called_once()

@pytest.mark.asyncio
async def test_generate_environment_success(mock_pipe_instance):
    with patch("vision.stylize_environment_prompt", new_callable=AsyncMock) as mock_style, \
         patch("vision.run_inference", new_callable=AsyncMock) as mock_inf, \
         patch("os.path.exists", return_value=False):
         
         mock_style.return_value = "Env Prompt"
         mock_image = MagicMock()
         mock_inf.return_value = mock_image
         
         url = await vision.generate_environment("Cave", "Spooky")
         assert url is not None
         mock_image.save.assert_called_once()

@pytest.mark.asyncio
async def test_generate_map_tile_success(mock_pipe_instance):
    with patch("vision.stylize_map_tile_prompt", new_callable=AsyncMock) as mock_style, \
         patch("vision.run_inference", new_callable=AsyncMock) as mock_inf, \
         patch("os.path.exists", return_value=False):
         
         mock_style.return_value = "Tile Prompt"
         mock_image = MagicMock()
         mock_inf.return_value = mock_image
         
         url = await vision.generate_map_tile("Forest")
         assert url is not None
         mock_image.save.assert_called_once()

@pytest.mark.asyncio
async def test_run_inference_cuda_success(mock_pipe_instance):
    with patch("vision.pipe", mock_pipe_instance), \
         patch("vision.device", "cuda"), \
         patch("torch.cuda.amp.autocast"), \
         patch("torch.cuda.empty_cache"):
         
         image = await vision.run_inference("Prompt")
         assert image is not None

@pytest.mark.asyncio
async def test_run_inference_cpu_fallback(mock_pipe_instance):
    with patch("vision.pipe") as mock_global_pipe:
        mock_global_pipe.side_effect = torch.cuda.OutOfMemoryError("OOM")
        
        with patch("vision.device", "cuda"), \
             patch("torch.cuda.empty_cache"), \
             patch("vision.AutoPipelineForText2Image.from_pretrained") as mock_load:
             
             new_pipe = MagicMock()
             mock_load.return_value = new_pipe
             new_pipe.return_value = MagicMock(images=[MagicMock()])
             new_pipe.vae = MagicMock()
             
             image = await vision.run_inference("Prompt")
             assert image is not None
             assert vision.device == "cpu"

@pytest.mark.asyncio
async def test_handle_vision_request():
    mock_ws = AsyncMock()
    message = {
        "request_type": "portrait",
        "content": {"name": "Test", "description": "D", "traits": "T"},
        "request_id": "123"
    }
    
    with patch("vision.generate_portrait", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "/url"
        await vision.handle_vision_request(mock_ws, message)
        
        args, kwargs = mock_ws.send.call_args
        import json
        resp = json.loads(args[0])
        assert resp['type'] == "vision_complete"
        assert resp['url'] == "/url"

@pytest.mark.asyncio
async def test_generate_portrait_failure():
    with patch("vision.run_inference", return_value=None), \
         patch("os.path.exists", return_value=False), \
         patch("vision.stylize_prompt", new_callable=AsyncMock) as mock_style:
        mock_style.return_value = "P"
        url = await vision.generate_portrait("Fail", "D", "T")
        assert url is None
