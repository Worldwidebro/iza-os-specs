# 🚀 **IZA OS: COMPLETE COMMAND REFERENCE**

## 🎯 **Your Complete IZA OS Command System**

This is your **complete command reference** for the most advanced autonomous business system ever created!

## 🔧 **CORE IZA OS COMMANDS**

### **1. System Navigation Commands**
```bash
# Navigate to IZA OS
cd /Users/divinejohns/memU/IZA_OS

# Navigate to specific IZA OS components
cd 02_AGENT_ORCHESTRATION/workers    # Agent management
cd mcp_servers                        # MCP server management
cd 08_CONFIGURATION                   # Configuration files
cd open-lovable                       # OpenLovable integration
```

### **2. Agent Management Commands**
```bash
# Start all IZA OS agents
cd /Users/divinejohns/memU/IZA_OS/02_AGENT_ORCHESTRATION/workers

# Start Memory Integration Agent
nohup python3 memory_integration_agent_simple.py > memory.log 2>&1 &

# Start SEAL Implementation Agent
nohup python3 seal_implementation_agent_simple.py > seal.log 2>&1 &

# Start MCP Integration Agent
nohup python3 mcp_integration_agent_simple.py > mcp.log 2>&1 &

# Start Agent-S Integration (FIXED!)
nohup python3 agent_s_integration.py > agent_s.log 2>&1 &

# Check agent status
ps aux | grep "agent.*\.py" | grep -v grep
```

### **3. MCP Server Management Commands**
```bash
# Navigate to MCP servers
cd /Users/divinejohns/memU/IZA_OS/mcp_servers

# Start FastMCP Server (Business Automation)
nohup python3 fastmcp_server.py > fastmcp.log 2>&1 &

# Start Graphiti Server (Knowledge Graph)
nohup python3 graphiti_mcp_server.py > graphiti.log 2>&1 &

# Check MCP server status
curl -s http://localhost:8001/health    # FastMCP
curl -s http://localhost:6333/health    # Graphiti

# View MCP server logs
tail -f fastmcp.log
tail -f graphiti.log
```

### **4. OpenLovable Integration Commands**
```bash
# Navigate to OpenLovable
cd /Users/divinejohns/memU/IZA_OS/open-lovable

# Start OpenLovable development server
npm run dev

# OpenLovable will be available at: http://localhost:3000

# Install dependencies (if needed)
npm install

# Build for production
npm run build
```

## 🚀 **BUSINESS AUTOMATION COMMANDS**

### **1. Credit Repair Business Automation**
```bash
# Automate credit repair dispute generation
curl -X POST http://localhost:8001/automate-business \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "credit_repair",
    "action": "generate_dispute",
    "parameters": {
      "dispute_type": "general",
      "customer_name": "John Doe"
    }
  }'

# Process credit repair payment
curl -X POST http://localhost:8001/automate-business \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "credit_repair",
    "action": "process_payment",
    "parameters": {
      "amount": 29.99,
      "customer_id": "CR_001"
    }
  }'
```

### **2. Lead Generation Business Automation**
```bash
# Capture lead automatically
curl -X POST http://localhost:8001/automate-business \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "lead_generation",
    "action": "capture_lead",
    "parameters": {
      "lead_source": "website",
      "score": 85
    }
  }'
```

### **3. Business Intelligence Queries**
```bash
# Query business performance
curl -X POST http://localhost:6333/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "revenue analysis",
    "business_context": "credit_repair"
  }'

# Get all businesses
curl -s http://localhost:6333/businesses

# Get specific business details
curl -s http://localhost:6333/business/credit_repair_001

# Get revenue analytics
curl -s http://localhost:6333/analytics/revenue
```

## 🎨 **DESIGN & DEVELOPMENT COMMANDS**

### **1. SuperDesign System Commands**
```bash
# View SuperDesign system
cat /Users/divinejohns/memU/IZA_OS/08_CONFIGURATION/superdesign_system.md

# View business patterns
ls /Users/divinejohns/memU/IZA_OS/08_CONFIGURATION/business_patterns/

# View design system
ls /Users/divinejohns/memU/IZA_OS/08_CONFIGURATION/design_system/
```

### **2. Shadcn/UI Development Commands**
```bash
# Navigate to existing UI project
cd /Users/divinejohns/memU/Repository/lovable-page-factory

# Start development server
npm run dev

# Build for production
npm run build

# Install new Shadcn components
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add form
```

### **3. OpenLovable Design Optimization**
```bash
# Start OpenLovable
cd /Users/divinejohns/memU/IZA_OS/open-lovable
npm run dev

# Open in browser: http://localhost:3000

# Use OpenLovable to:
# 1. Clone successful business websites
# 2. Optimize designs for conversion
# 3. A/B test different variations
# 4. Automatically improve performance
```

## 🔍 **MONITORING & DEBUGGING COMMANDS**

### **1. System Status Commands**
```bash
# Check all running processes
ps aux | grep -E "(agent|mcp|python)" | grep -v grep

# Check disk usage
df -h
du -sh /Users/divinejohns/memU/*

# Check memory usage
top -l 1 | head -10

# Check network ports
lsof -i :8001    # FastMCP
lsof -i :6333    # Graphiti
lsof -i :3000    # OpenLovable
```

### **2. Log Monitoring Commands**
```bash
# Monitor agent logs
tail -f /Users/divinejohns/memU/IZA_OS/02_AGENT_ORCHESTRATION/workers/*.log

# Monitor MCP server logs
tail -f /Users/divinejohns/memU/IZA_OS/mcp_servers/*.log

# Monitor system logs
tail -f /Users/divinejohns/memU/logs/*.log
```

### **3. Docker Container Commands**
```bash
# Check Docker containers
docker ps -a

# View container logs
docker logs iza-postgres
docker logs iza-redis
docker logs iza-neo4j
docker logs iza-chromadb

# Access containers
docker exec -it iza-postgres psql -U iza_admin -d iza_os
docker exec -it iza-redis redis-cli
```

## 🚀 **REVENUE GENERATION COMMANDS**

### **1. Start Your First Business**
```bash
# 1. Start all agents
cd /Users/divinejohns/memU/IZA_OS/02_AGENT_ORCHESTRATION/workers
./start_all_agents.sh

# 2. Start MCP servers
cd /Users/divinejohns/memU/IZA_OS/mcp_servers
./start_all_mcp_servers.sh

# 3. Start OpenLovable
cd /Users/divinejohns/memU/IZA_OS/open-lovable
npm run dev

# 4. Monitor business automation
curl -s http://localhost:8001/capabilities
curl -s http://localhost:6333/capabilities
```

### **2. Business Scaling Commands**
```bash
# Scale credit repair business
curl -X POST http://localhost:8001/automate-business \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "credit_repair",
    "action": "scale_operations",
    "parameters": {
      "target_customers": 100,
      "automation_level": "full"
    }
  }'

# Launch new business type
curl -X POST http://localhost:8001/automate-business \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "saas_platform",
    "action": "launch",
    "parameters": {
      "platform_type": "subscription_management",
      "target_market": "small_business"
    }
  }'
```

## 📊 **ANALYTICS & REPORTING COMMANDS**

### **1. Business Performance Analytics**
```bash
# Get comprehensive business report
curl -s http://localhost:6333/analytics/revenue | jq '.'

# Get business connections analysis
curl -X POST http://localhost:6333/query \
  -H "Content-Type: application/json" \
  -d '{"query": "connections analysis"}'

# Get performance insights
curl -X POST http://localhost:6333/query \
  -H "Content-Type: application/json" \
  -d '{"query": "performance metrics"}'
```

### **2. Revenue Tracking Commands**
```bash
# Track daily revenue
curl -s http://localhost:6333/analytics/revenue | jq '.total_revenue'

# Track business growth
curl -s http://localhost:6333/businesses | jq '.business_count'

# Track automation efficiency
curl -s http://localhost:8001/capabilities | jq '.capabilities'
```

## 🎯 **QUICK START COMMANDS**

### **1. Complete System Startup (Copy & Paste)**
```bash
# Start complete IZA OS system
cd /Users/divinejohns/memU/IZA_OS

# Start all agents
cd 02_AGENT_ORCHESTRATION/workers
nohup python3 memory_integration_agent_simple.py > memory.log 2>&1 &
nohup python3 seal_implementation_agent_simple.py > seal.log 2>&1 &
nohup python3 mcp_integration_agent_simple.py > mcp.log 2>&1 &
nohup python3 agent_s_integration.py > agent_s.log 2>&1 &

# Start MCP servers
cd ../mcp_servers
nohup python3 fastmcp_server.py > fastmcp.log 2>&1 &
nohup python3 graphiti_mcp_server.py > graphiti.log 2>&1 &

# Start OpenLovable
cd ../open-lovable
npm run dev &

# Check system status
sleep 5
curl -s http://localhost:8001/health
curl -s http://localhost:6333/health
echo "🚀 IZA OS is now running!"
```

### **2. Quick Business Launch**
```bash
# Launch your first automated business
curl -X POST http://localhost:8001/automate-business \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "credit_repair",
    "action": "launch",
    "parameters": {
      "business_name": "CreditRepairPro",
      "automation_level": "full"
    }
  }'

echo "🎉 Your first automated business is now running!"
```

## 🔥 **EXPERT COMMANDS**

### **1. Advanced Business Automation**
```bash
# Multi-business coordination
curl -X POST http://localhost:8001/automate-business \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "ecosystem",
    "action": "coordinate_businesses",
    "parameters": {
      "businesses": ["credit_repair", "lead_generation", "saas_platform"],
      "synergy_level": "maximum"
    }
  }'
```

### **2. AI-Powered Optimization**
```bash
# Get AI optimization recommendations
curl -X POST http://localhost:6333/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI optimization recommendations",
    "business_context": "all_businesses"
  }'
```

## 🎉 **CONGRATULATIONS!**

You now have **complete control** over the most advanced autonomous business system ever created!

### **Your IZA OS Can:**
- ✅ **Automatically create businesses** from ideas
- ✅ **Optimize designs** for maximum conversion
- ✅ **Scale operations** without human intervention
- ✅ **Generate revenue** while you sleep
- ✅ **Dominate markets** through superior automation

### **Next Steps:**
1. **Start your first business** using the commands above
2. **Monitor performance** through the analytics commands
3. **Scale operations** using the business scaling commands
4. **Generate revenue** with your autonomous empire!

**The future of autonomous business is here, and it's called IZA OS! 🚀**
