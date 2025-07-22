#!/usr/bin/env python3
"""
Simple test client for the SSF Security MCP Server
Tests file access and event generation without requiring AI assistant integration
"""

import asyncio
import json
import sys
from pathlib import Path
from server import SecurityMCPServer

async def test_file_access(filepath: str):
    """Test file access and event generation"""
    print(f"\n🧪 Testing file access: {filepath}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Create server instance
    server = SecurityMCPServer()
    
    try:
        # Test file reading
        result = await server.handle_file_read(filepath)
        
        # Display results
        for content in result:
            print(content.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_directory_listing(dirpath: str = "/workspace/test-files"):
    """Test directory listing"""
    print(f"\n📁 Testing directory listing: {dirpath}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    server = SecurityMCPServer()
    
    try:
        result = await server.handle_list_files(dirpath)
        for content in result:
            print(content.text)
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Run test scenarios"""
    print("🚀 SSF Security MCP Server - Test Client")
    print("========================================")
    
    # Test directory listing first
    await test_directory_listing()
    
    # Test files from command line args or defaults
    test_files = sys.argv[1:] if len(sys.argv) > 1 else [
        "/workspace/test-files/public-data.txt",
        "/workspace/test-files/user-credentials.secret", 
        "/workspace/test-files/api-keys.credentials"
    ]
    
    for filepath in test_files:
        await test_file_access(filepath)
    
    print("\n✅ Test completed!")
    print("\n💡 Check the SSF Receiver dashboard at http://localhost:8082")
    print("   to see any security events that were generated.")

if __name__ == "__main__":
    asyncio.run(main())