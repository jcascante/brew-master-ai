#!/usr/bin/env python3
"""
Query script for the Brew Master AI vector database.
"""

import json
import requests
import numpy as np
from sentence_transformers import SentenceTransformer
import argparse
import sys

# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "brew_master_ai"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

class VectorStoreQuery:
    def __init__(self):
        self.qdrant_url = QDRANT_URL
        self.collection_name = COLLECTION_NAME
        self.model = SentenceTransformer(MODEL_NAME)
    
    def semantic_search(self, query: str, limit: int = 10):
        """Perform semantic search using text query."""
        try:
            # Generate embedding for the query
            query_embedding = self.model.encode(query).tolist()
            
            # Prepare search payload
            payload = {
                "vector": query_embedding,
                "limit": limit,
                "with_payload": True,
                "with_vector": False
            }
            
            # Make the request
            response = requests.post(
                f"{self.qdrant_url}/collections/{self.collection_name}/points/search",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()["result"]
            else:
                print(f"Search failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description="Query Brew Master AI Vector Database")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Number of results")
    
    args = parser.parse_args()
    
    client = VectorStoreQuery()
    results = client.semantic_search(args.query, args.limit)
    
    if results:
        print(f"\nFound {len(results)} results for: '{args.query}'")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result.get('score', 'N/A'):.4f}")
            payload = result.get("payload", {})
            print(f"   Source: {payload.get('source_file', 'Unknown')}")
            print(f"   Text: {payload.get('text', 'No text')[:200]}...")
    else:
        print("No results found.")

if __name__ == "__main__":
    main() 