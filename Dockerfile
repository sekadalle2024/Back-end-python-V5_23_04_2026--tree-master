FROM python:3.11-slim

# Add labels for the image
LABEL org.opencontainers.image.title="Clara Backend"
LABEL org.opencontainers.image.description="Clara AI Assistant Backend Service"
LABEL org.opencontainers.image.authors="Clara Team"
LABEL org.opencontainers.image.source="https://github.com/clara17verse/clara"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.vendor="Clara"
LABEL org.opencontainers.image.version="1.0.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies directly with pip (faster than uv for Hugging Face)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV HOST="0.0.0.0" \
    PORT=7860 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port (Hugging Face uses 7860)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the application
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "7860"] 