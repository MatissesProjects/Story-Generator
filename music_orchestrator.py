import db
import llm
import json
import os
import config

class MusicOrchestrator:
    def __init__(self):
        # We'll use the AudioSequencer generated assets or sample tracks
        self.enabled = config.MUSIC_ENABLED
        self.tracks = self._load_tracks() if self.enabled else []

    def _load_tracks(self):
        if not self.enabled:
            return []
        # Scan config.AUDIO_SEQUENCER_PATH for .wav/.mp3 files
        # For now, let's look in musicExamples and generated_assets
        tracks = []
        
        # Check musicExamples
        examples_dir = os.path.join(config.AUDIO_SEQUENCER_PATH, "musicExamples")
        if os.path.exists(examples_dir):
            for f in os.listdir(examples_dir):
                if f.endswith(".wav") or f.endswith(".mp3"):
                    tracks.append({
                        "filename": f,
                        "file_path": os.path.join(examples_dir, f),
                        "mood": "Exploration" # Default
                    })

        # Check generated_assets
        gen_dir = os.path.join(config.AUDIO_SEQUENCER_PATH, "generated_assets")
        if os.path.exists(gen_dir):
            for f in os.listdir(gen_dir):
                if f.endswith(".wav") or f.endswith(".mp3"):
                    tracks.append({
                        "filename": f,
                        "file_path": os.path.join(gen_dir, f),
                        "mood": "Custom"
                    })
        return tracks

    async def detect_mood(self, story_text):
        """
        Uses the LLM to detect the current mood of the story.
        """
        prompt = f"""
[SYSTEM: You are the Music Orchestrator. Analyze the following story segment and select the most appropriate musical mood/category.

STORY:
"{story_text}"

CATEGORIES:
- Exploration (Neutral, Curious, Atmospheric)
- Tension (Nervous, Subtle, Mystery)
- Combat (Intense, Aggressive, Fast)
- Heroic (Grand, Orchestral, Inspiring)
- Mournful (Sad, Slow, Melancholic)
- Cosmic (Dreamy, Electronic, Vast)

REPLY ONLY WITH THE CATEGORY NAME.]
"""
        return await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)

    def select_track(self, mood, recent_tracks=None):
        """
        Selects a track from the AudioSequencer database that matches the mood.
        """
        if not self.enabled or not mood:
            return None
            
        # For now, let's use a simple mapping or keyword search in filenames/lyrics
        # In a more advanced version, we'd use embeddings.
        
        # Keyword mapping
        keywords = {
            "Exploration": ["nature", "ambient", "calm", "world"],
            "Tension": ["mystery", "dark", "stealth", "shadow"],
            "Combat": ["battle", "epic", "drums", "fast"],
            "Heroic": ["grand", "victory", "brass", "theme"],
            "Mournful": ["piano", "sad", "violin", "empty"],
            "Cosmic": ["synth", "space", "pad", "future"]
        }
        
        possible_tracks = []
        target_words = keywords.get(mood, [])
        
        for track in self.tracks:
            # Check if any keyword is in the filename
            if any(word in track['filename'].lower() for word in target_words):
                possible_tracks.append(track)
                
        if not possible_tracks:
            # Fallback: random track
            return self.tracks[0] if self.tracks else None
            
        import random
        return random.choice(possible_tracks)

if __name__ == "__main__":
    import asyncio
    async def test():
        print("Testing Music Orchestrator...")
        mo = MusicOrchestrator()
        if not mo.enabled:
            print("Music is disabled (check config.AUDIO_SEQUENCER_PATH). Skipping LLM test.")
            return
            
        mood = await mo.detect_mood("The dark shadows lengthened as a mysterious figure emerged from the fog, eyes glowing with a faint blue light.")
        print(f"Detected Mood: {mood}")
        track = mo.select_track(mood)
        if track:
            print(f"Selected Track: {track['filename']}")
    
    asyncio.run(test())
