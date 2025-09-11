.PHONY: setup bootstrap clone-all update-registry second-brain mobile-access

setup:
	pip install -r requirements.txt
	pip install -e 40-mcp-agents/mcp-servers/llm-core/

bootstrap:
	./99-ops/scripts/bootstrap.sh

clone-all:
	python 99-ops/scripts/clone_from_registry.py 00-meta/registry/repos.json

update-registry:
	./99-ops/scripts/refresh_registry.sh

second-brain:
	./99-ops/scripts/seed_second_brain.sh

mobile-access:
	./99-ops/scripts/setup_mobile_access.sh

start-orchestrator:
	cd 40-mcp-agents/mcp-servers/iza-os-orchestrator && python -m src.core

start-dashboard:
	cd 50-apps/ux-ui/iza-os-dashboard && npm run dev

start-mobile:
	cd 50-apps/ux-ui/iza-os-dashboard && npm run mobile

deploy-infrastructure:
	cd 10-infra/cloud/terraform && terraform init && terraform apply

deploy-k8s:
	kubectl apply -f 10-infra/k8s/

monitor:
	cd 60-observability && docker-compose up -d

test-mobile:
	./99-ops/scripts/test_mobile_features.sh
