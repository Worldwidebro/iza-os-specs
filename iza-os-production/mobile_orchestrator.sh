#!/bin/bash

# Mobile-Optimized Unified Orchestrator

echo "📱 Starting Mobile Unified Orchestrator..."

# Load mobile environment
if [ -f .env.mobile ]; then
    export $(cat .env.mobile | grep -v '^#' | xargs)
fi

# Run with mobile-optimized timeout
cd /Users/divinejohns/memU
timeout 60 python UNIFIED_ORCHESTRATOR.py || echo "Orchestrator completed or timed out"
