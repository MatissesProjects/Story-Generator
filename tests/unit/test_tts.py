import pytest
import tts
import os
import config
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_piper():
    with patch("tts.PiperVoice") as mock_voice:
        instance = MagicMock()
        mock_voice.load.return_value = instance
        yield instance

def test_clean_text_for_tts():
    # Test combining marks removal
    text = "Héllò* world"
    cleaned = tts.clean_text_for_tts(text)
    assert "*" not in cleaned
    assert "Hello" in cleaned

def test_get_voice_cached(mock_piper):
    # Setup cache
    tts.VOICE_CACHE["test.onnx"] = "CachedVoice"
    
    # We need to make sure the model_path matches the key
    with patch("os.path.join", return_value="test.onnx"):
        voice = tts.get_voice("test")
        assert voice == "CachedVoice"

def test_get_voice_load_failure(mock_piper):
    tts.VOICE_CACHE = {}
    with patch("os.path.exists", return_value=False):
        voice = tts.get_voice("nonexistent")
        assert voice is None

def test_generate_audio_success(mock_piper):
    # Mock voice.synthesize_wav
    voice_mock = MagicMock()
    model_name = config.DEFAULT_VOICE
    if not model_name.endswith(".onnx"): model_name += ".onnx"
    full_path = os.path.join(config.MODELS_DIR, model_name)
    
    tts.VOICE_CACHE[full_path] = voice_mock
    
    with patch("os.path.exists", return_value=True), \
         patch("wave.open") as mock_wave:
        
        path = tts.generate_audio("Hello", "speaker1")
        assert path is not None
        assert "speaker1" in path
        voice_mock.synthesize_wav.assert_called_once()

def test_generate_audio_failure(mock_piper):
    voice_mock = MagicMock()
    voice_mock.synthesize_wav.side_effect = Exception("Crash")
    tts.VOICE_CACHE = {k: voice_mock for k in tts.VOICE_CACHE} # Patch all cache
    
    with patch("os.path.exists", return_value=True), \
         patch("wave.open"):
        path = tts.generate_audio("Hello", "speaker1")
        assert path is None

def test_generate_audio_empty_text():
    assert tts.generate_audio("", "id") is None

def test_get_voice_with_cuda(mock_piper):
    tts.VOICE_CACHE = {}
    with patch("torch.cuda.is_available", return_value=True), \
         patch("os.path.exists", return_value=True), \
         patch("site.getsitepackages", return_value=[]), \
         patch("site.getusersitepackages", return_value=""), \
         patch("glob.glob", return_value=["/nvidia/lib"]):
         
         # Mock successful load
         voice = tts.get_voice("cuda_model")
         assert voice is not None
         assert "/nvidia/lib" in os.environ.get("LD_LIBRARY_PATH", "")

def test_get_voice_load_exception(mock_piper):
    tts.VOICE_CACHE = {}
    with patch("os.path.exists", return_value=True):
        # First load fails, second (CPU) succeeds
        mock_piper.load.side_effect = [Exception("CUDA Fail"), MagicMock()]
        voice = tts.get_voice("fail_model")
        assert voice is not None

def test_generate_audio_no_voice():
    with patch("tts.get_voice", return_value=None):
        assert tts.generate_audio("H", "S") is None

def test_play_audio_init_mixer():
    with patch("pygame.mixer.Sound"), \
         patch("pygame.mixer.init") as mock_init, \
         patch("pygame.mixer.get_init", return_value=False), \
         patch("os.path.exists", return_value=True), \
         patch("pygame.mixer.get_busy", side_effect=[True, False]):
         
        tts.play_audio("dummy.wav")
        assert mock_init.called

def test_play_audio_error():
    with patch("pygame.mixer.Sound", side_effect=Exception("Pygame Crash")), \
         patch("pygame.mixer.get_init", return_value=True), \
         patch("os.path.exists", return_value=True):
         
        # Should catch error and print
        tts.play_audio("fail.wav")
        assert True
