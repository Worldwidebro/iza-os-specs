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
