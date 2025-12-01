# ============================
# Build stage
# ============================
FROM python:3.12.3 AS builder

# Environment configs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system packages needed by Python deps (psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create venv
RUN python -m venv /app/.venv

# Install requirements
COPY requirements.txt .
RUN /app/.venv/bin/pip install --no-cache-dir -r requirements.txt


# ============================
# Final minimal runtime image
# ============================
FROM python:3.12.3-slim

WORKDIR /app

# Install only lightweight system deps needed at runtime
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY app ./app

# Expose app port
EXPOSE 8000

# Run using the venv Python
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
