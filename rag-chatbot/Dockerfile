FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch FIRST (much smaller, ~200MB instead of ~2GB)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install dependencies (no langchain needed - we use Anthropic directly)
RUN pip install --no-cache-dir fastapi uvicorn[standard]
RUN pip install --no-cache-dir anthropic psycopg2-binary python-dotenv pydantic
RUN pip install --no-cache-dir sentence-transformers
RUN pip install --no-cache-dir chromadb

# Copy application code
COPY . .

# Create data directory for ChromaDB
RUN mkdir -p /app/data/chroma

# Expose port
EXPOSE 5000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
