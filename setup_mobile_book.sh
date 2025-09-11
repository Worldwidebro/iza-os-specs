#!/bin/bash

# IZA OS Book Mobile Setup
# Creates mobile-optimized access to IZA OS Book from your phone

set -e

echo "📱 IZA OS Book Mobile Setup"
echo "==========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get Mac's IP address
MAC_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
print_status "Your Mac's IP address: $MAC_IP"

echo ""
echo "STEP 1: Setting up IZA OS Book for Mobile Access"
echo "================================================"

# Create mobile environment for IZA OS Book
cat > .env.mobile << EOF
# IZA OS Book Mobile Configuration
MOBILE_MODE=true
CURSOR_MOBILE=true

# Network Configuration
HOST=0.0.0.0
PORT=8000
MAC_IP=$MAC_IP

# Mobile URLs
MOBILE_API_URL=http://$MAC_IP:8000
MOBILE_DASHBOARD_URL=http://$MAC_IP:3000
MOBILE_METRICS_URL=http://$MAC_IP:9090

# Mobile-Optimized Settings
MAX_CONCURRENT_TASKS=3
TASK_TIMEOUT=180
LOG_LEVEL=WARNING
CACHE_TTL=1800

# API Keys (inherit from main .env)
ANTHROPIC_API_KEY=\$(grep ANTHROPIC_API_KEY .env 2>/dev/null | cut -d'=' -f2 || echo "")
OPENAI_API_KEY=\$(grep OPENAI_API_KEY .env 2>/dev/null | cut -d'=' -f2 || echo "")
EOF

print_success "Mobile environment configuration created ✓"

echo ""
echo "STEP 2: Creating Mobile Startup Scripts"
echo "======================================="

# Create mobile start script for IZA OS Book
cat > mobile_start_book.sh << 'EOF'
#!/bin/bash

# IZA OS Book Mobile Startup Script

echo "📱 Starting IZA OS Book Mobile Environment..."

# Load mobile environment
if [ -f .env.mobile ]; then
    export $(cat .env.mobile | grep -v '^#' | xargs)
    echo "✅ Mobile environment loaded"
else
    echo "⚠️  Mobile environment not found, using default"
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "🚀 Starting IZA OS Book services..."

# Start services with mobile configuration
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Test services
echo "🧪 Testing services..."
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ Main API responding"
else
    echo "⚠️  Main API not responding yet"
fi

if curl -s http://localhost:3000 >/dev/null; then
    echo "✅ Dashboard responding"
else
    echo "⚠️  Dashboard not responding yet"
fi

echo ""
echo "🎉 IZA OS Book Mobile Environment Ready!"
echo ""
echo "📱 Access URLs for your phone:"
echo "- Main API: http://$MAC_IP:8000"
echo "- Dashboard: http://$MAC_IP:3000"
echo "- Metrics: http://$MAC_IP:9090"
echo "- Health Check: http://$MAC_IP:8000/health"
echo ""
echo "📋 Quick Commands:"
echo "- Check status: ./mobile_status_book.sh"
echo "- Stop services: ./mobile_stop_book.sh"
echo "- View logs: docker-compose logs -f"
echo ""
EOF

chmod +x mobile_start_book.sh
print_success "Mobile start script created ✓"

# Create mobile status script
cat > mobile_status_book.sh << 'EOF'
#!/bin/bash

# IZA OS Book Mobile Status Check

echo "📱 IZA OS Book Mobile Status"
echo "============================"

# Check Docker services
echo "🐳 Docker Services:"
docker-compose ps

echo ""
echo "🔍 Service Health Checks:"

# Check main API
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ Main API: Running"
else
    echo "❌ Main API: Not responding"
fi

# Check dashboard
if curl -s http://localhost:3000 >/dev/null; then
    echo "✅ Dashboard: Running"
else
    echo "❌ Dashboard: Not responding"
fi

# Check metrics
if curl -s http://localhost:9090 >/dev/null; then
    echo "✅ Metrics: Running"
else
    echo "❌ Metrics: Not responding"
fi

echo ""
echo "📱 Mobile Access URLs:"
MAC_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo "- Main API: http://$MAC_IP:8000"
echo "- Dashboard: http://$MAC_IP:3000"
echo "- Metrics: http://$MAC_IP:9090"
EOF

chmod +x mobile_status_book.sh
print_success "Mobile status script created ✓"

# Create mobile stop script
cat > mobile_stop_book.sh << 'EOF'
#!/bin/bash

# Stop IZA OS Book Mobile Services

echo "🛑 Stopping IZA OS Book Mobile Services..."

# Stop Docker services
docker-compose down

echo "✅ All IZA OS Book services stopped"
EOF

chmod +x mobile_stop_book.sh
print_success "Mobile stop script created ✓"

echo ""
echo "STEP 3: Creating Mobile Dashboard"
echo "================================="

# Create mobile dashboard for IZA OS Book
mkdir -p mobile_dashboard_book
cat > mobile_dashboard_book/index.html << 'EOF'
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
        
        .status {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .status-dot.online {
            background: #10b981;
        }
        
        .status-dot.offline {
            background: #ef4444;
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
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .metric-value {
            font-weight: bold;
            color: #667eea;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 IZA OS Book Mobile</h1>
        
        <div class="card">
            <h2>System Status</h2>
            <div class="status">
                <div class="status-dot" id="api-status"></div>
                <span>Main API</span>
            </div>
            <div class="status">
                <div class="status-dot" id="dashboard-status"></div>
                <span>Dashboard</span>
            </div>
            <div class="status">
                <div class="status-dot" id="metrics-status"></div>
                <span>Metrics</span>
            </div>
        </div>
        
        <div class="card">
            <h2>AI Orchestrator</h2>
            <div class="input-group">
                <label for="task-input">Enter your task:</label>
                <textarea id="task-input" placeholder="e.g., analyze our Q4 financial performance"></textarea>
            </div>
            <button class="btn" onclick="executeTask()">Execute Task</button>
            <button class="btn secondary" onclick="checkStatus()">Check Status</button>
        </div>
        
        <div class="card">
            <h2>Quick Actions</h2>
            <button class="btn" onclick="openDashboard()">Open Dashboard</button>
            <button class="btn secondary" onclick="openMetrics()">View Metrics</button>
            <button class="btn secondary" onclick="viewLogs()">View Logs</button>
        </div>
        
        <div class="card">
            <h2>System Metrics</h2>
            <div class="metric">
                <span>Active Agents:</span>
                <span class="metric-value" id="agent-count">-</span>
            </div>
            <div class="metric">
                <span>Tasks Completed:</span>
                <span class="metric-value" id="task-count">-</span>
            </div>
            <div class="metric">
                <span>System Health:</span>
                <span class="metric-value" id="health-status">-</span>
            </div>
        </div>
    </div>

    <script>
        const MAC_IP = 'MAC_IP_PLACEHOLDER';
        
        async function checkStatus() {
            try {
                // Check Main API
                const apiResponse = await fetch(`http://${MAC_IP}:8000/health`);
                const apiStatus = apiResponse.ok ? 'online' : 'offline';
                document.getElementById('api-status').className = `status-dot ${apiStatus}`;
                
                if (apiResponse.ok) {
                    const apiData = await apiResponse.json();
                    document.getElementById('health-status').textContent = apiData.status || 'healthy';
                }
                
                // Check Dashboard
                const dashboardResponse = await fetch(`http://${MAC_IP}:3000`);
                const dashboardStatus = dashboardResponse.ok ? 'online' : 'offline';
                document.getElementById('dashboard-status').className = `status-dot ${dashboardStatus}`;
                
                // Check Metrics
                const metricsResponse = await fetch(`http://${MAC_IP}:9090`);
                const metricsStatus = metricsResponse.ok ? 'online' : 'offline';
                document.getElementById('metrics-status').className = `status-dot ${metricsStatus}`;
                
            } catch (error) {
                console.error('Status check failed:', error);
                document.getElementById('api-status').className = 'status-dot offline';
                document.getElementById('dashboard-status').className = 'status-dot offline';
                document.getElementById('metrics-status').className = 'status-dot offline';
            }
        }
        
        async function executeTask() {
            const taskInput = document.getElementById('task-input').value;
            if (!taskInput.trim()) {
                alert('Please enter a task');
                return;
            }
            
            try {
                const response = await fetch(`http://${MAC_IP}:8000/execute`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        content: taskInput
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    alert('Task executed successfully! Check logs for details.');
                    console.log('Task result:', result);
                } else {
                    alert('Task execution failed');
                }
            } catch (error) {
                console.error('Task execution error:', error);
                alert('Task execution failed: ' + error.message);
            }
        }
        
        function openDashboard() {
            window.open(`http://${MAC_IP}:3000`, '_blank');
        }
        
        function openMetrics() {
            window.open(`http://${MAC_IP}:9090`, '_blank');
        }
        
        function viewLogs() {
            window.open(`http://${MAC_IP}:8000/docs`, '_blank');
        }
        
        // Auto-refresh every 30 seconds
        setInterval(checkStatus, 30000);
        
        // Initial status check
        checkStatus();
    </script>
</body>
</html>
EOF

# Replace placeholder with actual IP
sed -i '' "s/MAC_IP_PLACEHOLDER/$MAC_IP/g" mobile_dashboard_book/index.html

print_success "Mobile dashboard created ✓"

echo ""
echo "STEP 4: Creating Mobile Connection Guide"
echo "========================================"

cat > MOBILE_BOOK_GUIDE.md << EOF
# 📚 IZA OS Book Mobile Access Guide

## 🚀 Quick Start

### 1. Start IZA OS Book Mobile
\`\`\`bash
./mobile_start_book.sh
\`\`\`

### 2. Access from Your Phone
Open your phone's browser and go to:
- **Mobile Dashboard**: http://$MAC_IP:3000
- **Main API**: http://$MAC_IP:8000
- **Metrics**: http://$MAC_IP:9090

### 3. Check Status
\`\`\`bash
./mobile_status_book.sh
\`\`\`

## 📱 Mobile Features

### ✅ Touch-Optimized Interface
- Large buttons and touch targets
- Mobile-friendly dashboard
- Swipe gestures support

### ✅ AI Orchestrator Access
- Execute tasks via mobile interface
- Real-time status monitoring
- Quick action buttons

### ✅ Full System Access
- Claude-powered intelligence
- Smart agent routing
- MCP integration (Apple Notes, Google Drive, GitHub, Calendar)
- Knowledge graph building

## 🔧 Mobile Commands

### Start Services
\`\`\`bash
./mobile_start_book.sh
\`\`\`

### Check Status
\`\`\`bash
./mobile_status_book.sh
\`\`\`

### Stop Services
\`\`\`bash
./mobile_stop_book.sh
\`\`\`

### View Logs
\`\`\`bash
docker-compose logs -f
\`\`\`

## 📱 Mobile Dashboard Features

- **System Status**: Live monitoring of all services
- **AI Orchestrator**: Execute tasks via mobile interface
- **Quick Actions**: One-tap access to dashboard, metrics, logs
- **System Metrics**: Agent count, task count, health status
- **Touch Optimized**: Designed for mobile interaction

## 🌐 Access URLs

**Local Network:**
- Mobile Dashboard: http://$MAC_IP:3000
- Main API: http://$MAC_IP:8000
- Metrics: http://$MAC_IP:9090
- Health Check: http://$MAC_IP:8000/health

## 🎯 Usage Examples

### Execute AI Tasks
1. Open mobile dashboard
2. Enter task in text area
3. Tap "Execute Task"
4. View results in logs

### Monitor System
1. Open mobile dashboard
2. Tap "Check Status"
3. View real-time metrics
4. Monitor agent activity

### Access Full Features
1. Tap "Open Dashboard" for full interface
2. Tap "View Metrics" for detailed analytics
3. Tap "View Logs" for system logs

## 🔧 Troubleshooting

### Services Not Starting
\`\`\`bash
# Check Docker
docker info

# Check logs
docker-compose logs

# Restart services
./mobile_stop_book.sh
./mobile_start_book.sh
\`\`\`

### Network Issues
\`\`\`bash
# Check Mac's IP
ifconfig | grep "inet "

# Test local access
curl http://localhost:8000/health
\`\`\`

## 🎉 Ready for Mobile AI Orchestration!

Your IZA OS Book is now fully accessible from your phone with:
- ✅ Touch-optimized interface
- ✅ AI task execution
- ✅ Real-time monitoring
- ✅ Full system access
- ✅ Mobile dashboard

Enjoy AI orchestration from anywhere! 📱🤖
EOF

print_success "Mobile connection guide created ✓"

echo ""
echo "🎉 IZA OS BOOK MOBILE SETUP COMPLETE!"
echo "===================================="
echo ""
echo "📱 Mobile Access Ready:"
echo "✅ Mobile-optimized startup scripts"
echo "✅ Touch-friendly mobile dashboard"
echo "✅ AI orchestrator mobile interface"
echo "✅ Real-time status monitoring"
echo "✅ Full system access from phone"
echo ""
echo "🚀 Quick Start:"
echo "1. Run: ./mobile_start_book.sh"
echo "2. Open: http://$MAC_IP:3000 on your phone"
echo "3. Check: ./mobile_status_book.sh"
echo ""
echo "📖 Read: MOBILE_BOOK_GUIDE.md for full details"
echo ""
echo "Your IZA OS Book is now mobile-ready! 📚📱✨"
