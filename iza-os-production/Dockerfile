# IZA OS - Multi-stage Docker Build
# Optimized for mobile development and production deployment

# =============================================================================
# BASE STAGE - Python and Node.js environment
# =============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    NODE_VERSION=18.18.2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Create app user
RUN useradd --create-home --shell /bin/bash iza && \
    mkdir -p /app && \
    chown -R iza:iza /app

# Set working directory
WORKDIR /app

# =============================================================================
# DEPENDENCIES STAGE - Install Python and Node.js dependencies
# =============================================================================
FROM base as dependencies

# Copy dependency files
COPY requirements.txt package.json package-lock.json ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies
RUN npm ci --only=production && npm cache clean --force

# =============================================================================
# DEVELOPMENT STAGE - For local development with hot reload
# =============================================================================
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    isort \
    flake8 \
    mypy \
    pre-commit

# Install Node.js dev dependencies
RUN npm ci && npm cache clean --force

# Copy application code
COPY --chown=iza:iza . .

# Switch to app user
USER iza

# Expose ports
EXPOSE 3000 8000

# Development command with hot reload
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]

# =============================================================================
# BUILD STAGE - Build frontend and prepare for production
# =============================================================================
FROM dependencies as build

# Copy source code
COPY --chown=iza:iza . .

# Build frontend assets (if any)
RUN npm run build || echo "No build script found"

# Build Python wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# =============================================================================
# PRODUCTION STAGE - Final optimized image
# =============================================================================
FROM python:3.11-slim as production

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=production \
    PORT=3000

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user
RUN useradd --create-home --shell /bin/bash --uid 1000 iza

# Create app directory
WORKDIR /app

# Copy Python wheels and install
COPY --from=build /app/wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --find-links /wheels -r requirements.txt \
    && rm -rf /wheels

# Copy built application
COPY --from=build --chown=iza:iza /app/src ./src
COPY --from=build --chown=iza:iza /app/scripts ./scripts
COPY --from=build --chown=iza:iza /app/config ./config
COPY --from=build --chown=iza:iza /app/package.json .

# Copy build artifacts
COPY --from=build --chown=iza:iza /app/dist ./dist 2>/dev/null || true
COPY --from=build --chown=iza:iza /app/build ./build 2>/dev/null || true

# Create necessary directories
RUN mkdir -p logs temp_files generated && \
    chown -R iza:iza /app

# Switch to app user
USER iza

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Production command
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3000", "--workers", "4"]

# =============================================================================
# MOBILE DEVELOPMENT STAGE - Optimized for Cursor and mobile workflows
# =============================================================================
FROM development as mobile

# Install mobile development tools
RUN npm install -g @expo/cli

# Copy mobile-specific configurations
COPY --chown=iza:iza .cursor .cursor/
COPY --chown=iza:iza mobile mobile/

# Install mobile dependencies
WORKDIR /app/mobile
RUN npm install 2>/dev/null || echo "No mobile dependencies found"

# Switch back to app directory
WORKDIR /app

# Mobile development command
CMD ["sh", "-c", "python src/main.py --cli & npm run mobile:web"]

# =============================================================================
# LABELS AND METADATA
# =============================================================================
LABEL maintainer="Divine Johns <divine@iza-os.dev>" \
      version="1.0.0" \
      description="IZA OS - Intelligent Zero-Administration Operating System" \
      org.opencontainers.image.title="IZA OS" \
      org.opencontainers.image.description="Your AI CEO that finds problems, launches ventures, and generates income" \
      org.opencontainers.image.url="https://iza-os.dev" \
      org.opencontainers.image.source="https://github.com/Worldwidebro/iza-os" \
      org.opencontainers.image.vendor="IZA OS" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.created="2024-08-26T05:00:00Z" \
      iza.os.mobile-optimized="true" \
      iza.os.cursor-ready="true"
