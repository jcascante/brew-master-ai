from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and client
model: Optional[SentenceTransformer] = None
qdrant_client: Optional[QdrantClient] = None
claude_client: Optional[anthropic.Anthropic] = None
COLLECTION_NAME = "brew_master_ai"

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="The search query")
    conversation_context: Optional[str] = Field(default="", description="Previous conversation context")
    top_k: int = Field(default=3, ge=1, le=20, description="Number of results to return")

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    query: str
    confidence_score: float
    response_quality: str

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
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
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

def format_fallback_response(query: str, chunks: List[ChunkResult], conversation_context: str = "") -> str:
    """Format raw chunks into a structured, readable fallback response"""
    
    # Start with a friendly introduction
    response_parts = [
        f"🍺 **Brew Master AI Response**\n",
        f"*Query: {query}*\n"
    ]
    
    # Add conversation context if available
    if conversation_context:
        response_parts.append(f"\n📝 **Previous Context**:\n{conversation_context}\n")
    
    # Add main content with structured formatting
    response_parts.append(f"\n🔍 **Relevant Information Found**:\n")
    
    # Group chunks by source file for better organization
    chunks_by_source = {}
    for chunk in chunks:
        source = chunk.source_file
        if source not in chunks_by_source:
            chunks_by_source[source] = []
        chunks_by_source[source].append(chunk)
    
    # Format each source's chunks
    for source_file, source_chunks in chunks_by_source.items():
        # Calculate average confidence for this source
        avg_confidence = sum(chunk.score for chunk in source_chunks) / len(source_chunks)
        
        response_parts.append(f"\n📄 **Source: {source_file}** ({(avg_confidence * 100):.1f}% match)")
        
        for i, chunk in enumerate(source_chunks, 1):
            # Clean and format the text
            clean_text = chunk.text.strip()
            if clean_text:
                # Add bullet point and format the text
                formatted_text = f"  • {clean_text}"
                response_parts.append(formatted_text)
    
    # Add summary and tips
    response_parts.append(f"\n💡 **Summary**:")
    response_parts.append(f"  • Found {len(chunks)} relevant information chunks")
    response_parts.append(f"  • Sources: {', '.join(chunks_by_source.keys())}")
    response_parts.append(f"  • Average confidence: {(sum(chunk.score for chunk in chunks) / len(chunks) * 100):.1f}%")
    
    # Add note about Claude API
    response_parts.append(f"\n⚠️ **Note**: This is a fallback response. For more polished answers, please configure the Claude API key.")
    
    return "\n".join(response_parts)

def calculate_confidence_score(chunks: List[ChunkResult], query_length: int) -> tuple[float, str]:
    """Calculate confidence score and response quality based on chunks and query"""
    
    if not chunks:
        return 0.0, "No relevant information found"
    
    # Calculate average similarity score
    avg_similarity = sum(chunk.score for chunk in chunks) / len(chunks)
    
    # Calculate coverage (how much information we have)
    total_content_length = sum(len(chunk.text) for chunk in chunks)
    coverage_score = min(total_content_length / (query_length * 10), 1.0)  # Normalize coverage
    
    # Calculate diversity (how many different sources)
    unique_sources = len(set(chunk.source_file for chunk in chunks))
    diversity_score = min(unique_sources / 3, 1.0)  # Normalize diversity
    
    # Combine scores with weights
    confidence_score = (avg_similarity * 0.6 + coverage_score * 0.3 + diversity_score * 0.1)
    
    # Determine response quality
    if confidence_score >= 0.8:
        quality = "Excellent"
    elif confidence_score >= 0.6:
        quality = "Good"
    elif confidence_score >= 0.4:
        quality = "Fair"
    else:
        quality = "Limited"
    
    return confidence_score, quality

async def generate_rag_response(query: str, chunks: List[ChunkResult], conversation_context: str = "") -> str:
    """Generate RAG response using Claude API with conversation context"""
    if claude_client is None:
        # Use the new formatted fallback response
        return format_fallback_response(query, chunks, conversation_context)
    
    # Prepare context from chunks
    context = "\n\n".join([f"Source: {chunk.source_file}\nContent: {chunk.text}" for chunk in chunks])
    
    # Create prompt for Claude with conversation context
    conversation_prompt = ""
    if conversation_context:
        conversation_prompt = f"\n\nPrevious conversation context:\n{conversation_context}"
    
    prompt = f"""You are a helpful assistant for beer brewing knowledge. Use the following context to answer the user's question. If the context doesn't contain enough information to answer the question, say so.

Context:
{context}{conversation_prompt}

User Question: {query}

Please provide a clear, helpful answer based on the context provided. If you reference information from the context, mention the source file. If this question relates to previous conversation context, acknowledge that connection."""

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
        # Use the same formatted fallback response
        return format_fallback_response(query, chunks, conversation_context)

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
        
        # Generate RAG response with conversation context
        conversation_context = request.conversation_context or ""
        answer = await generate_rag_response(request.query, chunks, conversation_context)
        
        # Calculate confidence score and response quality
        confidence_score, response_quality = calculate_confidence_score(chunks, len(request.query))
        
        # Format sources for response
        sources = [
            {
                "source_file": chunk.source_file,
                "score": chunk.score,
                "text_preview": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
            }
            for chunk in chunks
        ]
        
        logger.info(f"Generated response for query with {len(chunks)} sources, confidence: {confidence_score:.2f}")
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            query=request.query,
            confidence_score=confidence_score,
            response_quality=response_quality
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
