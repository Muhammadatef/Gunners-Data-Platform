# Arsenal FC RAG Chatbot

AI-powered football data analyst using RAG (Retrieval-Augmented Generation) to answer questions about Arsenal FC performance data.

## Features

- 🤖 **Claude 3.5 Sonnet Integration**: Elite AI model for nuanced football analysis
- 📊 **Vector Search**: ChromaDB for semantic search over Arsenal match data
- 🔍 **Context-Aware**: Retrieves relevant matches to ground responses in real data
- 💬 **Conversational**: Maintains conversation history for follow-up questions
- 🎯 **Confidence Scoring**: Provides confidence levels for each answer
- 📈 **Source Citations**: Shows which matches informed each response

## Setup

### 1. Configure Anthropic API Key

Edit `.env` in the project root:

```bash
ANTHROPIC_API_KEY=your_actual_key_here
```

Get your key from: https://console.anthropic.com/

### 2. Build and Start Services

```bash
docker-compose up -d --build rag-chatbot
```

### 3. Build Initial Embeddings

After the service starts, build the vector database:

```bash
curl -X POST http://localhost:5000/rebuild-embeddings
```

This fetches all Arsenal matches from PostgreSQL and creates embeddings for semantic search.

## API Endpoints

### POST /chat

Ask a question about Arsenal data.

**Request:**
```json
{
  "question": "How did Arsenal perform against Liverpool this season?",
  "conversation_history": []
}
```

**Response:**
```json
{
  "answer": "Arsenal played Liverpool twice in the 2024-25 season...",
  "sources": [
    {
      "match_date": "2024-12-29",
      "opponent": "Liverpool",
      "result": "W 3-1",
      "season": "2024-25"
    }
  ],
  "confidence": 0.92
}
```

### POST /rebuild-embeddings

Rebuild the vector database from current PostgreSQL data.

### GET /health

Health check endpoint.

### GET /stats

Get statistics about the vector database.

## Architecture

```
User Question
    ↓
Embedding Model (all-MiniLM-L6-v2)
    ↓
ChromaDB Vector Search → Retrieve Top 5 Matches
    ↓
Build Context from Matches
    ↓
LangChain RAG Pipeline
    ↓
Claude 3.5 Sonnet (with Arsenal analyst persona)
    ↓
Formatted Answer + Sources + Confidence
```

## Files

- `app.py` - FastAPI server with chat endpoints
- `rag/chain.py` - LangChain RAG orchestration
- `rag/embeddings.py` - ChromaDB vector database manager
- `utils/db_connector.py` - PostgreSQL data fetcher
- `system_prompts/analyst.txt` - AI persona definition

## Usage in Frontend

The chatbot appears as a floating button in the bottom-right corner of the Arsenal FC dashboard. Click to open the chat window and ask questions like:

- "How did we perform in our last match?"
- "What's our xG trend this season?"
- "Compare our home vs away performance"
- "Show stats against top 6 opponents"
- "Who's our top scorer?"

## Development

To run locally without Docker:

```bash
cd rag-chatbot
pip install -r requirements.txt
python app.py
```

Access at: http://localhost:5000
