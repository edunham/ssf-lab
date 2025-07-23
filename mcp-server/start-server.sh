#!/bin/bash
# Start the SSF Security MCP Server

echo "🚀 Starting SSF Security MCP Server..."

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Check if mcp module is available
if ! python -c "import mcp" 2>/dev/null; then
    echo "❌ MCP module not found. Please install dependencies:"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Start the server
echo "✅ Starting MCP server..."
exec python server.py