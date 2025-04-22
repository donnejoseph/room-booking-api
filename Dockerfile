FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PATH="/app/.venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Run as non-root user for better security
RUN addgroup --system appgroup && \
    adduser --system --no-create-home --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app
USER appuser

# Port where the Django app runs
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/swagger/ || exit 1

# Set default environment values if not provided
ENV DEBUG=${DEBUG:-False} \
    ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost,127.0.0.1} \
    DB_HOST=${DB_HOST:-db} \
    DB_PORT=${DB_PORT:-5432}

# Start the application
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2"] 