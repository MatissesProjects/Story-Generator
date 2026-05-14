import os
import wave
import config
import unicodedata
from piper import PiperVoice
from dataclasses import dataclass
from typing import Optional

# For Piper 1.x, the SynthesisConfig might be in piper.voice or similar
try:
    from piper.voice import SynthesisConfig
except ImportError:
    @dataclass
    class SynthesisConfig:
        speaker_id: Optional[int] = None
        length_scale: Optional[float] = None
        noise_scale: Optional[float] = None
        noise_w_scale: Optional[float] = None

# Cache for loaded voices to avoid reloading from disk every time
VOICE_CACHE = {}

def clean_text_for_tts(text: str) -> str:
    """
    Cleans text for TTS by removing problematic characters, specifically combining marks
    that Piper might not have phonemes for.
    """
    # Normalize to decomposed form to separate combining marks
    text = unicodedata.normalize('NFKD', text)
    # Remove non-spacing marks (category 'Mn')
    text = "".join([c for c in text if unicodedata.category(c) != 'Mn'])
    # Replace common problematic characters
    text = text.replace('\u0329', '')
    text = text.replace('*', '')
    return text.strip()

def get_voice(voice_model=None):
    """
    Loads or retrieves a PiperVoice from the cache.
    Automatically appends .onnx if missing.
    """
    if voice_model is None:
        voice_model = config.DEFAULT_VOICE

    if not voice_model.endswith(".onnx"):
        voice_model += ".onnx"

    model_path = os.path.join(config.MODELS_DIR, voice_model)
    config_path = f"{model_path}.json"

    if model_path not in VOICE_CACHE:
        if not os.path.exists(model_path):
            print(f"ERROR: Voice model '{model_path}' not found.")
            return None

        import torch
        use_cuda = torch.cuda.is_available()
        
        # RTX 4090 / CUDA 12 path patching for onnxruntime-gpu
        if use_cuda:
            import site
            import glob
            # Find all nvidia library directories in site-packages
            package_paths = site.getsitepackages() + [site.getusersitepackages()]
            if hasattr(site, 'getusersitepackages'):
                package_paths.append(site.getusersitepackages())
            
            # Specifically check venv if applicable
            venv_path = os.path.join(os.getcwd(), ".venv", "lib", "python*", "site-packages")
            
            nvidia_lib_paths = []
            search_patterns = [
                os.path.join(p, "nvidia", "*", "lib") for p in package_paths
            ] + [os.path.join(venv_path, "nvidia", "*", "lib")]
            
            for pattern in search_patterns:
                nvidia_lib_paths.extend(glob.glob(pattern))
            
            if nvidia_lib_paths:
                current_ld = os.environ.get("LD_LIBRARY_PATH", "")
                new_paths = ":".join(nvidia_lib_paths)
                os.environ["LD_LIBRARY_PATH"] = f"{new_paths}:{current_ld}"
                print(f"TTS: Patched LD_LIBRARY_PATH with {len(nvidia_lib_paths)} NVIDIA lib directories.")

        print(f"TTS: Loading voice model {voice_model} (CUDA: {use_cuda})...")
        try:
            VOICE_CACHE[model_path] = PiperVoice.load(model_path, config_path=config_path, use_cuda=use_cuda)
        except Exception as e:
            print(f"TTS: Failed to load with CUDA, falling back to CPU. Error: {e}")
            VOICE_CACHE[model_path] = PiperVoice.load(model_path, config_path=config_path, use_cuda=False)

    return VOICE_CACHE[model_path]

def generate_audio(text, speaker_id, voice_config=None):
    """
    Generates a WAV file for the given text using the piper-tts Python API.
    voice_config: dict with {voice_id, length_scale, noise_scale, noise_w}
    """
    text = clean_text_for_tts(text)

    if not text:
        return None

    if voice_config is None:
        voice_config = {
            "voice_id": config.DEFAULT_VOICE,
            "length_scale": 1.0,
            "noise_scale": 0.667,
            "noise_w": 0.8
        }

    output_dir = config.AUDIO_OUTPUT_DIR
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"{speaker_id}_{hash(text) % 10000}.wav")

    voice_id = voice_config.get('voice_id', config.DEFAULT_VOICE)
    print(f"TTS: Generating audio for '{speaker_id}' using model '{voice_id}'")    
    voice = get_voice(voice_id)
    if not voice:
        return None

    try:
        syn_config = SynthesisConfig(
            length_scale=voice_config.get('length_scale', 1.0),
            noise_scale=voice_config.get('noise_scale', 0.667),
            noise_w_scale=voice_config.get('noise_w', 0.8)
        )

        with wave.open(output_file, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file, syn_config=syn_config)
        
        if os.path.exists(output_file):
            return output_file
        return None
    except Exception as e:
        print(f"Error generating audio with Piper API: {e}")
        return None

# Use winsound on Windows, pygame elsewhere for playback
if os.name == 'nt':
    import winsound
    def play_audio(file_path):
        if file_path and os.path.exists(file_path):
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
else:
    import pygame
    def play_audio(file_path):
        if file_path and os.path.exists(file_path):
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            try:
                sound = pygame.mixer.Sound(file_path)
                sound.play()
                while pygame.mixer.get_busy():
                    pygame.time.delay(100)
            except Exception as e:
                print(f"Error playing audio with pygame: {e}")

if __name__ == "__main__":
    # Quick test
    print("Testing Piper TTS Python API integration with modifications...")
    test_config = {
        "voice_id": config.DEFAULT_VOICE,
        "length_scale": 1.5, # Slower
        "noise_scale": 0.8,
        "noise_w": 1.0
    }
    path = generate_audio("This is a test of the modified voice system.", "test_voice", voice_config=test_config)
    if path:
        print(f"Audio generated at {path}. Playing...")
        play_audio(path)
    else:
        print("Audio generation failed.")
