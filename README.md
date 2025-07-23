# SSF/CAEP Security Lab

A hands-on lab demonstrating the **Shared Signals Framework (SSF)** and **Continuous Access Evaluation Profile (CAEP)** using MCP servers as security event sources.

## 🎯 Lab Objectives

Students will learn to:
- Understand SSF/CAEP event-driven security architecture
- Implement real-time security event generation and processing  
- Use MCP servers as security monitoring components
- Build SSF-compliant event transmitters and receivers
- Test with real CAEP testing services like caep.dev

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  MCP Server     │────▶│  SSF Receiver   │────▶│  External Test  │
│  (File Monitor) │     │  (Mock Okta)    │     │  (caep.dev)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                         │                         │
        └── Monitors file access   └── Processes events     └── Validates events
            Generates CAEP events      Takes security actions     External testing
```

## 🚀 Complete Setup Guide

### Prerequisites
- GitHub Codespaces (recommended) or local Docker environment
- VS Code with MCP support (if testing AI assistant integration)

### Step 1: Environment Setup

**In Codespaces:**
1. Fork this repository
2. Open in GitHub Codespaces  
3. Wait for devcontainer to build (installs Python, Node.js, dependencies)
4. Open terminal in VS Code

**Local Setup:**
```bash
git clone [your-repo-url]
cd ssf-lab
# Ensure Python 3.11+ and Node.js 18+ installed
pip install -r mcp-server/requirements.txt
cd ssf-receiver && npm install && cd ..
```

### Step 2: Start Services (Required Order)

**Terminal 1 - Start SSF Receiver:**
```bash
cd ssf-receiver
./start-receiver.sh
```
✅ **Verify**: Dashboard loads at http://localhost:8082

**Terminal 2 - Start MCP Server:**
```bash
cd mcp-server  
./start-server.sh
```
✅ **Verify**: Server shows "SSF Security MCP Server Started"

### Step 3: Test Local Event Flow

**Option A - Manual Testing (No AI Assistant Required):**
```bash
# Test file reading directly
python mcp-server/test_client.py test-files/public-data.txt
python mcp-server/test_client.py test-files/user-credentials.secret
```

**Option B - AI Assistant Testing:**
Ask GitHub Copilot or similar AI:
- "Read the contents of test-files/public-data.txt"
- "Read the contents of test-files/user-credentials.secret" ⚠️ 
- "List all files in the test-files directory"

✅ **Expected**: Sensitive files (*.secret, *.credentials) trigger CAEP security events

### Step 4: Verify Event Generation

**Check the SSF Receiver Dashboard:**
1. Open http://localhost:8082 in your browser
2. Look for security events in the dashboard
3. Verify event details (risk level, file path, timestamp)

**Expected Results:**
- `public-data.txt` → No security event
- `user-credentials.secret` → 🚨 HIGH risk event  
- `api-keys.credentials` → 🚨 HIGH risk event

### Step 5: External Testing Options

**Option A - Test with caep.dev (SGNL's CAEP Testing Service):**
```bash
# 1. Visit https://caep.dev and create a test stream
# 2. Get your receiver endpoint URL  
# 3. Configure MCP server to send externally:
export SSF_RECEIVER_URL="https://caep.dev/api/receiver/[your-stream-id]"

# 4. Restart MCP server with new endpoint
cd mcp-server && python server.py
```

**Option B - ngrok for External Access:**
```bash
# Install ngrok (enables external access to local receiver)
npm install -g ngrok

# Expose local receiver publicly
ngrok http 8082

# Use ngrok URL for external testing
# Copy the https://[random-id].ngrok.io URL from ngrok output
```

**Option C - Send Test Event via curl:**
```bash
# Send a manual CAEP event to test receiver
curl -X POST http://localhost:8082/events \
  -H "Content-Type: application/json" \
  -d '{
    "iss": "https://test-transmitter.example.com",
    "jti": "test-event-12345",
    "iat": '$(date +%s)',
    "aud": "https://ssf-lab-receiver.example.com", 
    "sub_id": {"format": "email", "email": "test@example.com"},
    "events": {
      "https://schemas.openid.net/secevent/caep/event-type/session-risk-change": {
        "risk_level": "high",
        "risk_type": "manual_test", 
        "reason_admin": {"en": "Manual test event via curl"}
      }
    }
  }'
```

## 📂 Test Files

| File | Type | Security Event |
|------|------|----------------|
| `public-data.txt` | Public | None |  
| `user-credentials.secret` | Sensitive | 🚨 HIGH risk |
| `api-keys.credentials` | Sensitive | 🚨 HIGH risk |

## 🧪 Advanced Testing Scenarios

### Scenario 1: MCP Integration Test
**Goal**: Verify AI assistant can use MCP tools

1. Ensure MCP server is running
2. Ask GitHub Copilot: *"Use the read_file_secure tool to read test-files/user-credentials.secret"*
3. ✅ **Success**: AI uses MCP tool, security event generated
4. ❌ **Failure**: AI cannot access MCP tools → Use manual testing

### Scenario 2: Event Flow Validation
**Goal**: End-to-end SSF/CAEP event processing

1. Start receiver with dashboard monitoring
2. Trigger sensitive file access (any method)
3. Verify event appears in receiver dashboard
4. Check event structure matches CAEP specification
5. Confirm simulated policy actions are triggered

### Scenario 3: External Service Integration  
**Goal**: Test with real CAEP services

1. Configure caep.dev or other CAEP receiver
2. Update MCP server endpoint configuration
3. Trigger events and verify external reception
4. Compare local vs external event processing

### Scenario 4: Custom Event Types
**Goal**: Extend beyond basic file access

1. Modify MCP server to detect other patterns
2. Add new risk types (e.g., `bulk_download`, `off_hours_access`)
3. Test event generation with custom metadata
4. Verify receiver processes extended events

## 🔍 Critical Integration Questions

**MCP + Codespaces Compatibility:**
1. ✅/❌ Does VS Code in Codespaces register our custom MCP server?
2. ✅/❌ Can GitHub Copilot discover and use our MCP tools?
3. ✅/❌ Do file access events trigger when AI assistants read files?
4. ✅/❌ Does the complete SSF event flow work end-to-end?

**Results will determine next steps:**
- ✅ **Full Success**: Add CodeTours, more event types, OAuth
- ⚠️ **Partial Success**: Adapt integration, provide fallbacks  
- ❌ **Integration Issues**: Pivot to file watchers or extensions

## ⚙️ Technical Details

### SSF Event Format
```json
{
  "iss": "https://ssf-lab-mcp-server.example.com",
  "jti": "event-1234567890-1", 
  "sub_id": {"format": "email", "email": "lab-student@example.com"},
  "events": {
    "https://schemas.openid.net/secevent/caep/event-type/session-risk-change": {
      "risk_level": "high",
      "risk_type": "sensitive_file_access",
      "reason_admin": {"en": "Sensitive file accessed: user-credentials.secret"}
    }
  }
}
```

### MCP Server Configuration
MCP servers are configured in VS Code settings:
```json
{
  "mcpServers": {
    "ssf-security": {
      "command": "python", 
      "args": ["/workspace/mcp-server/server.py"]
    }
  }
}
```

## 🔬 Expected Results

**If MCP Integration Works:**
- AI assistants can call `read_file_secure` and `list_files_secure`
- Sensitive file access triggers real-time CAEP events  
- Events appear in receiver dashboard and logs
- Policy actions are simulated (session termination, alerts)

**If MCP Integration Fails:**
- AI assistants cannot access our custom tools
- Need alternative approach (file watchers, VS Code extensions)
- May require different event generation strategy

## 🛠️ Troubleshooting

### MCP Server Issues
```bash
# Check if MCP server is running
ps aux | grep "python.*server.py"

# Test MCP server directly
cd mcp-server && python test_client.py

# Check Python dependencies
pip list | grep -E "(mcp|aiohttp|pydantic)"
```

### SSF Receiver Issues  
```bash
# Check if receiver is running
curl -I http://localhost:8082

# View receiver logs
cd ssf-receiver && npm run dev

# Test receiver directly
curl -X POST http://localhost:8082/events -H "Content-Type: application/json" -d '{"test": true}'
```

### Common Problems
- **"Module not found"**: Run `pip install -r mcp-server/requirements.txt`
- **"Port already in use"**: Change ports in configuration or kill existing processes
- **"Events not appearing"**: Check receiver URL in MCP server configuration

## 🏷️ Event Testing Commands

### Quick Event Tests
```bash
# Test all files at once
cd mcp-server && python test_client.py

# Test specific file
cd mcp-server && python test_client.py /workspace/test-files/user-credentials.secret

# Send test event via API
curl -X POST http://localhost:8082/events \
  -H "Content-Type: application/json" \
  -d @../test-events/sample-caep-event.json
```

### Monitor Events in Real-Time
```bash
# Terminal 1: Watch receiver logs
cd ssf-receiver && npm run dev

# Terminal 2: Watch MCP server output  
cd mcp-server && python server.py

# Terminal 3: Trigger events
cd mcp-server && python test_client.py test-files/api-keys.credentials
```

## 📚 Learning Resources

- [OpenID SSF Specification](https://openid.net/specs/openid-sharedsignals-framework-1_0.html)
- [CAEP Specification](https://openid.net/specs/openid-caep-1_0.html) 
- [MCP Documentation](https://modelcontextprotocol.io)
- [caep.dev Testing Service](https://caep.dev) - Free CAEP transmitter by SGNL
- [Shared Signals Guide](https://sharedsignals.guide/) - Community documentation

## 🎓 Lab Extensions

### Beginner Extensions
1. **New File Patterns**: Add monitoring for `.env`, `.key`, `.pem` files
2. **Risk Levels**: Implement medium/low risk events for different patterns
3. **Time-based Events**: Add business hours vs off-hours risk assessment

### Intermediate Extensions  
1. **OAuth Integration**: Add proper authentication to receiver endpoints
2. **Event Persistence**: Store events in database for historical analysis
3. **Multiple Receivers**: Configure load balancing across receivers

### Advanced Extensions
1. **Custom CAEP Events**: Implement non-standard event types
2. **Stream Management**: Add SSF stream configuration and management
3. **Production Deployment**: Docker compose with proper security
4. **Real Integration**: Connect with actual identity providers (Okta, Auth0)

---

*This is an educational lab for learning SSF/CAEP concepts. Not for production use.*