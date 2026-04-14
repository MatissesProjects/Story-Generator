import sqlite3
import config
import llm
import os
import random
import json

class MusicOrchestrator:
    def __init__(self):
        self.db_path = config.MUSIC_DB_PATH
        self.sequencer_path = config.AUDIO_SEQUENCER_PATH

    def _query_db(self, query, params=(), one=False):
        if not os.path.exists(self.db_path):
            print(f"Music Error: DB not found at {self.db_path}")
            return None
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(query, params)
            rv = cur.fetchall()
            return (rv[0] if rv else None) if one else rv

    def detect_mood(self, story_text):
        """
        Uses the LLM to detect the emotional mood of the current story segment.
        """
        prompt = f"""
[SYSTEM: You are the Music Director. Analyze the following story segment and identify the primary emotional mood.

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
        mood = ""
        for chunk in llm.generate_story_segment(prompt):
            mood += chunk
            
        return mood.strip()

    def select_track(self, mood, recent_tracks=None):
        """
        Selects a track from the AudioSequencer database that matches the mood.
        """
        # For now, let's use a simple mapping or keyword search in filenames/lyrics
        # In a more advanced version, we'd use embeddings.
        
        mood_keywords = {
            "Exploration": ["wave", "serenade", "flow", "starlight", "dust"],
            "Tension": ["maze", "collision", "vice", "depths"],
            "Combat": ["velocity", "collision", "energy"],
            "Heroic": ["ascent", "revelation", "conduit"],
            "Mournful": ["catharsis", "surrender"],
            "Cosmic": ["cosmic", "celestial", "starlight", "sojourn", "pilgrimage"]
        }
        
        keywords = mood_keywords.get(mood, ["cosmic"])
        
        # Build a query to find tracks with matching keywords in filename
        like_clauses = " OR ".join([f"filename LIKE ?" for _ in keywords])
        query = f"SELECT * FROM tracks WHERE {like_clauses}"
        params = [f"%{k}%" for k in keywords]
        
        tracks = self._query_db(query, tuple(params))
        
        if not tracks:
            # Fallback: get any track
            tracks = self._query_db("SELECT * FROM tracks LIMIT 50")
            
        if tracks:
            # Avoid repeating recent tracks if possible
            if recent_tracks:
                available = [t for t in tracks if t['filename'] not in recent_tracks]
                if available:
                    return random.choice(available)
            
            return random.choice(tracks)
            
        return None

    def get_track_url(self, track):
        """
        Returns a URL or path that the frontend can use to play the track.
        Since the tracks are in a different project folder, we might need 
        to symlink or serve them specifically.
        """
        if not track:
            return None
            
        # For now, we'll return the absolute path and let the server decide how to mount it.
        return track['file_path']

if __name__ == "__main__":
    # Test
    print("Testing Music Orchestrator...")
    orchestrator = MusicOrchestrator()
    mood = orchestrator.detect_mood("I stand on the edge of the galactic core, watching the stars swirl.")
    print(f"Detected Mood: {mood}")
    track = orchestrator.select_track(mood)
    if track:
        print(f"Selected Track: {track['filename']} at {track['file_path']}")
    else:
        print("No track found.")
