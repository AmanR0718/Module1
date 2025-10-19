# ============================================================
#  Zambian Farmer Backend — Final working bcrypt build
# ============================================================

FROM python:3.11-bookworm

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# ------------------------------------------------------------
# Install full build toolchain and modern Rust (for bcrypt)
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        python3-dev \
        curl \
    && curl https://sh.rustup.rs -sSf | bash -s -- -y \
    && . "$HOME/.cargo/env" \
    && rustup install stable \
    && rustup default stable \
    && echo 'export PATH=$HOME/.cargo/bin:$PATH' >> /root/.bashrc \
    && export PATH=$HOME/.cargo/bin:$PATH \
    && python3 -m pip install --upgrade pip setuptools wheel \
    # Force bcrypt source build with native C extension
    && python3 -m pip install --no-binary bcrypt --no-cache-dir --force-reinstall bcrypt==4.1.3 passlib[bcrypt]==1.7.4 \
    && apt-get purge -y build-essential python3-dev \
    && apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*


# ============================================
# Copy application files
# ============================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


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
