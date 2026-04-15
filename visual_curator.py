import db
import os
import config

class VisualCurator:
    def __init__(self):
        # Mood-based texture registry (generic assets)
        self.textures = {
            "Cyberpunk": "/static/textures/grid_flow.gif",
            "Grimdark": "/static/textures/smoke_slow.gif",
            "High Fantasy": "/static/textures/magical_dust.gif",
            "Ethereal": "/static/textures/aurora_bokeh.gif",
            "Default": "/static/textures/subtle_noise.png"
        }
        
        # Overlay registry
        self.overlays = {
            "Rain": "/static/overlays/rain_glass.png",
            "Glitch": "/static/overlays/vhs_glitch.gif",
            "Dust": "/static/overlays/dust_motes.gif",
            "None": None
        }

    def get_visual_stack(self, current_location, involved_entities, atmosphere_data):
        """
        Determines the current state of all visual layers.
        """
        stack = {
            "texture": self.textures.get("Default"),
            "environment": None,
            "entity": None,
            "overlay": None
        }

        # 1. Environment Layer
        if current_location:
            safe_name = "".join([c for c in current_location if c.isalnum()]).lower()
            env_path = os.path.join(config.ENVIRONMENTS_DIR, f"{safe_name}.png")
            if os.path.exists(env_path):
                stack["environment"] = f"/static/environments/{safe_name}.png"

        # 2. Entity Layer (Portrait of the primary character)
        if involved_entities:
            # For now, just pick the first one detected
            primary = involved_entities[0]
            safe_name = "".join([c for c in primary if c.isalnum()]).lower()
            port_path = os.path.join(config.PORTRAITS_DIR, f"{safe_name}.png")
            if os.path.exists(port_path):
                stack["entity"] = f"/static/portraits/{safe_name}.png"

        # 3. Texture Layer (Based on mood/atmosphere)
        # Placeholder: Logic to map atmosphere/location to texture
        if "City" in current_location or "Neon" in current_location:
            stack["texture"] = self.textures["Cyberpunk"]
        elif "Void" in current_location or "Shadow" in current_location:
            stack["texture"] = self.textures["Grimdark"]

        # 4. Overlay Layer (Based on weather)
        weather = atmosphere_data.get('weather', '').lower()
        if 'rain' in weather or 'storm' in weather:
            stack["overlay"] = self.overlays["Rain"]
        elif 'glitch' in weather or 'anomaly' in weather:
            stack["overlay"] = self.overlays["Glitch"]

        return stack
