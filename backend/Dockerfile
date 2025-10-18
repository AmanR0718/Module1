# ============================================
# Zambian Farmer System - FastAPI Backend
# Base: Python 3.11 slim (lightweight, secure)
# ============================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# ============================================
# Install system dependencies
# ============================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Copy dependency file first (for layer caching)
# ============================================
COPY requirements.txt .

# Upgrade pip & install dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir bcrypt==4.1.3 passlib[bcrypt]==1.7.4 \
    && pip install --no-cache-dir -r requirements.txt


# ============================================
# Copy application source code
# ============================================
COPY . .

# ============================================
# Create necessary directories
# ============================================
RUN mkdir -p /app/uploads /app/uploads/qr_codes /app/logs

# ============================================
# Environment configuration
# ============================================
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH" \
    APP_HOME=/app \
    TZ=UTC

# ============================================
# Expose API port
# ============================================
EXPOSE 8000

# ============================================
# Healthcheck (optional)
# ============================================
HEALTHCHECK --interval=30s --timeout=5s --retries=5 CMD curl -f http://localhost:8000/docs || exit 1

# ============================================
# Run the FastAPI application using Uvicorn
# ============================================
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
