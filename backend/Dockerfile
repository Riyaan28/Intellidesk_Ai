FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y \
  gcc \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel for better performance
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements from both backend and ai
COPY backend/requirements.txt ./backend_requirements.txt
COPY ai/requirements.txt ./ai_requirements.txt

# Install lightweight dependencies first (faster, can cache)
RUN pip install --default-timeout=1000 --retries 5 \
  fastapi uvicorn[standard] sqlalchemy pydantic python-dotenv \
  python-multipart email-validator redis psycopg2-binary

# Install heavy ML dependencies separately with longer timeout
RUN pip install --default-timeout=2000 --retries 5 \
  google-generativeai numpy

# Install the heaviest packages last (torch-based)
RUN pip install --default-timeout=2000 --retries 5 \
  sentence-transformers faiss-cpu

# Copy AI module first
COPY ai/ /app/ai/

# Copy backend code
COPY backend/ /app/backend/

# Copy run_backend.py launcher
COPY run_backend.py /app/

# Set working directory to backend
WORKDIR /app/backend

# Create directory for SQLite database
RUN mkdir -p /app/backend/data

# Expose port
EXPOSE 8000

# Run application using the launcher script
CMD ["python", "/app/run_backend.py"]
