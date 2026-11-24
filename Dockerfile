# ==============================================================================
# ShellSathi - Intelligent Linux Command Assistant Dockerfile
# Production-ready multi-service container supporting FastAPI API & Streamlit UI
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer standard output/error
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    BACKEND_URL=http://api:8000

# Set container working directory
WORKDIR /app

# Install system dependencies (curl for container health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies manifest first to leverage Docker layer caching
COPY requirements.txt .

# Install Python production dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source code, dataset records, prompts and configurations
COPY app/ ./app/
COPY ui/ ./ui/
COPY data/ ./data/
COPY prompts/ ./prompts/
COPY eval/ ./eval/
COPY pyproject.toml ./
COPY README.md ./

# Expose FastAPI API port (8000) and Streamlit UI port (8501)
EXPOSE 8000 8501

# Default startup command launches FastAPI backend; overridden by docker-compose for UI
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
