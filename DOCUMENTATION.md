# Arsenal FC Analytics Platform - Complete Documentation

A professional-grade football analytics platform that scrapes, processes, and visualizes Arsenal FC match data with an AI-powered chatbot.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Flow](#data-flow)
3. [Quick Start](#quick-start)
4. [RAG Chatbot - Beginner's Guide](#rag-chatbot---beginners-guide)
5. [Component Details](#component-details)
6. [Makefile Commands](#makefile-commands)
7. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARSENAL FC ANALYTICS PLATFORM                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│   │   Understat  │    │    FBref     │    │  (Future)    │                   │
│   │   (xG data)  │    │  (Advanced)  │    │  Other APIs  │                   │
│   └──────┬───────┘    └──────┬───────┘    └──────────────┘                   │
│          │                   │                                                │
│          └─────────┬─────────┘                                                │
│                    │                                                          │
│                    ▼                                                          │
│   ┌────────────────────────────────────────────────────────────┐             │
│   │                    APACHE AIRFLOW                          │             │
│   │  ┌─────────────────────────────────────────────────────┐  │             │
│   │  │ arsenal_smart_match_scraper (runs every 6 hours)    │  │             │
│   │  │ • Checks for new completed matches                   │  │             │
│   │  │ • Scrapes Understat + FBref data                     │  │             │
│   │  │ • Loads into PostgreSQL                              │  │             │
│   │  └─────────────────────────────────────────────────────┘  │             │
│   └────────────────────────────────────────────────────────────┘             │
│                    │                                                          │
│                    ▼                                                          │
│   ┌────────────────────────────────────────────────────────────┐             │
│   │                    POSTGRESQL DATABASE                      │             │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────┐            │             │
│   │  │   BRONZE   │→ │   SILVER   │→ │    GOLD    │            │             │
│   │  │ (Raw JSON) │  │ (Cleaned)  │  │ (Metrics)  │            │             │
│   │  └────────────┘  └────────────┘  └────────────┘            │             │
│   └────────────────────────────────────────────────────────────┘             │
│          │                                         │                          │
│          │                                         │                          │
│          ▼                                         ▼                          │
│   ┌──────────────────┐                 ┌──────────────────────┐              │
│   │  GRAPHQL BACKEND │                 │    RAG CHATBOT       │              │
│   │   (Node.js)      │                 │  (Python/FastAPI)    │              │
│   │   Port: 4000     │                 │    Port: 5000        │              │
│   └────────┬─────────┘                 └──────────┬───────────┘              │
│            │                                       │                          │
│            └───────────────┬───────────────────────┘                          │
│                            │                                                  │
│                            ▼                                                  │
│   ┌────────────────────────────────────────────────────────────┐             │
│   │                    REACT FRONTEND (Vite)                    │             │
│   │                       Port: 3000                            │             │
│   │  ┌─────────────────────────────────────────────────────┐   │             │
│   │  │ • 11 Interactive Dashboards                          │   │             │
│   │  │ • AI Chatbot Integration                             │   │             │
│   │  │ • Season Selector                                    │   │             │
│   │  │ • Data Quality Indicators                            │   │             │
│   │  └─────────────────────────────────────────────────────┘   │             │
│   └────────────────────────────────────────────────────────────┘             │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Services Summary

| Service | Technology | Port | Purpose |
|---------|------------|------|---------|
| Frontend | React + Vite + Chakra UI | 3000 | User interface with dashboards |
| Backend | Node.js + GraphQL | 4000 | API layer for data queries |
| RAG Chatbot | Python + FastAPI | 5000 | AI-powered analytics assistant |
| Database | PostgreSQL | 5432 | Data storage (medallion architecture) |
| Airflow | Apache Airflow | 8080 | Scheduled data scraping |

---

## Data Flow

### 1. Data Collection (Scraping)

```
Match Played → Wait 2 hours → Airflow DAG triggers → Scrapers run
                                                          │
                        ┌─────────────────────────────────┴─────────────────────────────────┐
                        │                                                                   │
                        ▼                                                                   ▼
                 ┌──────────────┐                                                  ┌──────────────┐
                 │  Understat   │                                                  │    FBref     │
                 │ • Match xG   │                                                  │ • Lineups    │
                 │ • Shot data  │                                                  │ • Passing    │
                 │ • Positions  │                                                  │ • Advanced   │
                 └──────────────┘                                                  └──────────────┘
```

### 2. Medallion Architecture (Data Layers)

```
BRONZE (Raw)                    SILVER (Cleaned)                 GOLD (Metrics)
────────────                    ────────────────                 ──────────────
• understat_raw                 • shots_cleaned                  • arsenal_matches
• fbref_raw                     • matches_normalized             • arsenal_player_stats
• scrape_runs                   • player_performances            • opponent_comparison
                                                                 • season_summary
```

### 3. Data Access

```
Frontend Request → GraphQL Query → PostgreSQL (Gold Layer) → Response → Dashboard
                                                    │
AI Chat Request → RAG Chatbot → ChromaDB (Vector Search) → Claude API → Response
                                         │
                                    Uses embeddings of
                                    match data for
                                    semantic search
```

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Make (optional, for convenience commands)

### Start Everything

```bash
# Clone and enter directory
cd Gunners-Platform

# Start all services
make up

# Or manually:
docker compose up -d

# Check status
make status
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend Dashboard | http://localhost:3000 |
| GraphQL Playground | http://localhost:4000/graphql |
| Airflow UI | http://localhost:8080 (admin/admin) |
| RAG Chatbot API | http://localhost:5000 |

---

## RAG Chatbot - Beginner's Guide

### What is RAG?

**RAG = Retrieval-Augmented Generation**

It's a technique that makes AI chatbots smarter by giving them access to your specific data. Instead of relying only on what the AI was trained on, RAG lets you:

1. **Store your data** in a searchable format (embeddings)
2. **Find relevant data** when a user asks a question
3. **Pass that data** to the AI along with the question
4. **Get accurate answers** based on YOUR data, not general knowledge

### Why Use RAG?

| Without RAG | With RAG |
|-------------|----------|
| AI might hallucinate statistics | AI uses your real match data |
| Generic football knowledge | Specific Arsenal FC analysis |
| Can't answer about recent matches | Knows every scraped match |
| No sources/citations | Can cite specific match dates |

### How Our RAG System Works

```
User Question: "How did Arsenal perform against Liverpool?"
                            │
                            ▼
                ┌───────────────────────┐
                │  1. EMBEDDING SEARCH   │
                │  Convert question to   │
                │  vector, find similar  │
                │  match documents       │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  2. RETRIEVE DATA      │
                │  Get top 5 most        │
                │  relevant matches      │
                │  from ChromaDB         │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  3. BUILD PROMPT       │
                │  Combine: system       │
                │  prompt + match data   │
                │  + user question       │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  4. CALL CLAUDE API    │
                │  Send augmented        │
                │  prompt, get response  │
                └───────────┬───────────┘
                            │
                            ▼
                   AI Response with
                   real match statistics
```

### RAG Code Explained (Line by Line)

#### File 1: `rag-chatbot/rag/embeddings.py`

This file handles converting match data into searchable vectors.

```python
# Import the embedding model - this converts text to vectors (numbers)
from sentence_transformers import SentenceTransformer

# Import ChromaDB - a vector database that stores and searches embeddings
import chromadb
from chromadb.config import Settings

class EmbeddingManager:
    def __init__(self, persist_directory: str = "./data/chroma"):
        # Load the embedding model
        # 'all-MiniLM-L6-v2' is a small, fast model that creates 384-dimensional vectors
        # It understands semantic meaning - "Arsenal won" and "Gunners victory" are similar
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Connect to ChromaDB (vector database)
        # This stores our match embeddings on disk
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=persist_directory,  # Where to save the database
            anonymized_telemetry=False           # Don't send usage data
        ))
        
        # Get or create our collection (like a table in a regular database)
        try:
            self.collection = self.chroma_client.get_collection("arsenal_matches")
        except:
            # If it doesn't exist, create it
            self.collection = self.chroma_client.create_collection(
                name="arsenal_matches",
                metadata={"description": "Arsenal FC match statistics"}
            )
    
    def create_match_document(self, match: Dict[str, Any]) -> str:
        """Convert match data to searchable text
        
        WHY: ChromaDB needs text documents to create embeddings.
        We format each match as a readable text block with all important stats.
        """
        text = f"""
        Match: Arsenal vs {match['opponent']} on {match['match_date']}
        Result: {match['result']} ({match['arsenal_goals']}-{match['opponent_goals']})
        
        Expected Goals (xG):
        - Arsenal xG: {match['arsenal_xg']:.2f}
        - Opponent xG: {match['opponent_xg']:.2f}
        
        Shot Statistics:
        - Total Shots: {match['total_shots']}
        - Shots on Target: {match['shots_on_target']}
        ...
        """
        return text
    
    def add_matches(self, matches: List[Dict[str, Any]]):
        """Add matches to ChromaDB with embeddings
        
        HOW IT WORKS:
        1. For each match, create a text document
        2. ChromaDB automatically creates an embedding (vector) for each document
        3. Store document + embedding + metadata for later retrieval
        """
        documents = []   # The text content
        metadatas = []   # Extra info (date, opponent, etc.)
        ids = []         # Unique identifier for each document
        
        for match in matches:
            documents.append(self.create_match_document(match))
            metadatas.append({
                "match_date": str(match['match_date']),
                "opponent": match['opponent'],
                "result": match['result']
            })
            ids.append(f"{match['match_date']}_{match['opponent']}")
        
        # Add to ChromaDB - it handles embedding automatically!
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search for relevant matches based on user query
        
        HOW IT WORKS:
        1. ChromaDB converts the query to an embedding vector
        2. It finds the 5 most similar document vectors (cosine similarity)
        3. Returns those documents with their metadata
        
        EXAMPLE:
        Query: "Liverpool matches" → Returns all Liverpool match documents
        Query: "Big wins" → Returns matches with high goal differences
        """
        results = self.collection.query(
            query_texts=[query],  # The user's question
            n_results=n_results   # How many results to return
        )
        
        return {
            "documents": results['documents'][0],   # The actual text
            "metadatas": results['metadatas'][0],   # Match info
            "distances": results['distances'][0]    # How similar (lower = more similar)
        }
```

#### File 2: `rag-chatbot/rag/chain.py`

This file handles the conversation with Claude AI.

```python
from anthropic import Anthropic  # Claude's official Python client

class RAGChain:
    def __init__(self):
        # Initialize the Anthropic client with API key from environment
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Load the system prompt - this tells Claude how to behave
        # It's like giving Claude a job description
        with open('./system_prompts/analyst.txt', 'r') as f:
            self.system_prompt = f.read()
    
    def build_context(self, documents: List[str]) -> str:
        """Combine retrieved documents into a context string
        
        WHY: We need to format the retrieved match data in a way
        that's easy for Claude to understand and reference.
        """
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"--- Match Data {i} ---\n{doc}\n")
        return "\n".join(context_parts)
    
    def invoke(self, question: str, context: str, history: List[Dict] = None):
        """Run the RAG chain - this is where the magic happens!
        
        STEPS:
        1. Build message history (for multi-turn conversations)
        2. Create prompt with context + question
        3. Call Claude API
        4. Return the response
        """
        messages = []
        
        # Add conversation history if exists (for follow-up questions)
        if history:
            for msg in history:
                messages.append({
                    "role": msg['role'],      # "user" or "assistant"
                    "content": msg['content']  # The message text
                })
        
        # Build the augmented prompt
        # THIS IS THE KEY RAG STEP: We inject retrieved data into the prompt
        user_message = f"""Using the following Arsenal FC match data, please answer:

RELEVANT MATCH DATA:
{context}  # <-- This is the retrieved match data!

USER QUESTION:
{question}

Please provide data-driven analysis with specific statistics."""
        
        messages.append({"role": "user", "content": user_message})
        
        # Call Claude API
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",  # The AI model
            max_tokens=1024,                      # Max response length
            system=self.system_prompt,            # How Claude should behave
            messages=messages                     # The conversation
        )
        
        return {
            "answer": response.content[0].text,
            "model": "claude-3-5-sonnet"
        }
```

#### File 3: `rag-chatbot/app.py`

The FastAPI application that ties everything together.

```python
from fastapi import FastAPI
from rag.embeddings import EmbeddingManager
from rag.chain import RAGChain

app = FastAPI()

# Initialize our components
embeddings = EmbeddingManager()  # Vector database
rag_chain = RAGChain()           # Claude integration

@app.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint
    
    THE COMPLETE RAG FLOW:
    1. User sends question
    2. Search vector DB for relevant matches
    3. Build context from retrieved matches
    4. Send context + question to Claude
    5. Return AI response with sources
    """
    
    # STEP 1: Search for relevant matches in vector database
    search_results = embeddings.search(request.question, n_results=5)
    
    # STEP 2: Extract documents and metadata
    documents = search_results['documents']   # Match text documents
    metadatas = search_results['metadatas']   # Match info (date, opponent)
    distances = search_results['distances']   # Similarity scores
    
    # STEP 3: Build context string from retrieved documents
    context = rag_chain.build_context(documents)
    
    # STEP 4: Call Claude with augmented prompt
    response = rag_chain.invoke(
        question=request.question,
        context=context,          # <-- The retrieved match data!
        history=request.history
    )
    
    # STEP 5: Calculate confidence based on retrieval quality
    avg_distance = sum(distances) / len(distances)
    confidence = 1.0 - (avg_distance / 2.0)  # Lower distance = higher confidence
    
    # STEP 6: Format sources for the frontend
    sources = [
        {"match_date": m['match_date'], "opponent": m['opponent']}
        for m in metadatas
    ]
    
    return {
        "answer": response['answer'],
        "sources": sources,         # What matches were used
        "confidence": confidence    # How confident we are
    }
```

### Building RAG in Your Own Projects

#### Step-by-Step Guide

1. **Choose Your Data**
   - What knowledge does your chatbot need?
   - Format it as text documents

2. **Choose an Embedding Model**
   - `all-MiniLM-L6-v2` - Fast, good for most cases
   - `text-embedding-3-small` (OpenAI) - Higher quality
   - `voyage-2` - Great for specialized domains

3. **Choose a Vector Database**
   - **ChromaDB** - Simple, good for prototypes (we use this)
   - **Pinecone** - Managed, scales well
   - **Weaviate** - Feature-rich
   - **Qdrant** - Fast, Rust-based

4. **Choose an LLM**
   - **Claude** - Great reasoning (we use this)
   - **GPT-4** - Versatile
   - **Llama 3** - Open source, self-hosted

5. **The Basic Code Pattern**

```python
# Pseudocode for any RAG application

# 1. Initialize
embedding_model = load_model("all-MiniLM-L6-v2")
vector_db = ChromaDB()
llm = Claude()

# 2. Index your data (do once)
for document in your_documents:
    embedding = embedding_model.encode(document)
    vector_db.add(document, embedding)

# 3. Answer questions (on each request)
def answer(question):
    # Search for relevant documents
    relevant_docs = vector_db.search(question, top_k=5)
    
    # Build prompt with context
    prompt = f"""
    Context: {relevant_docs}
    Question: {question}
    Answer based on the context above.
    """
    
    # Get AI response
    answer = llm.generate(prompt)
    return answer
```

---

## Component Details

### Frontend (React + Vite)

Located in `frontend-vite/`

**Key Files:**
- `src/App.tsx` - Main app with tab navigation
- `src/components/dashboards/` - 11 dashboard components
- `src/components/AIChatbot.tsx` - Chatbot UI
- `src/lib/apollo-client.ts` - GraphQL client setup

**Dashboards:**
1. Season Overview - Team performance summary
2. Match Detail - Individual match analysis
3. Player Stats - Player performance metrics
4. Tactical Analysis - Formation and style insights
5. Shot Networks - Passing and shooting patterns
6. Expected Threat (xT) - Zone-based threat analysis
7. Player Match Analysis - Per-match player breakdown
8. Opponent Analysis - Head-to-head comparisons
9. Performance Trends - Rolling averages and trends
10. Player Comparison - Side-by-side player stats
11. Match Insights - AI-generated match observations

### Backend (Node.js + GraphQL)

Located in `backend/`

**Key Files:**
- `src/server.js` - Express + Apollo Server setup
- `src/resolvers/` - GraphQL resolvers
- `src/schema/` - GraphQL type definitions
- `src/db/` - PostgreSQL connection

### Scrapers (Python)

Located in `scrapers/`

**Key Files:**
- `playwright_scraper.py` - Browser-based scraping with Playwright
- `fbref_scraper.py` - FBref data extraction
- `backfill_historical.py` - Bulk historical data loading
- `db_loader.py` - Database insertion logic

### Airflow (Data Orchestration)

Located in `airflow/`

**Key DAG: `arsenal_smart_match_scraper`**
- Runs every 6 hours
- Checks for newly completed matches
- Scrapes Understat + FBref
- Loads data into PostgreSQL
- Triggers dbt transformations

---

## Makefile Commands

```bash
# === Starting Services ===
make up              # Start all services
make up-build        # Build and start
make down            # Stop all services

# === Monitoring ===
make status          # Show container status
make logs            # Follow all logs
make logs-backend    # Backend logs only
make logs-frontend   # Frontend logs only

# === Database ===
make db-shell        # PostgreSQL shell
make db-check        # Check database status

# === Development ===
make rebuild-frontend  # Rebuild frontend container
make rebuild-backend   # Rebuild backend container
make frontend-shell    # Shell into frontend container
make backend-shell     # Shell into backend container

# === Airflow ===
make airflow-enable-dag DAG=arsenal_smart_match_scraper

# === Cleanup ===
make clean           # Remove all containers and volumes
make clean-containers  # Remove containers only
```

---

## Troubleshooting

### Frontend White Screen

**Symptoms:** Page loads briefly then goes blank

**Solution:**
```bash
# Rebuild frontend without cache
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Database Connection Errors

**Symptoms:** Backend can't connect to PostgreSQL

**Solution:**
```bash
# Check if postgres is running
docker compose ps postgres

# Restart database
docker compose restart postgres

# Check logs
docker compose logs postgres
```

### Airflow DAGs Not Loading

**Symptoms:** DAGs show import errors

**Solution:**
```bash
# Check Airflow logs
docker compose logs airflow-scheduler

# Restart Airflow
docker compose restart airflow-scheduler airflow-webserver
```

### RAG Chatbot Not Working

**Symptoms:** Chat returns errors

**Checklist:**
1. Is `ANTHROPIC_API_KEY` set in environment?
2. Is ChromaDB data populated?

```bash
# Check RAG chatbot logs
docker compose logs rag-chatbot

# Rebuild embeddings
curl -X POST http://localhost:5000/rebuild-embeddings
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=arsenalfc_analytics
POSTGRES_USER=analytics_user
POSTGRES_PASSWORD=analytics_pass

# RAG Chatbot
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Airflow (optional)
AIRFLOW_UID=50000
```

---

## License

MIT License - Feel free to use this as a template for your own analytics projects!

---

*Built with ❤️ for Arsenal FC*
