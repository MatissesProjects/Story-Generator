import db
import llm
import config
import json

class AtmosphereEngine:
    def __init__(self):
        # Registry of named atmospheres for quick mapping
        self.registry = {
            "Default": {
                "lighting": "neutral",
                "weather": "clear",
                "haptic": "none",
                "tint": "rgba(0,0,0,0)",
                "ambiance": "silence"
            },
            "Ominous": {
                "lighting": "dim_cold",
                "weather": "misty",
                "haptic": "subtle_vibration",
                "tint": "rgba(0, 20, 40, 0.2)",
                "ambiance": "wind_howl"
            },
            "Combat": {
                "lighting": "strobe_red",
                "weather": "unchanged",
                "haptic": "heavy_pulses",
                "tint": "rgba(100, 0, 0, 0.1)",
                "ambiance": "battle_drums"
            },
            "Mystical": {
                "lighting": "glowing_purple",
                "weather": "sparkles",
                "haptic": "none",
                "tint": "rgba(80, 0, 100, 0.15)",
                "ambiance": "ethereal_hum"
            },
            "Tavern": {
                "lighting": "warm_orange",
                "weather": "indoor",
                "haptic": "none",
                "tint": "rgba(100, 50, 0, 0.1)",
                "ambiance": "tavern_crowd"
            }
        }

    def get_atmosphere_by_mood(self, mood):
        """
        Retrieves a predefined atmosphere from the registry based on a mood keyword.
        """
        # Mapping pacing/moods to registry keys
        mapping = {
            "Exploration": "Default",
            "Introspective": "Ominous",
            "Action-Packed": "Combat",
            "Mystery-Focused": "Ominous",
            "Dialogue-Heavy": "Tavern"
        }
        
        key = mapping.get(mood, "Default")
        return self.registry.get(key, self.registry["Default"])

    async def detect_atmosphere(self, story_text, current_location=None):
        """
        Uses the LLM to extract atmospheric cues and map them to structured codes.
        """
        prompt = f"""
[SYSTEM: You are the Atmosphere Director. Analyze the following story segment and decide if the physical environment or mood has changed.

STORY:
"{story_text}"

CURRENT LOCATION: {current_location}

Instructions:
1. Identify the dominant Lighting (e.g., Dim, Bright, Flickering, Red, Cold).
2. Identify the Weather (e.g., Rain, Storm, Mist, Clear, Indoor).
3. Identify any Haptic/Vibration cues (e.g., Rumble, Pulse, None).
4. Identify the best Visual Tint color. 
   - MUST be an RGBA string.
   - The alpha channel (A) MUST be between 0.05 and 0.25. NEVER higher.
   - Example: "rgba(0, 0, 50, 0.15)" for a cold night.
5. Identify the best Ambiance Loop (e.g., Wind, Rain, Crowd, Silence).

Reply ONLY with a JSON object.
]
"""
        response = await llm.async_generate_full_response(prompt, model=config.FAST_MODEL)
        try:
            clean_json = response.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
            data = json.loads(clean_json)
            
            # Sanitize tint to ensure alpha is low
            tint = data.get("tint", "rgba(0,0,0,0)")
            if "rgb" in tint and "," in tint:
                # Force alpha if LLM returned rgb or high alpha rgba
                parts = tint.replace("rgba(", "").replace("rgb(", "").replace(")", "").split(",")
                r = parts[0].strip()
                g = parts[1].strip()
                b = parts[2].strip()
                # Always force a safe alpha
                tint = f"rgba({r}, {g}, {b}, 0.15)"

            # Basic validation/defaults
            return {
                "lighting": data.get("lighting", "neutral"),
                "weather": data.get("weather", "clear"),
                "haptic": data.get("haptic", "none"),
                "tint": tint,
                "ambiance": data.get("ambiance", "silence")
            }
        except Exception as e:
            print(f"Atmosphere Error (detect_atmosphere): {e}")
            return self.registry["Default"]

    def get_atmosphere_style_css(self, atmosphere):
        """
        Helper to turn atmosphere data into a CSS filter or overlay style string.
        (Useful if the backend wants to suggest CSS).
        """
        tint = atmosphere.get('tint', 'rgba(0,0,0,0)')
        return f"background-color: {tint}; mix-blend-mode: multiply;"

    def get_ambiance_filename(self, ambiance_type):
        """
        Maps a generic ambiance type to a standard filename.
        """
        mapping = {
            "wind": "ambient_wind_loop.wav",
            "rain": "ambient_rain_heavy.wav",
            "crowd": "tavern_ambiance.wav",
            "battle": "distant_war_drums.wav",
            "silence": None
        }
        # Look for partial matches
        for key in mapping:
            if key in ambiance_type.lower():
                return mapping[key]
        return None
