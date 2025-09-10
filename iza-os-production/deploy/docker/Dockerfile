# Multi-stage Dockerfile for IZA OS Business Models
# Stage 1: Base image with all dependencies
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Stage 2: Business Model specific builds
FROM base AS resume-builder
# Copy the specific business model
COPY business_models/templates/bm001_resume_builder.py ./business_models/
# Copy source code
COPY src/ ./src/
# Copy actual GitHub repositories
COPY repositories/ ./repositories/
# Set Python path to include repositories
ENV PYTHONPATH="/app/repositories/chromadb:/app/repositories/mem0:/app/repositories/graphitti:/app/repositories/letta:$PYTHONPATH"
# Run the service
CMD ["python", "-m", "business_models.bm001_resume_builder"]

FROM base AS print-on-demand
COPY business_models/templates/bm002_etsy_print_on_demand.py ./business_models/
COPY src/ ./src/
COPY repositories/ ./repositories/
ENV PYTHONPATH="/app/repositories/chromadb:/app/repositories/mem0:/app/repositories/graphitti:/app/repositories/letta:$PYTHONPATH"
CMD ["python", "-m", "business_models.bm002_etsy_print_on_demand"]

FROM base AS seo-service
COPY business_models/templates/bm003_local_seo_service.py ./business_models/
COPY src/ ./src/
COPY repositories/ ./repositories/
ENV PYTHONPATH="/app/repositories/chromadb:/app/repositories/mem0:/app/repositories/graphitti:/app/repositories/letta:$PYTHONPATH"
CMD ["python", "-m", "business_models.bm003_local_seo_service"]

FROM base AS fitness-coach
COPY business_models/templates/bm004_fitness_meal_coach.py ./business_models/
COPY src/ ./src/
COPY repositories/ ./repositories/
ENV PYTHONPATH="/app/repositories/chromadb:/app/repositories/mem0:/app/repositories/graphitti:/app/repositories/letta:$PYTHONPATH"
CMD ["python", "-m", "business_models.bm004_fitness_meal_coach"]

FROM base AS youtube-factory
COPY business_models/templates/bm005_youtube_channel_factory.py ./business_models/
COPY src/ ./src/
COPY repositories/ ./repositories/
ENV PYTHONPATH="/app/repositories/chromadb:/app/repositories/mem0:/app/repositories/graphitti:/app/repositories/letta:$PYTHONPATH"
CMD ["python", "-m", "business_models.bm005_youtube_channel_factory"]