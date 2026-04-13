import db

# Test Character
db.add_character("Elara", "A brave warrior", "Determined, Loyal")

# Test Retrieval
chars = db.query_db("SELECT * FROM characters")
for char in chars:
    print(f"Character: {char['name']} - {char['description']} ({char['traits']})")

# Clean up (Optional, but good for testing)
db.execute_db("DELETE FROM characters WHERE name = ?", ("Elara",))
print("Test complete.")