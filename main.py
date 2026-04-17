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

            # --- Periodic Maintenance (Summary & Plot Threads) ---
            history_count = db.get_history_count()
            if history_count % 3 == 0:
                print("\n[Updating story state...]")
                recent_history = db.get_recent_history(limit=10)
                active_threads = db.get_active_plot_threads()
                
                # 1. Update Narrative Seed (Summary)
                if history_count % 10 == 0:
                    await summarizer.update_narrative_seed()
                
                # 2. Analyze Plot Threads
                thread_updates = await director.analyze_plot_threads(recent_history, active_threads)
                
                for tid in thread_updates.get("resolved_ids", []):
                    db.update_plot_thread_status(tid, "resolved")
                    print(f"Plot Thread Resolved: {tid}")
                    
                for desc in thread_updates.get("new_threads", []):
                    db.add_plot_thread(desc)
                    print(f"New Plot Thread Discovered: {desc}")
            # ----------------------------------------------------
            
        except Exception as e:
            print(f"\nError generating story: {e}")

if __name__ == "__main__":
    asyncio.run(main())
