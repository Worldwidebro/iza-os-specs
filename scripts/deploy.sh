#!/bin/bash
# Production deployment script

set -e

echo " Deploying AI Orchestrator to Production"
echo "========================================="

# Check prerequisites
check_deployment_prereqs() {
    echo " Checking deployment prerequisites..."
    
    required_tools=("kubectl" "helm" "docker")
    for tool in "${required_tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            echo "❌ $tool is required but not installed"
            exit 1
        fi
    done
    
    # Check cluster access
    if ! kubectl cluster-info &> /dev/null; then
        echo "❌ Cannot access Kubernetes cluster"
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Build and push images
build_and_push() {
    echo " Building and pushing Docker images..."
    
    # Get image registry from environment
    REGISTRY=${DOCKER_REGISTRY:-"your-registry.com"}
    
    # Build orchestrator
    docker build -t $REGISTRY/ai-orchestrator:latest .
    docker push $REGISTRY/ai-orchestrator:latest
    
    # Build agents
    for agent in finance marketing operations; do
        docker build -t $REGISTRY/ai-orchestrator-${agent}:latest agents/${agent}_agent/
        docker push $REGISTRY/ai-orchestrator-${agent}:latest
    done
    
    echo "✅ Images built and pushed"
}

# Deploy infrastructure
deploy_infrastructure() {
    echo " Deploying infrastructure..."
    
    # Apply Kubernetes manifests
    kubectl apply -f kubernetes/namespace.yaml
    kubectl apply -f kubernetes/configmap.yaml
    kubectl apply -f kubernetes/secrets.yaml
    
    # Deploy Redis
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm upgrade --install redis bitnami/redis \
        --namespace ai-orchestrator \
        --set auth.enabled=false \
        --set replica.replicaCount=2
    
    # Deploy Neo4j
    helm repo add neo4j https://helm.neo4j.com/neo4j
    helm upgrade --install neo4j neo4j/neo4j \
        --namespace ai-orchestrator \
        --set neo4j.password=production-password
    
    echo "✅ Infrastructure deployed"
}

# Deploy applications
deploy_applications() {
    echo " Deploying applications..."
    
    # Deploy orchestrator
    kubectl apply -f kubernetes/orchestrator-deployment.yaml
    kubectl apply -f kubernetes/orchestrator-service.yaml
    
    # Wait for rollout
    kubectl rollout status deployment/orchestrator -n ai-orchestrator
    
    echo "✅ Applications deployed"
}

# Run health checks
run_health_checks() {
    echo " Running health checks..."
    
    # Wait for services to be ready
    kubectl wait --for=condition=ready pod -l app=orchestrator -n ai-orchestrator --timeout=300s
    
    # Get load balancer IP
    EXTERNAL_IP=$(kubectl get service orchestrator-service -n ai-orchestrator -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -z "$EXTERNAL_IP" ]; then
        echo "⏳ Waiting for load balancer IP..."
        sleep 30
        EXTERNAL_IP=$(kubectl get service orchestrator-service -n ai-orchestrator -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    fi
    
    # Health check
    if curl -f http://$EXTERNAL_IP/health; then
        echo "✅ Health check passed"
        echo " System available at: http://$EXTERNAL_IP"
    else
        echo "❌ Health check failed"
        exit 1
    fi
}

# Main deployment function
main() {
    check_deployment_prereqs
    build_and_push
    deploy_infrastructure
    deploy_applications
    run_health_checks
    
    echo ""
    echo " Deployment completed successfully!"
    echo ""
    echo " Monitor your deployment:"
    echo "  kubectl get pods -n ai-orchestrator"
    echo "  kubectl logs -f deployment/orchestrator -n ai-orchestrator"
    echo ""
    echo " Useful commands:"
    echo "  kubectl port-forward service/orchestrator-service 8000:80 -n ai-orchestrator"
    echo "  kubectl exec -it deployment/orchestrator -n ai-orchestrator -- /bin/bash"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
