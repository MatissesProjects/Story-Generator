import db
import llm
import os

def main():
    # Ensure DB is initialized
    if not os.path.exists(db.DB_PATH):
        db.init_db()

    print("--- Story Generator (Core Engine) ---")
    print("Type 'exit' to quit, 'add character' to add a character, or just type to start the story.")

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

        # For now, we don't have the Context Curator (Track 3), 
        # so we just send the prompt directly.
        print("\nStory: ", end="", flush=True)
        try:
            for chunk in llm.generate_story_segment(user_input):
                print(chunk, end="", flush=True)
            print()
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()