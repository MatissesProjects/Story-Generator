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

    def get_visual_stack(self, current_location, involved_entities, atmosphere_data, primary_entity=None):
        """
        Determines the current state of all visual layers.
        """
        stack = {
            "texture": self.textures.get("Default"),
            "environment": None,
            "entity": None,
            "overlay": None,
            "involved_portraits": {},
            "primary_entity": primary_entity
        }

        # 1. Environment Layer
        if current_location:
            safe_name = "".join([c for c in current_location if c.isalnum()]).lower()
            env_path = os.path.join(config.ENVIRONMENTS_DIR, f"{safe_name}.png")
            if os.path.exists(env_path):
                # Mounted at /environments in server.py
                stack["environment"] = f"/environments/{safe_name}.png"

        # 2. Entity Layer (Portrait mapping)
        if involved_entities:
            for entity in involved_entities:
                safe_name = "".join([c for c in entity if c.isalnum()]).lower()
                port_path = os.path.join(config.PORTRAITS_DIR, f"{safe_name}.png")
                if os.path.exists(port_path):
                    # Mounted at /portraits in server.py
                    stack["involved_portraits"][entity] = f"/portraits/{safe_name}.png"

            # Set the primary visual entity
            if primary_entity and primary_entity in stack["involved_portraits"]:
                stack["entity"] = stack["involved_portraits"][primary_entity]
            elif involved_entities:
                # Try to find any available portrait from the involved list
                for ent in involved_entities:
                    if ent in stack["involved_portraits"]:
                        stack["entity"] = stack["involved_portraits"][ent]
                        break

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
