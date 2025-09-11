#!/bin/bash
# Entrypoint script for IZA OS Business Models

set -e

# Function to wait for database
wait_for_db() {
    echo "Waiting for database to be ready..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 1
    done
    echo "Database is ready!"
}

# Function to run database migrations
run_migrations() {
    echo "Running database migrations..."
    python -c "
import sqlite3
import os
from pathlib import Path

# Create database directory if it doesn't exist
db_dir = Path('/app/data')
db_dir.mkdir(exist_ok=True)

# Initialize databases for each business model
business_models = [
    'resume_builder',
    'print_on_demand', 
    'seo_service',
    'fitness_coach',
    'youtube_factory'
]

for model in business_models:
    db_path = db_dir / f'{model}.db'
    print(f'Initializing database: {db_path}')
    # Database initialization will be handled by each business model
"
}

# Function to start the application
start_app() {
    echo "Starting IZA OS Business Model: $BUSINESS_MODEL"
    
    case $BUSINESS_MODEL in
        "resume-builder")
            python -m business_models.templates.bm001_resume_builder
            ;;
        "print-on-demand")
            python -m business_models.templates.bm002_etsy_print_on_demand
            ;;
        "seo-service")
            python -m business_models.templates.bm003_local_seo_service
            ;;
        "fitness-coach")
            python -m business_models.templates.bm004_fitness_meal_coach
            ;;
        "youtube-factory")
            python -m business_models.templates.bm005_youtube_channel_factory
            ;;
        *)
            echo "Starting main application..."
            python -m src.main
            ;;
    esac
}

# Main execution
main() {
    echo "IZA OS Business Model Container Starting..."
    echo "Business Model: ${BUSINESS_MODEL:-main}"
    echo "Environment: ${ENVIRONMENT:-development}"
    
    # Wait for database if configured
    if [ ! -z "$DB_HOST" ]; then
        wait_for_db
    fi
    
    # Run migrations
    run_migrations
    
    # Start the application
    start_app
}

# Execute main function
main "$@"
