# Multi-stage lightweight Dockerfile optimized for AWS ECS / Fargate deployment
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into wheels or venv
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime container
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install runtime PostgreSQL client libraries and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root docta user for container security
RUN useradd -m -u 1000 docta && \
    mkdir -p /app/uploads && \
    chown -R docta:docta /app

# Copy application source code
COPY --chown=docta:docta . /app/

USER docta

EXPOSE 8000

# AWS Fargate container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/bin/sh", "docker/entrypoint.sh"]
