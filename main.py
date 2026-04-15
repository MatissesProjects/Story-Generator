import curator
import llm
import db
import parser
import tts
import config
import spark
import asyncio

async def main():
    db.init_db()
    print("--- Story Generator (CLI) ---")
    print("Type 'spark' for a random idea, or just start typing your story.")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nYou: ")
        except EOFError:
            break
            
        if user_input.lower() in ["exit", "quit"]:
            break

        if user_input.lower() == "spark":
            genre = input("Genre (optional, press Enter for random): ")
            # Note: spark.generate_spark should probably be async too if it uses llm
            # Let's check spark.py
            idea = await spark.generate_spark(genre if genre else None)
            print(f"\nSpark:\n{idea}")
            continue

        # Use the Curator to find relevant context
        facts = curator.get_relevant_context(user_input)
        if facts:
            print(f"[DEBUG: Using context: {', '.join(facts[:2])}...]")

        print("\nStory: ", end="", flush=True)
        full_response = ""
        try:
            async for chunk in llm.generate_story_segment(user_input, context_facts=facts):
                print(chunk, end="", flush=True)
                full_response += chunk
            print()
            
            # --- Audio Processing (Track 4) ---
            print("\n[Audio Generation...]")
            dialogue_lines = parser.parse_dialogue(full_response)
            for speaker, text in dialogue_lines:
                voice_config = db.get_character_voice(speaker)
                
                print(f"Generating audio for {speaker}...")
                audio_path = tts.generate_audio(text, speaker, voice_config=voice_config)
                if audio_path:
                    tts.play_audio(audio_path)
            # ---------------------------------
            
        except Exception as e:
            print(f"\nError generating story: {e}")

if __name__ == "__main__":
    asyncio.run(main())
