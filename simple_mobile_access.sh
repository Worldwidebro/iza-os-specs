#!/bin/bash

# Simple Mobile Access Solution
# Creates a public URL that works from your phone

echo "📱 Creating Mobile Access for IZA OS Book"
echo "========================================"

# Start the services first
echo "🚀 Starting IZA OS Book services..."
python3 -m http.server 3000 --directory . &
SERVER_PID=$!

echo "✅ Server started on port 3000"
echo ""

# Try different tunnel methods
echo "🌐 Attempting to create public tunnel..."

# Method 1: Try serveo
echo "Trying Serveo tunnel..."
timeout 10s ssh -o StrictHostKeyChecking=no -R 80:localhost:3000 serveo.net 2>/dev/null &
SERVEO_PID=$!

sleep 5

# Method 2: Try localtunnel if available
if command -v lt &> /dev/null; then
    echo "Trying localtunnel..."
    lt --port 3000 --subdomain iza-os-book &
    LT_PID=$!
    sleep 3
fi

# Method 3: Try cloudflared if available
if command -v cloudflared &> /dev/null; then
    echo "Trying cloudflared..."
    cloudflared tunnel --url http://localhost:3000 &
    CF_PID=$!
    sleep 3
fi

echo ""
echo "📱 MOBILE ACCESS OPTIONS:"
echo "========================"
echo ""
echo "1. 🌐 Try these URLs on your phone:"
echo "   - https://iza-os-book.loca.lt (if localtunnel worked)"
echo "   - Check terminal for serveo URL"
echo "   - Check terminal for cloudflared URL"
echo ""
echo "2. 📱 Use Cursor Mobile App:"
echo "   - Open Cursor mobile app"
echo "   - Connect to your Mac"
echo "   - Access IZA OS Book through Cursor"
echo ""
echo "3. 🔥 Enable Mac WiFi Hotspot:"
echo "   - System Preferences > Sharing"
echo "   - Enable 'Internet Sharing'"
echo "   - Share from Ethernet to WiFi"
echo "   - Connect phone to Mac's hotspot"
echo "   - Then use: http://192.168.1.187:3000"
echo ""
echo "4. ☁️ Deploy to Cloud (Best Option):"
echo "   - Run: ./deploy_to_cloud.sh"
echo "   - Get permanent public URL"
echo "   - Works from anywhere"
echo ""

# Keep the server running
echo "🔄 Server is running in background..."
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user input
read -p "Press Enter to stop services and exit..."

# Cleanup
echo "🧹 Stopping services..."
kill $SERVER_PID 2>/dev/null
kill $SERVEO_PID 2>/dev/null
kill $LT_PID 2>/dev/null
kill $CF_PID 2>/dev/null

echo "✅ All services stopped"
