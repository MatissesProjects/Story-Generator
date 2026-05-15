import db
import llm
import json
import os
import config

class MusicOrchestrator:
    def __init__(self):
        # We'll use the AudioSequencer generated assets or sample tracks
        self.enabled = config.MUSIC_ENABLED
        self.tracks = [
            {"filename": "ambient_mystery.wav", "mood": "Mystery", "intensity": 2},
            {"filename": "ambient_forest.wav", "mood": "Nature", "intensity": 1},
            {"filename": "battle_intense.wav", "mood": "Combat", "intensity": 5},
            {"filename": "dark_suspense.wav", "mood": "Suspense", "intensity": 3}
        ]

    async def detect_mood(self, text):
        """
        Uses the LLM to determine the appropriate musical mood for the text.
        """
        prompt = f"""
[SYSTEM: You are the Musical Director. Analyze the following story segment and decide on the most appropriate musical mood.
CHOICES: Mystery, Nature, Combat, Suspense, Ethereal, Sorrow, Triumph.

STORY SEGMENT:
"{text}"

REPLY ONLY WITH THE MOOD NAME.]
"""
        try:
            mood = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
            return mood.strip().strip('"').strip("'")
        except Exception as e:
            print(f"Music Orchestrator Error (detect_mood): {e}")
            return "Suspense"

    def select_track(self, mood):
        """
        Picks the best matching track for a given mood.
        """
        matches = [t for t in self.tracks if mood.lower() in t['mood'].lower()]
        if matches:
            import random
            return random.choice(matches)
        
        # Fallback to general ambient if no match
        if self.tracks:
            return self.tracks[0]
        return None

    def get_ambiance_filename(self, ambiance_type):
        """
        Maps a descriptive ambiance type to a loopable WAV file.
        """
        if not ambiance_type:
            return None
            
        mapping = {
            "rain": "ambient_rain_heavy.wav",
            "wind": "ambient_wind_loop.wav",
            "fire": "campfire_crackle.wav",
            "crowd": "tavern_crowd.wav",
            "battle": "distant_war_drums.wav",
            "silence": None
        }
        # Look for partial matches
        for key in mapping:
            if key in ambiance_type.lower():
                return mapping[key]
        return None

if __name__ == "__main__":
    import asyncio
    async def test():
        print("Testing Music Orchestrator...")
        mo = MusicOrchestrator()
        mood = await mo.detect_mood("A shadowy figure emerges from the fog, eyes glowing with a faint blue light.")
        print(f"Detected Mood: {mood}")
        track = mo.select_track(mood)
        if track:
            print(f"Selected Track: {track['filename']}")
    
    asyncio.run(test())
