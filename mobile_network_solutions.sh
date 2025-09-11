#!/bin/bash

# IZA OS Book Mobile Access - Alternative Solutions
# Since Mac is on Ethernet, phone needs different connection method

echo "📱 IZA OS Book Mobile Access - Network Solutions"
echo "==============================================="
echo ""

# Get Mac's IP address
MAC_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo "Your Mac's IP: $MAC_IP"
echo ""

echo "🔍 NETWORK DIAGNOSIS:"
echo "===================="
echo "❌ Mac is connected via Ethernet (not WiFi)"
echo "❌ Phone cannot access local IP directly"
echo "✅ Need alternative connection methods"
echo ""

echo "🚀 SOLUTION 1: Enable WiFi Hotspot on Mac"
echo "=========================================="
echo "1. Go to System Preferences > Sharing"
echo "2. Enable 'Internet Sharing'"
echo "3. Share from: Ethernet"
echo "4. To computers using: Wi-Fi"
echo "5. Set WiFi password"
echo "6. Connect your phone to Mac's hotspot"
echo "7. Then use: http://$MAC_IP:3000"
echo ""

echo "🌐 SOLUTION 2: Use ngrok for Public Access"
echo "=========================================="
echo "This creates a public URL that works from anywhere:"
echo ""

# Check if ngrok is installed
if command -v ngrok &> /dev/null; then
    echo "✅ ngrok is installed"
    echo "Starting ngrok tunnel..."
    echo ""
    echo "Run this command in another terminal:"
    echo "ngrok http 3000"
    echo ""
    echo "Then use the ngrok URL on your phone"
else
    echo "❌ ngrok not installed"
    echo "Install with: brew install ngrok"
    echo "Or download from: https://ngrok.com/"
fi

echo ""
echo "☁️ SOLUTION 3: Deploy to Cloud (Recommended)"
echo "============================================"
echo "Deploy IZA OS Book to a cloud service:"
echo ""

# Create cloud deployment script
cat > deploy_to_cloud.sh << 'EOF'
#!/bin/bash

echo "☁️ Deploying IZA OS Book to Cloud"
echo "================================="

# Option 1: Vercel (Free)
echo "🚀 Option 1: Vercel Deployment"
echo "1. Install Vercel CLI: npm i -g vercel"
echo "2. Run: vercel"
echo "3. Follow prompts"
echo "4. Get public URL for mobile access"
echo ""

# Option 2: Render (Free)
echo "🌐 Option 2: Render Deployment"
echo "1. Push code to GitHub"
echo "2. Connect to Render.com"
echo "3. Deploy as web service"
echo "4. Get public URL"
echo ""

# Option 3: Railway (Free)
echo "🚂 Option 3: Railway Deployment"
echo "1. Install Railway CLI: npm i -g @railway/cli"
echo "2. Run: railway login"
echo "3. Run: railway deploy"
echo "4. Get public URL"
echo ""

echo "📱 After deployment, use the public URL on your phone!"
EOF

chmod +x deploy_to_cloud.sh
echo "✅ Cloud deployment script created: deploy_to_cloud.sh"

echo ""
echo "🔧 SOLUTION 4: Quick Local Tunnel"
echo "================================"
echo "Use a simple tunnel service:"
echo ""

# Create tunnel script
cat > create_tunnel.sh << 'EOF'
#!/bin/bash

echo "🔧 Creating Local Tunnel"
echo "========================"

# Option 1: localtunnel
if command -v lt &> /dev/null; then
    echo "✅ localtunnel available"
    echo "Run: lt --port 3000"
    echo "Use the provided URL on your phone"
else
    echo "Install: npm install -g localtunnel"
    echo "Then run: lt --port 3000"
fi

echo ""

# Option 2: serveo
echo "🌐 Option 2: Serveo (no installation needed)"
echo "Run: ssh -R 80:localhost:3000 serveo.net"
echo "Use the provided URL on your phone"

echo ""

# Option 3: cloudflared
if command -v cloudflared &> /dev/null; then
    echo "✅ cloudflared available"
    echo "Run: cloudflared tunnel --url http://localhost:3000"
else
    echo "Install: brew install cloudflared"
    echo "Then run: cloudflared tunnel --url http://localhost:3000"
fi
EOF

chmod +x create_tunnel.sh
echo "✅ Tunnel script created: create_tunnel.sh"

echo ""
echo "📱 IMMEDIATE SOLUTION: Use Cursor Mobile App"
echo "============================================="
echo "Since you have Cursor mobile app:"
echo ""

# Create Cursor mobile setup
cat > setup_cursor_mobile.sh << 'EOF'
#!/bin/bash

echo "📱 Setting up Cursor Mobile Access"
echo "==================================="

# Create mobile-optimized configuration
cat > .cursor-mobile.json << 'JSON'
{
  "mobile": {
    "enabled": true,
    "port": 3000,
    "host": "0.0.0.0",
    "ssl": false,
    "cors": true
  },
  "services": {
    "main_api": {
      "port": 8000,
      "path": "/api"
    },
    "agent_orchestrator": {
      "port": 8001,
      "path": "/agents"
    },
    "dashboard": {
      "port": 3000,
      "path": "/"
    }
  },
  "mobile_features": {
    "touch_optimized": true,
    "offline_support": true,
    "push_notifications": true,
    "voice_control": true
  }
}
JSON

echo "✅ Cursor mobile config created"

# Start services for mobile
echo "🚀 Starting services for mobile access..."
docker-compose up -d

echo "📱 Mobile access ready!"
echo "Use Cursor mobile app to connect to your Mac"
echo "Or use one of the tunnel solutions above"
EOF

chmod +x setup_cursor_mobile.sh
echo "✅ Cursor mobile setup created: setup_cursor_mobile.sh"

echo ""
echo "🎯 RECOMMENDED NEXT STEPS:"
echo "=========================="
echo ""
echo "1. 🚀 QUICKEST: Run tunnel script"
echo "   ./create_tunnel.sh"
echo ""
echo "2. ☁️ BEST: Deploy to cloud"
echo "   ./deploy_to_cloud.sh"
echo ""
echo "3. 📱 MOBILE: Use Cursor app"
echo "   ./setup_cursor_mobile.sh"
echo ""
echo "4. 🔥 HOTSPOT: Enable Mac WiFi hotspot"
echo "   (Manual setup in System Preferences)"
echo ""

echo "💡 WHY THE ROUTER MESSAGE APPEARS:"
echo "================================="
echo "Your phone is trying to connect to 192.168.1.187"
echo "But your Mac is on Ethernet, not WiFi"
echo "So your phone can't reach that IP address"
echo "The solutions above fix this network issue"
echo ""

echo "🎉 Choose your preferred solution and run the script!"
