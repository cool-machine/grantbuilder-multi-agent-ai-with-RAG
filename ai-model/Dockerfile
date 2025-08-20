# GrantSeeker AI - Gemma 3 270M-IT Container
# Production-ready deployment for Azure Container Instances
FROM python:3.10-slim

LABEL maintainer="GrantSeeker AI Platform" \
      description="Containerized Gemma 3 270M-IT for AI-powered grant writing" \
      version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with optimization
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy Flask API application
COPY flask_gemma_api.py .
COPY deploy/ ./deploy/

# Create necessary directories
RUN mkdir -p /app/logs /app/cache

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    HF_HOME=/app/cache \
    TRANSFORMERS_CACHE=/app/cache \
    PYTORCH_TRANSFORMERS_CACHE=/app/cache

# Expose port 8000
EXPOSE 8000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app
USER appuser

# Run Flask application
CMD ["python", "flask_gemma_api.py"]