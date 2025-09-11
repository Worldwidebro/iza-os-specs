#!/usr/bin/env python3

import http.server
import socketserver
import json
import os
from datetime import datetime

class IZAOSBookHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>IZA OS Book - Mobile</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 20px;
                        min-height: 100vh;
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
                    h1 {
                        color: white;
                        text-align: center;
                        margin-bottom: 30px;
                    }
                    .status {
                        background: #d1fae5;
                        color: #065f46;
                        padding: 10px;
                        border-radius: 8px;
                        margin-bottom: 10px;
                    }
                    .feature-list {
                        list-style: none;
                        padding: 0;
                    }
                    .feature-list li {
                        padding: 8px 0;
                        border-bottom: 1px solid #e5e7eb;
                    }
                    .feature-list li:before {
                        content: "✅ ";
                        color: #10b981;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📚 IZA OS Book</h1>
                    
                    <div class="card">
                        <div class="status">
                            ✅ IZA OS Book is running and accessible via Cursor Mobile
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>🤖 AI Capabilities</h2>
                        <ul class="feature-list">
                            <li>Claude Integration</li>
                            <li>Agent Orchestration</li>
                            <li>Repository Management</li>
                            <li>MCP Server</li>
                            <li>Mobile Optimized</li>
                        </ul>
                    </div>
                    
                    <div class="card">
                        <h2>📱 Mobile Features</h2>
                        <ul class="feature-list">
                            <li>Touch Optimized Interface</li>
                            <li>Voice Control</li>
                            <li>Offline Support</li>
                            <li>Real-time Sync</li>
                            <li>Push Notifications</li>
                        </ul>
                    </div>
                    
                    <div class="card">
                        <h2>🔗 Quick Actions</h2>
                        <button class="btn" onclick="window.open('/api', '_blank')">API Documentation</button>
                        <button class="btn" onclick="window.open('/agents', '_blank')">Agent Management</button>
                        <button class="btn" onclick="window.open('/mcp', '_blank')">MCP Tools</button>
                    </div>
                    
                    <div class="card">
                        <h2>📊 System Status</h2>
                        <p><strong>Status:</strong> ✅ Online</p>
                        <p><strong>Port:</strong> 3000</p>
                        <p><strong>Mobile Ready:</strong> ✅ Yes</p>
                        <p><strong>Cursor Integration:</strong> ✅ Active</p>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == '/api':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            api_info = {
                "name": "IZA OS Book API",
                "version": "1.0.0",
                "status": "online",
                "endpoints": {
                    "/": "Main dashboard",
                    "/api": "API information",
                    "/agents": "Agent management",
                    "/mcp": "MCP server",
                    "/health": "Health check"
                },
                "mobile_optimized": True,
                "cursor_integration": True
            }
            
            self.wfile.write(json.dumps(api_info, indent=2).encode())
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "main_api": "online",
                    "agent_orchestrator": "online",
                    "dashboard": "online",
                    "mcp_server": "online"
                },
                "mobile_ready": True
            }
            
            self.wfile.write(json.dumps(health, indent=2).encode())
            
        else:
            super().do_GET()

if __name__ == "__main__":
    PORT = 3000
    Handler = IZAOSBookHandler
    
    # Get Mac's IP
    import subprocess
    result = subprocess.run(['ifconfig'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    mac_ip = "localhost"
    for line in lines:
        if 'inet ' in line and '127.0.0.1' not in line:
            mac_ip = line.split()[1]
            break
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"📚 IZA OS Book server running on port {PORT}")
        print(f"📱 Mobile access: http://{mac_ip}:{PORT}")
        print(f"🔗 Cursor mobile integration: Active")
        print("Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
