import os
import sqlite3
import shutil
import db

def reset():
    print("--- Story Generator: Total Reset ---")
    
    # 1. Close any connections and delete the database
    if os.path.exists("story_memory.db"):
        print("Deleting story_memory.db...")
        try:
            os.remove("story_memory.db")
        except Exception as e:
            print(f"Error deleting DB: {e}")

    # 2. Delete the vector database (Chroma)
    if os.path.exists("vector_db"):
        print("Deleting vector_db folder...")
        try:
            shutil.rmtree("vector_db")
        except Exception as e:
            print(f"Error deleting vector_db: {e}")

    # 3. Re-initialize the database schema
    print("Re-initializing database...")
    db.init_db()

    # 4. Clear any persistent state in story_state if needed
    # (Already handled by deleting the .db file)

    print("\n[SUCCESS] The slate is clean. Start a new session now.")

if __name__ == "__main__":
    reset()
