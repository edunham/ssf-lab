#!/bin/bash
set -e

echo "Setting up SSF/CAEP Lab Environment..."

# Get the correct workspace directory
WORKSPACE_DIR="$PWD"
echo "Working in: $WORKSPACE_DIR"

# Install Python dependencies for MCP server
echo "📦 Installing MCP server dependencies..."
cd "$WORKSPACE_DIR/mcp-server"
pip install --user -r requirements.txt

# Install Node.js dependencies for SSF components
echo "📦 Installing SSF transmitter dependencies..."
cd "$WORKSPACE_DIR/ssf-transmitter"
npm install

echo "📦 Installing SSF receiver dependencies..."
cd "$WORKSPACE_DIR/ssf-receiver"
npm install

# Create test files
echo "📄 Creating test files..."
cd "$WORKSPACE_DIR/test-files"
echo "This is public information that anyone can access." > public-data.txt
echo "username=admin\npassword=secret123\napi_key=sk-1234567890abcdef" > user-credentials.secret
echo "DATABASE_URL=postgresql://user:pass@db:5432/prod\nAWS_SECRET_KEY=AKIAIOSFODNN7EXAMPLE" > api-keys.credentials

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x "$WORKSPACE_DIR/mcp-server/start-server.sh"
chmod +x "$WORKSPACE_DIR/ssf-transmitter/start-transmitter.sh" 2>/dev/null || echo "  Note: start-transmitter.sh not found"
chmod +x "$WORKSPACE_DIR/ssf-receiver/start-receiver.sh"

echo "✅ SSF/CAEP Lab environment setup complete!"
echo "📋 Available commands:"
echo "  - Start MCP Server: cd mcp-server && ./start-server.sh"
echo "  - Start SSF Transmitter: cd ssf-transmitter && ./start-transmitter.sh" 
echo "  - Start SSF Receiver: cd ssf-receiver && ./start-receiver.sh"