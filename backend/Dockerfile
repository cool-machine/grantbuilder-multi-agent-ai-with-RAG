# Use Python 3.10 slim image for smaller size
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements-container.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-container.txt

# Copy Flask API application
COPY flask_gemma_api.py .

# Create logs directory
RUN mkdir -p /app/logs

# Expose port 8000
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV HF_HOME=/app/cache

# Create cache directory for model
RUN mkdir -p /app/cache

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run Flask application
CMD ["python", "flask_gemma_api.py"]