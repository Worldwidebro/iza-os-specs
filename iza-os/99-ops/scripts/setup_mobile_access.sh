#!/bin/bash

# IZA OS Mobile Access Setup
echo "📱 IZA OS Mobile Access Setup"
echo "============================"

# Get Mac's IP address
MAC_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo "Your Mac's IP: $MAC_IP"

# Create mobile-optimized configuration
cat > .env.mobile << EOF
# IZA OS Mobile Configuration
IZA_OS_MOBILE_ENABLED=true
IZA_OS_MOBILE_PORT=3000
IZA_OS_MOBILE_HOST=0.0.0.0
IZA_OS_MOBILE_IP=$MAC_IP
IZA_OS_MOBILE_SSL=false
IZA_OS_MOBILE_CORS=true

# Mobile Features
IZA_OS_TOUCH_OPTIMIZED=true
IZA_OS_VOICE_CONTROL=true
IZA_OS_OFFLINE_SUPPORT=true
IZA_OS_PUSH_NOTIFICATIONS=true
IZA_OS_REAL_TIME_SYNC=true
