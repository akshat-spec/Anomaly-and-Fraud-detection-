# Build Stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Upgrade pip and install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final Runtime Stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime minimal dependencies natively for confluent-kafka
RUN apt-get update && apt-get install -y --no-install-recommends \
    librdkafka1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment natively
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source maps & pre-built models securely
COPY src/ /app/src/
COPY models/ /app/models/

# Secure execution privileges via non-root limits safely
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# API Health Check tracking limits dynamically
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
