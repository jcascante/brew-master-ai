from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

def test_query():
    # Connect to Qdrant
    client = QdrantClient(host="localhost", port=6333)
    collection_name = "brew_master_ai"
    
    # Load the same embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Test query
    query = "What is the basic process of brewing beer?"
    print(f"Query: {query}")
    
    # Generate embedding for the query
    query_embedding = model.encode(query)
    
    # Search in Qdrant
    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding.tolist(),
        limit=3
    )
    
    print(f"\nFound {len(results)} relevant results:")
    print("-" * 50)
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i} (Score: {result.score:.3f}):")
        print(f"Source: {result.payload['source_file']}")
        print(f"Text: {result.payload['text'][:200]}...")
        print("-" * 30)

if __name__ == "__main__":
    test_query() 