FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy startup script
COPY backend/start.sh .
RUN chmod +x start.sh

# Expose port (Railway sets PORT env var)
EXPOSE 8000

# Use shell entrypoint — guarantees $PORT expansion
ENTRYPOINT ["/bin/sh", "start.sh"]
