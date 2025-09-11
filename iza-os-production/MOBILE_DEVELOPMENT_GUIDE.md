# 📱 IZA OS Mobile Development Guide

## Quick Start for Cursor Mobile

### 1. Start Mobile Environment
```bash
./mobile_start.sh
```

### 2. Check Status
```bash
./mobile_status.sh
```

### 3. Access Mobile Dashboard
Open: `mobile_dashboard/index.html` in your browser

### 4. Run Orchestrator
```bash
./mobile_orchestrator.sh
```

## Mobile-Optimized Features

### ✅ Touch-Friendly Interface
- Large buttons and touch targets
- Swipe gestures support
- Mobile-optimized layouts

### ✅ Reduced Resource Usage
- Lower concurrent task limits
- Shorter timeouts
- Optimized logging levels

### ✅ Quick Actions
- One-tap service management
- Instant status checks
- Mobile dashboard integration

### ✅ Offline Capability
- Core functions work offline
- Local data persistence
- Sync when online

## Mobile Workflow

### Morning Routine (2 minutes)
1. Open Cursor mobile
2. Run `./mobile_start.sh`
3. Check `./mobile_status.sh`
4. Open mobile dashboard

### Throughout Day
- Use mobile dashboard for quick checks
- Run `./mobile_orchestrator.sh` for tasks
- Monitor via mobile dashboard

### Evening
- Run `./mobile_stop.sh` to stop services
- Check logs if needed

## Mobile Dashboard Features

- **Real-time Status**: Live service health monitoring
- **Quick Actions**: One-tap service management
- **System Metrics**: Agent count, repository count, task count
- **Touch Optimized**: Designed for mobile interaction

## Troubleshooting

### Services Not Starting
```bash
# Check logs
tail -f logs/mcp_mobile.log
tail -f logs/orchestrator_mobile.log

# Restart services
./mobile_stop.sh
./mobile_start.sh
```

### Port Conflicts
```bash
# Kill conflicting processes
lsof -ti:8000,8001 | xargs kill -9
./mobile_start.sh
```

### GitHub Issues
```bash
# Check GitHub authentication
gh auth status

# Re-authenticate if needed
gh auth login --web
```

## Mobile Development Tips

1. **Use Mobile Dashboard**: Always keep it open for quick status checks
2. **Quick Commands**: Memorize the mobile shortcuts
3. **Log Monitoring**: Check logs regularly for issues
4. **Resource Management**: Mobile has limited resources, use efficiently
5. **Offline Mode**: Core functions work offline, sync when possible

## Cursor Mobile Integration

The system is optimized for Cursor mobile with:
- Touch-friendly interfaces
- Mobile-optimized workflows
- Quick action shortcuts
- Resource-efficient operation
- Offline capability

Enjoy mobile development with IZA OS! 🚀
