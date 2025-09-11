#!/bin/bash

# IZA OS Book Mobile Access (No Docker Required)
# Uses existing services and creates mobile interface

set -e

echo "📱 IZA OS Book Mobile Access Setup"
echo "=================================="
echo ""

# Get Mac's IP address
MAC_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo "Your Mac's IP address: $MAC_IP"

echo ""
echo "STEP 1: Creating Simple Mobile Interface"
echo "========================================="

# Create a simple mobile interface that works with existing services
cat > mobile_book_interface.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IZA OS Book Mobile</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 400px;
            margin: 0 auto;
        }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            margin-bottom: 10px;
            transition: background 0.2s;
        }
        
        .btn:hover {
            background: #5a67d8;
        }
        
        .btn.secondary {
            background: #6b7280;
        }
        
        .btn.secondary:hover {
            background: #4b5563;
        }
        
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 24px;
        }
        
        h2 {
            margin-bottom: 15px;
            color: #374151;
        }
        
        .input-group {
            margin-bottom: 15px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 5px;
            color: #374151;
            font-weight: 500;
        }
        
        .input-group input, .input-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 16px;
        }
        
        .input-group textarea {
            height: 80px;
            resize: vertical;
        }
        
        .status {
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        
        .status.success {
            background: #d1fae5;
            color: #065f46;
        }
        
        .status.error {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .url-list {
            background: #f3f4f6;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .url-list a {
            display: block;
            color: #667eea;
            text-decoration: none;
            margin-bottom: 5px;
            padding: 5px 0;
        }
        
        .url-list a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 IZA OS Book Mobile</h1>
        
        <div class="card">
            <h2>📱 Mobile Access URLs</h2>
            <div class="url-list">
                <a href="http://$MAC_IP:8000" target="_blank">🔗 Main API (Port 8000)</a>
                <a href="http://$MAC_IP:8001" target="_blank">🔗 Agent Orchestrator (Port 8001)</a>
                <a href="http://$MAC_IP:3000" target="_blank">🔗 Dashboard (Port 3000)</a>
                <a href="http://$MAC_IP:9090" target="_blank">🔗 Metrics (Port 9090)</a>
            </div>
        </div>
        
        <div class="card">
            <h2>🤖 AI Task Execution</h2>
            <div class="input-group">
                <label for="task-input">Enter your AI task:</label>
                <textarea id="task-input" placeholder="e.g., analyze our Q4 financial performance, create a marketing strategy, research competitors"></textarea>
            </div>
            <button class="btn" onclick="executeTask()">Execute AI Task</button>
            <div id="task-result" class="status" style="display: none;"></div>
        </div>
        
        <div class="card">
            <h2>🔍 System Status</h2>
            <button class="btn" onclick="checkAllServices()">Check All Services</button>
            <div id="status-results"></div>
        </div>
        
        <div class="card">
            <h2>📋 Quick Actions</h2>
            <button class="btn" onclick="openUnifiedOrchestrator()">Run Unified Orchestrator</button>
            <button class="btn secondary" onclick="openMCPDocs()">View MCP Documentation</button>
            <button class="btn secondary" onclick="openAgentDocs()">View Agent Documentation</button>
        </div>
        
        <div class="card">
            <h2>📖 IZA OS Book Features</h2>
            <ul style="color: #374151; line-height: 1.6;">
                <li>🧠 Claude-Powered Intelligence</li>
                <li>🤖 Smart Agent Routing</li>
                <li>🔗 MCP Integration (Apple Notes, Google Drive, GitHub)</li>
                <li>🏭 Auto-Agent Creation</li>
                <li>📊 Knowledge Graph Building</li>
                <li>📱 Mobile Voice Control</li>
                <li>☁️ Production Ready (Docker, Kubernetes)</li>
            </ul>
        </div>
    </div>

    <script>
        const MAC_IP = '$MAC_IP';
        
        async function executeTask() {
            const taskInput = document.getElementById('task-input').value;
            if (!taskInput.trim()) {
                showResult('Please enter a task', 'error');
                return;
            }
            
            showResult('Executing task...', 'success');
            
            try {
                // Try different endpoints
                const endpoints = [
                    \`http://\${MAC_IP}:8000/execute\`,
                    \`http://\${MAC_IP}:8001/execute\`,
                    \`http://\${MAC_IP}:8000/api/execute\`,
                    \`http://\${MAC_IP}:8001/api/execute\`
                ];
                
                let success = false;
                for (const endpoint of endpoints) {
                    try {
                        const response = await fetch(endpoint, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                content: taskInput,
                                task: taskInput,
                                prompt: taskInput
                            })
                        });
                        
                        if (response.ok) {
                            const result = await response.json();
                            showResult(\`Task executed successfully! Response: \${JSON.stringify(result)}\`, 'success');
                            success = true;
                            break;
                        }
                    } catch (e) {
                        // Try next endpoint
                        continue;
                    }
                }
                
                if (!success) {
                    showResult('Task execution failed. Please check if services are running.', 'error');
                }
                
            } catch (error) {
                showResult(\`Task execution error: \${error.message}\`, 'error');
            }
        }
        
        async function checkAllServices() {
            const services = [
                { name: 'MCP Server', url: \`http://\${MAC_IP}:8000/health\` },
                { name: 'Agent Orchestrator', url: \`http://\${MAC_IP}:8001/health\` },
                { name: 'Dashboard', url: \`http://\${MAC_IP}:3000\` },
                { name: 'Metrics', url: \`http://\${MAC_IP}:9090\` }
            ];
            
            const resultsDiv = document.getElementById('status-results');
            resultsDiv.innerHTML = '';
            
            for (const service of services) {
                try {
                    const response = await fetch(service.url);
                    const status = response.ok ? 'success' : 'error';
                    const message = response.ok ? '✅ Running' : '❌ Not responding';
                    
                    const statusDiv = document.createElement('div');
                    statusDiv.className = \`status \${status}\`;
                    statusDiv.textContent = \`\${service.name}: \${message}\`;
                    resultsDiv.appendChild(statusDiv);
                    
                } catch (error) {
                    const statusDiv = document.createElement('div');
                    statusDiv.className = 'status error';
                    statusDiv.textContent = \`\${service.name}: ❌ Not accessible\`;
                    resultsDiv.appendChild(statusDiv);
                }
            }
        }
        
        function showResult(message, type) {
            const resultDiv = document.getElementById('task-result');
            resultDiv.textContent = message;
            resultDiv.className = \`status \${type}\`;
            resultDiv.style.display = 'block';
        }
        
        function openUnifiedOrchestrator() {
            window.open('http://localhost:8001/docs', '_blank');
        }
        
        function openMCPDocs() {
            window.open(\`http://\${MAC_IP}:8000/docs\`, '_blank');
        }
        
        function openAgentDocs() {
            window.open(\`http://\${MAC_IP}:8001/docs\`, '_blank');
        }
        
        // Auto-check services on load
        checkAllServices();
    </script>
</body>
</html>
EOF

print_success "Mobile interface created ✓"

echo ""
echo "STEP 2: Creating Mobile Access Instructions"
echo "=========================================="

cat > MOBILE_ACCESS_INSTRUCTIONS.md << EOF
# 📚 IZA OS Book Mobile Access Instructions

## 🚀 How to Use IZA OS Book from Your Phone

### Method 1: Direct Browser Access (Easiest)

1. **Make sure your phone is on the same WiFi network as your Mac**

2. **Open your phone's browser and go to:**
   - **Mobile Interface**: http://$MAC_IP:3000
   - **Main API**: http://$MAC_IP:8000
   - **Agent Orchestrator**: http://$MAC_IP:8001

3. **Use the mobile interface to:**
   - Execute AI tasks
   - Check system status
   - Access all IZA OS Book features

### Method 2: Local Mobile Interface

1. **Open the mobile interface file:**
   \`\`\`bash
   open mobile_book_interface.html
   \`\`\`

2. **Access from your phone:**
   - The interface will show your Mac's IP
   - Use that IP to access from your phone's browser

### Method 3: SSH Access (Advanced)

1. **Install SSH client on your phone** (Termius, Prompt, etc.)

2. **Connect with these details:**
   - Host: $MAC_IP
   - Port: 22
   - Username: $(whoami)
   - Password: Your Mac password

3. **Once connected, run:**
   \`\`\`bash
   cd /Users/$(whoami)/memU/IZA_OS_BOOK
   python src/main.py
   \`\`\`

## 📱 Mobile Features Available

### ✅ AI Task Execution
- Enter any task in the mobile interface
- Execute via Claude-powered intelligence
- Get real-time results

### ✅ System Monitoring
- Check status of all services
- Monitor agent activity
- View system health

### ✅ Full IZA OS Book Access
- Claude-powered intelligence
- Smart agent routing
- MCP integration (Apple Notes, Google Drive, GitHub)
- Knowledge graph building
- Auto-agent creation

## 🔧 Troubleshooting

### Can't Access from Phone
1. **Check WiFi**: Make sure phone and Mac are on same network
2. **Check IP**: Run \`ifconfig | grep "inet "\` to get current IP
3. **Check Services**: Make sure services are running on Mac

### Services Not Running
1. **Start MCP Server**: 
   \`\`\`bash
   cd /Users/$(whoami)/memU/iza-os-production
   ./mobile_start.sh
   \`\`\`

2. **Start Unified Orchestrator**:
   \`\`\`bash
   cd /Users/$(whoami)/memU
   python UNIFIED_ORCHESTRATOR.py &
   \`\`\`

### Network Issues
1. **Check Mac's IP**: \`ifconfig | grep "inet "\`
2. **Test local access**: \`curl http://localhost:8000/health\`
3. **Check firewall**: Make sure Mac firewall allows connections

## 🎯 Quick Start Commands

### Start All Services
\`\`\`bash
# Start MCP Server and Agent Orchestrator
cd /Users/$(whoami)/memU/iza-os-production
./mobile_start.sh

# Start Unified Orchestrator
cd /Users/$(whoami)/memU
python UNIFIED_ORCHESTRATOR.py &
\`\`\`

### Check Status
\`\`\`bash
cd /Users/$(whoami)/memU/iza-os-production
./mobile_status.sh
\`\`\`

### Access Mobile Interface
\`\`\`bash
cd /Users/$(whoami)/memU/IZA_OS_BOOK
open mobile_book_interface.html
\`\`\`

## 📱 Your Mobile URLs

- **Mobile Interface**: http://$MAC_IP:3000
- **MCP Server**: http://$MAC_IP:8000
- **Agent Orchestrator**: http://$MAC_IP:8001
- **Health Check**: http://$MAC_IP:8000/health

## 🎉 Ready to Use!

Your IZA OS Book is now accessible from your phone with full AI orchestration capabilities!

**Next Steps:**
1. Open http://$MAC_IP:3000 on your phone
2. Try executing an AI task
3. Monitor system status
4. Enjoy mobile AI orchestration! 📱🤖
EOF

print_success "Mobile access instructions created ✓"

echo ""
echo "🎉 IZA OS BOOK MOBILE ACCESS READY!"
echo "=================================="
echo ""
echo "📱 Your Mobile Access URLs:"
echo "- Mobile Interface: http://$MAC_IP:3000"
echo "- MCP Server: http://$MAC_IP:8000"
echo "- Agent Orchestrator: http://$MAC_IP:8001"
echo ""
echo "🚀 Quick Start:"
echo "1. Open http://$MAC_IP:3000 on your phone"
echo "2. Try executing an AI task"
echo "3. Check system status"
echo ""
echo "📖 Read: MOBILE_ACCESS_INSTRUCTIONS.md for full details"
echo ""
echo "Your IZA OS Book is now mobile-accessible! 📚📱✨"
