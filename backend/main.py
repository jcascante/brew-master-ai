from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
import anthropic
import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Global variables for model and client
model: Optional[SentenceTransformer] = None
qdrant_client: Optional[QdrantClient] = None
claude_client: Optional[anthropic.Anthropic] = None
COLLECTION_NAME = "brew_master_ai"

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="The search query")
    top_k: int = Field(default=3, ge=1, le=20, description="Number of results to return")

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    query: str

class ChunkResult(BaseModel):
    score: float
    source_file: str
    text: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize model and Qdrant client on startup"""
    global model, qdrant_client, claude_client
    try:
        logger.info("Loading sentence transformer model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")
        
        logger.info("Connecting to Qdrant...")
        qdrant_client = QdrantClient(host="localhost", port=6333)
        # Test connection
        collections = qdrant_client.get_collections()
        if COLLECTION_NAME not in [c.name for c in collections.collections]:
            raise HTTPException(status_code=500, detail=f"Collection '{COLLECTION_NAME}' not found in Qdrant")
        logger.info("Qdrant connection established")
        
        # Initialize Claude client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not found in environment variables")
        else:
            claude_client = anthropic.Anthropic(api_key=api_key)
            logger.info("Claude client initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Backend initialization failed: {str(e)}")

async def get_relevant_chunks(query: str, top_k: int) -> List[ChunkResult]:
    """Get relevant chunks from Qdrant"""
    if model is None or qdrant_client is None:
        raise HTTPException(status_code=503, detail="Backend not properly initialized")
    
    # Embed the query (run in thread pool to avoid blocking)
    query_embedding = await asyncio.to_thread(model.encode, query)
    
    # Search Qdrant (run in thread pool to avoid blocking)
    results = await asyncio.to_thread(
        qdrant_client.search,
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding.tolist(),
        limit=top_k,
        with_payload=True
    )
    
    # Format results
    formatted_results = []
    for hit in results:
        formatted_results.append(ChunkResult(
            score=float(hit.score),
            source_file=hit.payload.get("source_file", "unknown"),
            text=hit.payload.get("text", "")
        ))
    
    return formatted_results

async def generate_rag_response(query: str, chunks: List[ChunkResult]) -> str:
    """Generate RAG response using Claude API"""
    if claude_client is None:
        # Fallback: return just the chunks if Claude is not available
        return f"Query: {query}\n\nRelevant information:\n" + "\n\n".join([f"From {chunk.source_file}: {chunk.text}" for chunk in chunks])
    
    # Prepare context from chunks
    context = "\n\n".join([f"Source: {chunk.source_file}\nContent: {chunk.text}" for chunk in chunks])
    
    # Create prompt for Claude
    prompt = f"""You are a helpful assistant for beer brewing knowledge. Use the following context to answer the user's question. If the context doesn't contain enough information to answer the question, say so.

Context:
{context}

User Question: {query}

Please provide a clear, helpful answer based on the context provided. If you reference information from the context, mention the source file."""

    try:
        model_name = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")

        # Call Claude API (run in thread pool to avoid blocking)
        response = await asyncio.to_thread(
            claude_client.messages.create,
            model=model_name,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
        
    except Exception as e:
        logger.error(f"Claude API error: {str(e)}")
        # Fallback response
        return f"Query: {query}\n\nRelevant information:\n" + "\n\n".join([f"From {chunk.source_file}: {chunk.text}" for chunk in chunks])

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Full RAG chat endpoint with Claude API integration"""
    try:
        # Validate query
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Processing query: {request.query[:50]}...")
        
        # Get relevant chunks
        chunks = await get_relevant_chunks(request.query, request.top_k)
        
        if not chunks:
            return ChatResponse(
                answer="I couldn't find any relevant information in my knowledge base for your question.",
                sources=[],
                query=request.query
            )
        
        # Generate RAG response
        answer = await generate_rag_response(request.query, chunks)
        
        # Format sources for response
        sources = [
            {
                "source_file": chunk.source_file,
                "score": chunk.score,
                "text_preview": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
            }
            for chunk in chunks
        ]
        
        logger.info(f"Generated response for query with {len(chunks)} sources")
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            query=request.query
        )
        
    except UnexpectedResponse as e:
        logger.error(f"Qdrant error: {str(e)}")
        raise HTTPException(status_code=503, detail="Vector database error")
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get('/health')
def health_check():
    """Health check endpoint"""
    try:
        if model is None or qdrant_client is None:
            return {"status": "error", "message": "Backend not initialized"}
        
        # Test Qdrant connection
        collections = qdrant_client.get_collections()
        collection_exists = COLLECTION_NAME in [c.name for c in collections.collections]
        
        return {
            "status": "ok",
            "model_loaded": model is not None,
            "qdrant_connected": qdrant_client is not None,
            "collection_exists": collection_exists,
            "claude_available": claude_client is not None
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get('/')
def read_root():
    return {"message": "Hello from Brew Master AI Backend!"}
