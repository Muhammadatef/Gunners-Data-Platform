from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

from utils.db_connector import DatabaseConnector
from rag.embeddings import EmbeddingManager
from rag.chain import RAGChain

load_dotenv()

app = FastAPI(title="Arsenal FC RAG Chatbot API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = DatabaseConnector()
embeddings = EmbeddingManager(persist_directory=os.getenv('CHROMA_DB_PATH', './data/chroma'))
rag_chain = RAGChain()

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    conversation_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict]
    confidence: float
    model: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Arsenal FC RAG Chatbot"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for Arsenal FC analysis
    """
    try:
        # Retrieve relevant matches from vector DB
        search_results = embeddings.search(request.question, n_results=5)

        documents = search_results['documents']
        metadatas = search_results['metadatas']
        distances = search_results['distances']

        # Build context from retrieved documents
        context = rag_chain.build_context(documents)

        # Convert Pydantic models to dicts for the chain
        history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]

        # Get response from RAG chain
        response = rag_chain.invoke(
            question=request.question,
            context=context,
            history=history
        )

        # Calculate confidence based on retrieval scores (inverse of distance)
        avg_distance = sum(distances) / len(distances) if distances else 1.0
        confidence = max(0.0, min(1.0, 1.0 - (avg_distance / 2.0)))

        # Format sources
        sources = [
            {
                "match_date": meta['match_date'],
                "opponent": meta['opponent'],
                "result": meta['result'],
                "season": meta['season']
            }
            for meta in metadatas
        ]

        return ChatResponse(
            answer=response['answer'],
            sources=sources,
            confidence=round(confidence, 2),
            model=response['model']
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/rebuild-embeddings")
async def rebuild_embeddings():
    """
    Rebuild embeddings from database (admin endpoint)
    """
    try:
        # Clear existing embeddings
        embeddings.clear_collection()

        # Fetch all matches
        matches = db.fetch_all_matches()

        # Add to vector database
        embeddings.add_matches(matches)

        return {
            "status": "success",
            "matches_indexed": len(matches),
            "message": "Embeddings rebuilt successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rebuilding embeddings: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get chatbot statistics"""
    try:
        collection_count = embeddings.collection.count()

        return {
            "indexed_matches": collection_count,
            "model": "claude-3-5-sonnet",
            "embedding_model": "all-MiniLM-L6-v2",
            "vector_db": "ChromaDB"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
