import chromadb
from chromadb.utils import embedding_functions
import config
import os

# Set up the embedding function
# This will download the model on first use (default: all-MiniLM-L6-v2)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=config.EMBEDDING_MODEL
)

_client = None
_lore_collection = None
_char_collection = None

def _get_collections():
    """
    Lazily initializes the ChromaDB client and collections.
    Ensures they use the current config.VECTOR_DB_PATH.
    """
    global _client, _lore_collection, _char_collection
    if _client is None:
        # Ensure directory exists
        if not os.path.exists(config.VECTOR_DB_PATH):
            os.makedirs(config.VECTOR_DB_PATH, exist_ok=True)
            
        _client = chromadb.PersistentClient(path=config.VECTOR_DB_PATH)
        _lore_collection = _client.get_or_create_collection(
            name="lore", 
            embedding_function=embedding_func,
            metadata={"hnsw:space": "cosine"} # Use cosine similarity
        )

        _char_collection = _client.get_or_create_collection(
            name="characters", 
            embedding_function=embedding_func,
            metadata={"hnsw:space": "cosine"}
        )
    return _lore_collection, _char_collection

def reset_memory_engine():
    """
    Resets the memory engine, clearing the client and collections.
    Used for testing to ensure isolation.
    """
    global _client, _lore_collection, _char_collection
    # No need to explicitly delete collections if we are changing paths,
    # but we must clear the references so they are re-initialized.
    _client = None
    _lore_collection = None
    _char_collection = None

def add_lore_vector(topic, description, lore_id):
    """
    Adds a lore entry to the vector database.
    """
    lore_collection, _ = _get_collections()
    lore_collection.add(
        documents=[f"{topic}: {description}"],
        metadatas=[{"topic": topic, "type": "lore", "id": lore_id}],
        ids=[f"lore_{lore_id}"]
    )

def add_character_vector(name, description, traits, char_id):
    """
    Adds a character entry to the vector database.
    """
    _, char_collection = _get_collections()
    char_collection.add(
        documents=[f"{name}: {description}. Traits: {traits}"],
        metadatas=[{"name": name, "type": "character", "id": char_id}],
        ids=[f"char_{char_id}"]
    )

def search_semantic_with_scores(query, n_results=3, threshold=0.5):
    """
    Searches both collections and returns (fact, similarity_score).
    """
    lore_collection, char_collection = _get_collections()
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
        for i in range(len(lore_results['documents'][0])):
            doc = lore_results['documents'][0][i]
            dist = lore_results['distances'][0][i]
            # Convert distance to similarity score (cosine)
            # Chroma returns 1 - similarity for cosine
            score = 1.0 - dist
            if score >= threshold:
                results.append((f"LORE: {doc}", score))

    # Process character results
    if char_results['distances'] and char_results['distances'][0]:
        for i in range(len(char_results['documents'][0])):
            doc = char_results['documents'][0][i]
            dist = char_results['distances'][0][i]
            score = 1.0 - dist
            if score >= threshold:
                results.append((f"CHARACTER: {doc}", score))

    # Sort by score descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:n_results]

if __name__ == "__main__":
    # Test
    test_query = "Who is the assassin?"
    print(f"Searching for: {test_query}")
    
    # Add dummy data
    add_character_vector("Malakar", "A shadowy assassin", "Ruthless", 999)
    add_lore_vector("The Void", "A region of pure shadow and cold.", 999)
    
    semantic_matches = search_semantic_with_scores(test_query)
    print(f"Results for '{test_query}':")
    for match, score in semantic_matches:
        print(f"- {match} (Score: {score:.2f})")
