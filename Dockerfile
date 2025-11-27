FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    rustc \
    cargo \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY sta_controlers.py .
COPY staremotemcp.py .

# Expose port
EXPOSE 3131

# Run the MCP server
CMD ["python", "staremotemcp.py"]