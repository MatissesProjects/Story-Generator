import db
import llm
import spark
import curator
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
            db.execute_db("INSERT INTO characters (name, description, traits) VALUES (?, ?, ?)", (name, desc, traits))
            print(f"Character {name} added.")
            continue

        if user_input.lower() == "add lore":
            topic = input("Topic: ")
            desc = input("Description: ")
            db.execute_db("INSERT INTO lore (topic, description) VALUES (?, ?)", (topic, desc))
            print(f"Lore topic '{topic}' added.")
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
        try:
            for chunk in llm.generate_story_segment(user_input, context_facts=facts):
                print(chunk, end="", flush=True)
            print()
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()