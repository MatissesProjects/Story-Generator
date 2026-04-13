import chromadb
from chromadb.utils import embedding_functions
import config
import os

# Set up the embedding function
# This will download the model on first use (default: all-MiniLM-L6-v2)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=config.EMBEDDING_MODEL
)

# Initialize ChromaDB client
# We use PersistentClient to save the data to disk
client = chromadb.PersistentClient(path=config.VECTOR_DB_PATH)

# Get or create the collections
# One for lore and one for characters
lore_collection = client.get_or_create_collection(
    name="lore", 
    embedding_function=embedding_func,
    metadata={"hnsw:space": "cosine"} # Use cosine similarity
)

char_collection = client.get_or_create_collection(
    name="characters", 
    embedding_function=embedding_func,
    metadata={"hnsw:space": "cosine"}
)

def add_lore_vector(topic, description, lore_id):
    """
    Adds a lore entry to the vector database.
    """
    lore_collection.add(
        documents=[f"{topic}: {description}"],
        metadatas=[{"topic": topic, "type": "lore", "id": lore_id}],
        ids=[f"lore_{lore_id}"]
    )

def add_character_vector(name, description, traits, char_id):
    """
    Adds a character entry to the vector database.
    """
    char_collection.add(
        documents=[f"{name}: {description}. Traits: {traits}"],
        metadatas=[{"name": name, "type": "character", "id": char_id}],
        ids=[f"char_{char_id}"]
    )

def search_semantic(query, n_results=3, threshold=0.5):
    """
    Searches both collections for semantically similar entries.
    Returns a list of strings ready for prompt injection.
    """
    results = []
    
    # Search lore
    lore_results = lore_collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    # Search characters
    char_results = char_collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    # Process lore results
    if lore_results['distances'] and lore_results['distances'][0]:
        for i, distance in enumerate(lore_results['distances'][0]):
            # distance is 1 - cosine_similarity for 'cosine' space
            # smaller distance = more similar
            similarity = 1 - distance
            if similarity >= threshold:
                doc = lore_results['documents'][0][i]
                results.append(f"LORE (Semantic): {doc}")
                
    # Process character results
    if char_results['distances'] and char_results['distances'][0]:
        for i, distance in enumerate(char_results['distances'][0]):
            similarity = 1 - distance
            if similarity >= threshold:
                doc = char_results['documents'][0][i]
                results.append(f"CHARACTER (Semantic): {doc}")
                
    return results

if __name__ == "__main__":
    # Quick test
    print("Testing Memory Engine...")
    test_query = "What do we know about dark realms?"
    add_lore_vector("The Abyss", "A terrifying dimension of pure shadow and cold.", 999)
    
    semantic_matches = search_semantic(test_query)
    print(f"Results for '{test_query}':")
    for match in semantic_matches:
        print(f"- {match}")
