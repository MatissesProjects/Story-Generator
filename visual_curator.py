import db
import os
import config

class VisualCurator:
    def __init__(self):
        # Cache for mapping character/location names to their specific hashed asset URLs
        self.entity_cache = {}

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
        Determines the current state of all visual layers, including character staging slots.
        """
        stack = {
            "texture": self.textures.get("Default"),
            "environment": None,
            "slots": {
                "left": None,
                "center": None,
                "right": None
            },
            "overlay": None,
            "primary": primary_entity # The current speaker
        }

        # 1. Environment Layer
        if current_location:
            # Prefer cached URL if available
            if current_location in self.entity_cache:
                stack["environment"] = self.entity_cache[current_location]
            else:
                safe_name = "".join([c for c in current_location if c.isalnum()]).lower()
                # Use on-demand asset endpoint as fallback
                stack["environment"] = f"/asset/environment/{safe_name}"

        # 2. Character Staging (Slots)
        if involved_entities:
            available_slots = ["left", "right", "center"]
            assigned = []

            # Primary speaker goes in Center
            if primary_entity and primary_entity in involved_entities:
                if primary_entity in self.entity_cache:
                    stack["slots"]["center"] = self.entity_cache[primary_entity]
                else:
                    safe_primary = "".join([c for c in primary_entity if c.isalnum()]).lower()
                    stack["slots"]["center"] = f"/asset/portrait/{safe_primary}"
                assigned.append(primary_entity)
                available_slots.remove("center")

            # Fill remaining slots
            for entity in involved_entities:
                if entity not in assigned and available_slots:
                    slot = available_slots.pop(0)
                    if entity in self.entity_cache:
                        stack["slots"][slot] = self.entity_cache[entity]
                    else:
                        safe_name = "".join([c for c in entity if c.isalnum()]).lower()
                        stack["slots"][slot] = f"/asset/portrait/{safe_name}"
                    assigned.append(entity)

        # 3. Texture Layer (Based on mood/atmosphere)
        if current_location:
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
