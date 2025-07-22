#!/bin/bash
# Start the SSF Security MCP Server

echo "🚀 Starting SSF Security MCP Server..."

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the server
exec python server.py