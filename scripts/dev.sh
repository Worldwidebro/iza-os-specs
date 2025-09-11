#!/bin/bash
# Start the system in development mode

echo "🛠️  Starting system in DEVELOPMENT mode..."

# This command will start the services and attach the logs to the terminal
# for real-time feedback. Press Ctrl+C to stop.
docker-compose up --build

echo "
✅ System has been shut down.
"