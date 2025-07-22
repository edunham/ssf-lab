#!/bin/bash
# Start the SSF Event Receiver

echo "🚀 Starting SSF Event Receiver..."

cd "$(dirname "$0")"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the receiver
exec npm start