import subprocess
import os
import config

# Use winsound on Windows, pygame elsewhere
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

# Path to the Piper executable and models
PIPER_EXE = config.PIPER_EXE
MODELS_DIR = config.MODELS_DIR
OUTPUT_DIR = config.AUDIO_OUTPUT_DIR

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_audio(text, speaker_id, voice_model="en_US-lessac-medium.onnx"):
    """
    Calls Piper TTS to generate a WAV file for the given text.
    """
    if not text.strip():
        return None

    # Check if executable exists
    import shutil
    if not os.path.exists(PIPER_EXE) and shutil.which(PIPER_EXE) is None:
        print(f"CRITICAL ERROR: Piper executable '{PIPER_EXE}' not found. Please download it and place it in the project root or add it to your PATH.")
        print("Download from: https://github.com/rhasspy/piper/releases")
        return None

    output_file = os.path.join(OUTPUT_DIR, f"{speaker_id}_{hash(text) % 10000}.wav")
    model_path = os.path.join(MODELS_DIR, voice_model)
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"ERROR: Voice model '{model_path}' not found.")
        print(f"Please create the '{MODELS_DIR}' folder and download '{voice_model}' AND its '.json' counterpart.")
        print("Download from: https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium")
        return None
    
    command = [
        PIPER_EXE,
        "--model", model_path,
        "--output_file", output_file
    ]
    
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process.communicate(input=text)
        
        if process.returncode == 0:
            return output_file
        else:
            print(f"Piper error: {process.stderr.read()}") # type: ignore
            return None
    except Exception as e:
        print(f"Error calling Piper: {e}")
        return None

if __name__ == "__main__":
    # Quick test if piper is installed
    print("Testing Piper TTS integration...")
    test_text = "Hello, I am a character in your story."
    path = generate_audio(test_text, "test_voice")
    if path:
        print(f"Audio generated at {path}. Playing...")
        play_audio(path)
    else:
        print("Audio generation failed (Expected if Piper/Models are not set up).")
