#!/usr/bin/env python3
"""
SSF/CAEP Lab MCP Server
Monitors file access and generates CAEP security events for educational purposes
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import aiohttp

# AIDEV-NOTE: SSF transmitter integrated into MCP server per best practices
class SecurityMCPServer:
    def __init__(self):
        self.server = Server("ssf-security-mcp")
        self.ssf_receiver_url = "http://localhost:8082/events"
        self.monitored_patterns = [".secret", ".credentials", "/secure/", "api-key", "password"]
        self.event_count = 0
        
        # Register tools
        self.setup_tools()
    
    def setup_tools(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools for the MCP client"""
            return [
                types.Tool(
                    name="read_file_secure",
                    description="Read file contents with security monitoring",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to the file to read"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                types.Tool(
                    name="list_files_secure", 
                    description="List files in directory with security monitoring",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path to list",
                                "default": "/workspace/test-files"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """Handle tool calls with security monitoring"""
            
            if name == "read_file_secure":
                return await self.handle_file_read(arguments["path"])
            elif name == "list_files_secure":
                path = arguments.get("path", "/workspace/test-files")
                return await self.handle_list_files(path)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def handle_file_read(self, filepath: str) -> List[types.TextContent]:
        """Handle secure file reading with event generation"""
        try:
            # Normalize path
            abs_path = Path(filepath).resolve()
            
            # Check if file is sensitive
            is_sensitive = self.is_sensitive_file(str(abs_path))
            
            # Generate SSF event if sensitive
            if is_sensitive:
                await self.generate_caep_event(str(abs_path), "file_access")
            
            # Read file content (sandbox to test-files directory)
            if not str(abs_path).startswith("/workspace/test-files"):
                return [types.TextContent(
                    type="text",
                    text=f"⚠️  Access denied: File outside allowed directory\nPath: {abs_path}"
                )]
            
            if abs_path.exists() and abs_path.is_file():
                content = abs_path.read_text()
                event_notice = "🔒 SECURITY EVENT GENERATED" if is_sensitive else ""
                
                return [types.TextContent(
                    type="text", 
                    text=f"📄 File: {abs_path}\n{event_notice}\n\nContent:\n{content}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ File not found: {abs_path}"
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Error reading file: {e}"
            )]
    
    async def handle_list_files(self, dirpath: str) -> List[types.TextContent]:
        """Handle secure directory listing"""
        try:
            abs_path = Path(dirpath).resolve()
            
            if not abs_path.exists() or not abs_path.is_dir():
                return [types.TextContent(
                    type="text",
                    text=f"❌ Directory not found: {abs_path}"
                )]
            
            files = []
            for item in abs_path.iterdir():
                is_sensitive = self.is_sensitive_file(str(item))
                icon = "🔒" if is_sensitive else ("📁" if item.is_dir() else "📄")
                files.append(f"{icon} {item.name}")
            
            return [types.TextContent(
                type="text",
                text=f"📁 Directory: {abs_path}\n\n" + "\n".join(files)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text", 
                text=f"❌ Error listing directory: {e}"
            )]
    
    def is_sensitive_file(self, filepath: str) -> bool:
        """Check if file matches sensitive patterns"""
        filepath_lower = filepath.lower()
        return any(pattern in filepath_lower for pattern in self.monitored_patterns)
    
    async def generate_caep_event(self, filepath: str, access_type: str):
        """Generate and send CAEP security event (integrated transmitter)"""
        self.event_count += 1
        
        # Create CAEP-compliant event
        event = {
            "iss": "https://ssf-lab-mcp-server.example.com",
            "jti": f"event-{int(time.time())}-{self.event_count}",
            "iat": int(time.time()),
            "aud": "https://ssf-lab-receiver.example.com",
            "sub_id": {
                "format": "email",
                "email": "lab-student@example.com"
            },
            "events": {
                "https://schemas.openid.net/secevent/caep/event-type/session-risk-change": {
                    "initiating_entity": "system",
                    "risk_level": "high",
                    "risk_type": "sensitive_file_access",
                    "reason_admin": {
                        "en": f"Sensitive file accessed: {os.path.basename(filepath)}"
                    },
                    "event_timestamp": int(time.time() * 1000),
                    "custom_data": {
                        "file_path": filepath,
                        "access_type": access_type,
                        "lab_session": True
                    }
                }
            }
        }
        
        # Log event locally (console output)
        print(f"🚨 SSF EVENT GENERATED: {datetime.now().isoformat()}")
        print(f"   File: {filepath}")
        print(f"   Risk Level: HIGH")
        print(f"   Event ID: {event['jti']}")
        
        # Send to receiver (if running)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.ssf_receiver_url,
                    json=event,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as response:
                    if response.status == 200:
                        print(f"✅ Event delivered to receiver")
                    else:
                        print(f"⚠️  Receiver returned status: {response.status}")
        except Exception as e:
            print(f"⚠️  Receiver not available: {e}")

async def main():
    """Run the MCP server"""
    server_instance = SecurityMCPServer()
    
    # Run the server with stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ssf-security-mcp",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())