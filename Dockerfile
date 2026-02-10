FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p data

# Expose logs volume
VOLUME ["/app/data"]

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1 || python3 -c "import json; json.load(open('data/ibis_true_state.json'))" || exit 1

# Run IBIS agent
CMD ["python3", "ibis_true_agent.py"]
