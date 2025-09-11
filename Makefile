# Makefile for AI Orchestrator management

.PHONY: help setup start stop status test clean dev deploy

help: ## Show this help message
	@echo "AI Orchestrator Management Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $1, $2}'

setup: ## Run initial setup
	@echo " Running setup..."
	@chmod +x setup.sh
	@./setup.sh

start: ## Start all services
	@echo "▶️ Starting AI Orchestrator..."
	@./scripts/start.sh

stop: ## Stop all services
	@echo "⏹️ Stopping AI Orchestrator..."
	@./scripts/stop.sh

status: ## Check system status
	@echo " Checking system status..."
	@./scripts/status.sh

test: ## Run tests
	@echo " Running tests..."
	@./scripts/test.sh

clean: ## Clean up containers and volumes
	@echo " Cleaning up..."
	@docker-compose down -v
	@docker system prune -f

dev: ## Start in development mode
	@echo "️ Starting development mode..."
	@./scripts/dev.sh

logs: ## Show logs for all services
	@docker-compose logs -f

logs-orchestrator: ## Show orchestrator logs
	@docker-compose logs -f orchestrator

logs-agents: ## Show agent logs
	@docker-compose logs -f finance-agent marketing-agent operations-agent

build: ## Build all images
	@echo " Building images..."
	@docker-compose build

deploy: ## Deploy to production
	@echo " Deploying to production..."
	@./scripts/deploy.sh

health: ## Quick health check
	@curl -s http://localhost:8000/health | jq .

demo: ## Run demo tasks
	@echo " Running demo tasks..."
	@echo "Financial Analysis:"
	@curl -X POST http://localhost:8000/execute \
	-H "Content-Type: application/json" \
	-d '{"content": "analyze our Q4 financial performance", "priority": 1}' | jq .
	@echo ""
	@echo "Marketing Campaign:"
	@curl -X POST http://localhost:8000/execute \
	-H "Content-Type: application/json" \
	-d '{"content": "create marketing campaign analysis", "priority": 1}' | jq .
