# Multi-stage build for optimized image size
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install UV package manager
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml .
COPY uv.lock* .

# Install dependencies
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    ENVIRONMENT=production

# Create non-root user
RUN useradd -m -u 1000 mcp && \
    mkdir -p /app /data /logs && \
    chown -R mcp:mcp /app /data /logs

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=mcp:mcp /app/.venv /app/.venv

# Copy application code
COPY --chown=mcp:mcp . .

# Switch to non-root user
USER mcp

# Create data directories
RUN mkdir -p /data/mcp_server_template /logs/mcp_server_template

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "-m", "mcp_server_template.main"]