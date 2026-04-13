import db
import llm
import spark
import curator
import parser
import tts
import os

def main():
    # Ensure DB is initialized
    if not os.path.exists(db.DB_PATH):
        db.init_db()

    print("--- Story Generator ---")
    print("Type 'exit' to quit.")
    print("Type 'add character' or 'add lore' to update the world.")
    print("Type 'spark' to generate a story idea.")
    print("Or just type to continue the story.")

    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == "exit":
            break
        
        if user_input.lower() == "add character":
            name = input("Name: ")
            desc = input("Description: ")
            traits = input("Traits: ")
            voice = input("Voice Model (default: en_US-lessac-medium.onnx): ") or "en_US-lessac-medium.onnx"
            db.add_character(name, desc, traits, voice)
            print(f"Character {name} added with voice {voice}.")
            continue

        if user_input.lower() == "add lore":
            topic = input("Topic: ")
            desc = input("Description: ")
            db.add_lore(topic, desc)
            print(f"Lore topic '{topic}' added.")
            continue

        if user_input.lower() == "add meta":
            topic = input("Meta-Narrative Topic: ")
            desc = input("Subtle Description: ")
            kws = input("Trigger Keywords (comma separated): ")
            db.add_meta_lore(topic, desc, kws)
            print(f"Meta-narrative '{topic}' added.")
            continue

        if user_input.lower() == "spark":
            genre = input("Genre (optional, press Enter for random): ")
            idea = spark.generate_spark(genre if genre else None)
            print(f"\nSpark:\n{idea}")
            continue

        # Use the Curator to find relevant context
        facts = curator.get_relevant_context(user_input)
        if facts:
            print(f"[DEBUG: Using context: {', '.join(facts[:2])}...]")

        print("\nStory: ", end="", flush=True)
        full_response = ""
        try:
            for chunk in llm.generate_story_segment(user_input, context_facts=facts):
                print(chunk, end="", flush=True)
                full_response += chunk
            print()
            
            # --- Audio Processing (Track 4) ---
            print("\n[Audio Generation...]")
            dialogue_lines = parser.parse_dialogue(full_response)
            for speaker, text in dialogue_lines:
                voice_model = db.get_character_voice(speaker)
                print(f"Generating audio for {speaker}...")
                audio_path = tts.generate_audio(text, speaker, voice_model)
                if audio_path:
                    tts.play_audio(audio_path)
            # ---------------------------------
            
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()