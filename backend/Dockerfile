FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y \
  gcc \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements from both backend and ai
COPY backend/requirements.txt ./backend_requirements.txt
COPY ai/requirements.txt ./ai_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r backend_requirements.txt
RUN pip install --no-cache-dir -r ai_requirements.txt

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
