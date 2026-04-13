import subprocess
import os
import winsound # Using built-in winsound for WAV playback on Windows

# Path to the Piper executable and models (User should configure these)
PIPER_EXE = "piper" # Assumes it's in the PATH
MODELS_DIR = "models"
OUTPUT_DIR = "audio_output"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_audio(text, speaker_id, voice_model="en_US-lessac-medium.onnx"):
    """
    Calls Piper TTS to generate a WAV file for the given text.
    """
    if not text.strip():
        return None

    output_file = os.path.join(OUTPUT_DIR, f"{speaker_id}_{hash(text) % 10000}.wav")
    model_path = os.path.join(MODELS_DIR, voice_model)
    
    # Check if model exists, if not, use a default or print a warning
    if not os.path.exists(model_path):
        print(f"Warning: Voice model {model_path} not found. Using default if available.")
        # For MVP, we'll just assume piper is configured correctly or has a default
    
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
            print(f"Piper error: {process.stderr.read()}")
            return None
    except Exception as e:
        print(f"Error calling Piper: {e}")
        return None

def play_audio(file_path):
    """
    Plays the generated WAV file using winsound.
    """
    if file_path and os.path.exists(file_path):
        winsound.PlaySound(file_path, winsound.SND_FILENAME)

if __name__ == "__main__":
    # Quick test if piper is installed
    print("Testing Piper TTS integration...")
    test_text = "Hello, I am a character in your story."
    # Note: This will fail if piper is not in PATH or models are missing, 
    # but the logic is sound for the integration.
    path = generate_audio(test_text, "test_voice")
    if path:
        print(f"Audio generated at {path}. Playing...")
        play_audio(path)
    else:
        print("Audio generation failed (Expected if Piper/Models are not set up).")