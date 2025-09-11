# 📚 IZA OS Book Mobile Access Guide

## 🚀 Quick Start

### 1. Start IZA OS Book Mobile
```bash
./mobile_start_book.sh
```

### 2. Access from Your Phone
Open your phone's browser and go to:
- **Mobile Dashboard**: http://192.168.1.187:3000
- **Main API**: http://192.168.1.187:8000
- **Metrics**: http://192.168.1.187:9090

### 3. Check Status
```bash
./mobile_status_book.sh
```

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
```bash
./mobile_start_book.sh
```

### Check Status
```bash
./mobile_status_book.sh
```

### Stop Services
```bash
./mobile_stop_book.sh
```

### View Logs
```bash
docker-compose logs -f
```

## 📱 Mobile Dashboard Features

- **System Status**: Live monitoring of all services
- **AI Orchestrator**: Execute tasks via mobile interface
- **Quick Actions**: One-tap access to dashboard, metrics, logs
- **System Metrics**: Agent count, task count, health status
- **Touch Optimized**: Designed for mobile interaction

## 🌐 Access URLs

**Local Network:**
- Mobile Dashboard: http://192.168.1.187:3000
- Main API: http://192.168.1.187:8000
- Metrics: http://192.168.1.187:9090
- Health Check: http://192.168.1.187:8000/health

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
```bash
# Check Docker
docker info

# Check logs
docker-compose logs

# Restart services
./mobile_stop_book.sh
./mobile_start_book.sh
```

### Network Issues
```bash
# Check Mac's IP
ifconfig | grep "inet "

# Test local access
curl http://localhost:8000/health
```

## 🎉 Ready for Mobile AI Orchestration!

Your IZA OS Book is now fully accessible from your phone with:
- ✅ Touch-optimized interface
- ✅ AI task execution
- ✅ Real-time monitoring
- ✅ Full system access
- ✅ Mobile dashboard

Enjoy AI orchestration from anywhere! 📱🤖
