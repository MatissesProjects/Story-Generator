import os
import wave
import config
from piper import PiperVoice

# Cache for loaded voices to avoid reloading from disk every time
VOICE_CACHE = {}

def get_voice(voice_model="en_US-lessac-medium.onnx"):
    """
    Loads or retrieves a PiperVoice from the cache.
    """
    model_path = os.path.join(config.MODELS_DIR, voice_model)
    config_path = f"{model_path}.json"

    if model_path not in VOICE_CACHE:
        if not os.path.exists(model_path):
            print(f"ERROR: Voice model '{model_path}' not found.")
            return None
        
        print(f"TTS: Loading voice model {voice_model}...")
        VOICE_CACHE[model_path] = PiperVoice.load(model_path, config_path=config_path)
    
    return VOICE_CACHE[model_path]

def generate_audio(text, speaker_id, voice_model="en_US-lessac-medium.onnx"):
    """
    Generates a WAV file for the given text using the piper-tts Python API.
    """
    if not text.strip():
        return None

    output_dir = config.AUDIO_OUTPUT_DIR
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"{speaker_id}_{hash(text) % 10000}.wav")
    
    voice = get_voice(voice_model)
    if not voice:
        return None

    try:
        with wave.open(output_file, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)
        
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
    print("Testing Piper TTS Python API integration...")
    test_text = "The ancient gears of the library groaned as the secret door finally opened."
    path = generate_audio(test_text, "test_voice")
    if path:
        print(f"Audio generated at {path}. Playing...")
        play_audio(path)
    else:
        print("Audio generation failed.")
