#!/bin/bash
# IZA OS Business Models Deployment Script
# Deploys all 5 business models to production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
BUSINESS_MODELS=("resume-builder" "print-on-demand" "seo-service" "fitness-coach" "youtube-factory")
DOCKER_COMPOSE_FILE="deploy/docker/docker-compose.${ENVIRONMENT}.yml"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if environment file exists
    if [ ! -f ".env.${ENVIRONMENT}" ]; then
        log_warning "Environment file .env.${ENVIRONMENT} not found. Creating template..."
        create_env_template
    fi
    
    log_success "Prerequisites check passed"
}

create_env_template() {
    cat > ".env.${ENVIRONMENT}" << EOF
# IZA OS Business Models Environment Configuration
# Environment: ${ENVIRONMENT}

# Database Configuration
POSTGRES_USER=iza_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=iza_os_${ENVIRONMENT}

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# API Keys
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
GOOGLE_API_KEY=your_google_api_key
GMB_API_KEY=your_gmb_api_key
SERP_API_KEY=your_serp_api_key
NUTRITION_API_KEY=your_nutrition_api_key
FITNESS_API_KEY=your_fitness_api_key
PUSH_NOTIFICATION_KEY=your_push_notification_key

# Business Model Specific Keys
PRINTFUL_API_KEY=your_printful_api_key
ETSY_API_KEY=your_etsy_api_key
SHOPIFY_API_KEY=your_shopify_api_key
YOUTUBE_API_KEY=your_youtube_api_key

# Monitoring
ALERT_WEBHOOK_URL=https://hooks.slack.com/your-webhook-url
EMAIL_ALERTS=alerts@yourcompany.com

# Security
JWT_SECRET_KEY=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key
EOF
    
    log_warning "Please update .env.${ENVIRONMENT} with your actual API keys before deploying"
}

build_images() {
    log_info "Building Docker images for all business models..."
    
    for model in "${BUSINESS_MODELS[@]}"; do
        log_info "Building image for ${model}..."
        
        docker build \
            -t iza-os/${model}:${ENVIRONMENT} \
            -f deploy/docker/Dockerfile \
            --target ${model} \
            .
        
        if [ $? -eq 0 ]; then
            log_success "Successfully built image for ${model}"
        else
            log_error "Failed to build image for ${model}"
            exit 1
        fi
    done
    
    log_success "All Docker images built successfully"
}

run_tests() {
    log_info "Running tests for all business models..."
    
    for model in "${BUSINESS_MODELS[@]}"; do
        log_info "Running tests for ${model}..."
        
        # Run tests in Docker container
        docker run --rm \
            -v $(pwd)/tests:/app/tests \
            iza-os/${model}:${ENVIRONMENT} \
            python -m pytest tests/business_models/test_${model}.py -v
        
        if [ $? -eq 0 ]; then
            log_success "Tests passed for ${model}"
        else
            log_error "Tests failed for ${model}"
            exit 1
        fi
    done
    
    log_success "All tests passed"
}

deploy_services() {
    log_info "Deploying services to ${ENVIRONMENT} environment..."
    
    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose -f ${DOCKER_COMPOSE_FILE} down
    
    # Start services
    log_info "Starting services..."
    docker-compose -f ${DOCKER_COMPOSE_FILE} up -d
    
    if [ $? -eq 0 ]; then
        log_success "Services deployed successfully"
    else
        log_error "Failed to deploy services"
        exit 1
    fi
}

wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    for model in "${BUSINESS_MODELS[@]}"; do
        port=$((8000 + ${#BUSINESS_MODELS[@]} - $(printf '%s\n' "${BUSINESS_MODELS[@]}" | grep -n "^${model}$" | cut -d: -f1) + 1))
        
        log_info "Waiting for ${model} on port ${port}..."
        
        max_attempts=30
        attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -f http://localhost:${port}/health > /dev/null 2>&1; then
                log_success "${model} is ready"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                log_error "${model} failed to start after ${max_attempts} attempts"
                exit 1
            fi
            
            log_info "Attempt ${attempt}/${max_attempts} - waiting for ${model}..."
            sleep 10
            attempt=$((attempt + 1))
        done
    done
    
    log_success "All services are ready"
}

run_health_checks() {
    log_info "Running comprehensive health checks..."
    
    for model in "${BUSINESS_MODELS[@]}"; do
        port=$((8000 + ${#BUSINESS_MODELS[@]} - $(printf '%s\n' "${BUSINESS_MODELS[@]}" | grep -n "^${model}$" | cut -d: -f1) + 1))
        
        log_info "Health check for ${model}..."
        
        # Basic health check
        response=$(curl -s http://localhost:${port}/health)
        if echo "$response" | grep -q "healthy"; then
            log_success "${model} health check passed"
        else
            log_error "${model} health check failed"
            exit 1
        fi
        
        # Performance check
        response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:${port}/health)
        if (( $(echo "$response_time < 1.0" | bc -l) )); then
            log_success "${model} performance check passed (${response_time}s)"
        else
            log_warning "${model} performance check warning (${response_time}s)"
        fi
    done
    
    log_success "All health checks completed"
}

setup_monitoring() {
    log_info "Setting up monitoring and alerting..."
    
    # Start monitoring service
    docker-compose -f ${DOCKER_COMPOSE_FILE} up -d monitoring
    
    # Wait for monitoring to be ready
    sleep 10
    
    # Run initial monitoring check
    docker-compose -f ${DOCKER_COMPOSE_FILE} exec monitoring python -m src.monitoring.monitoring_system
    
    log_success "Monitoring setup completed"
}

setup_monetization() {
    log_info "Setting up monetization system..."
    
    # Start monetization service
    docker-compose -f ${DOCKER_COMPOSE_FILE} up -d monetization
    
    # Wait for monetization to be ready
    sleep 10
    
    # Initialize monetization system
    docker-compose -f ${DOCKER_COMPOSE_FILE} exec monetization python -m src.monetization.monetization_system
    
    log_success "Monetization system setup completed"
}

show_deployment_summary() {
    log_info "Deployment Summary"
    echo "=================================="
    echo "Environment: ${ENVIRONMENT}"
    echo "Business Models Deployed:"
    
    for model in "${BUSINESS_MODELS[@]}"; do
        port=$((8000 + ${#BUSINESS_MODELS[@]} - $(printf '%s\n' "${BUSINESS_MODELS[@]}" | grep -n "^${model}$" | cut -d: -f1) + 1))
        echo "  - ${model}: http://localhost:${port}"
    done
    
    echo ""
    echo "Monitoring Dashboard: http://localhost:3000"
    echo "Monetization Dashboard: http://localhost:3001"
    echo ""
    echo "To view logs: docker-compose -f ${DOCKER_COMPOSE_FILE} logs -f"
    echo "To stop services: docker-compose -f ${DOCKER_COMPOSE_FILE} down"
    echo "=================================="
}

cleanup() {
    log_info "Cleaning up..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    log_info "Starting IZA OS Business Models deployment..."
    log_info "Environment: ${ENVIRONMENT}"
    
    # Check prerequisites
    check_prerequisites
    
    # Build images
    build_images
    
    # Run tests
    run_tests
    
    # Deploy services
    deploy_services
    
    # Wait for services to be ready
    wait_for_services
    
    # Run health checks
    run_health_checks
    
    # Setup monitoring
    setup_monitoring
    
    # Setup monetization
    setup_monetization
    
    # Cleanup
    cleanup
    
    # Show summary
    show_deployment_summary
    
    log_success "Deployment completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    "staging")
        ENVIRONMENT="staging"
        main
        ;;
    "production")
        ENVIRONMENT="production"
        main
        ;;
    "test")
        log_info "Running tests only..."
        check_prerequisites
        build_images
        run_tests
        log_success "Tests completed"
        ;;
    "clean")
        log_info "Cleaning up deployment..."
        docker-compose -f ${DOCKER_COMPOSE_FILE} down -v
        docker system prune -f
        log_success "Cleanup completed"
        ;;
    "status")
        log_info "Checking deployment status..."
        docker-compose -f ${DOCKER_COMPOSE_FILE} ps
        ;;
    *)
        echo "Usage: $0 {staging|production|test|clean|status}"
        echo ""
        echo "Commands:"
        echo "  staging    - Deploy to staging environment"
        echo "  production - Deploy to production environment"
        echo "  test       - Run tests only"
        echo "  clean      - Clean up deployment"
        echo "  status     - Show deployment status"
        exit 1
        ;;
esac
