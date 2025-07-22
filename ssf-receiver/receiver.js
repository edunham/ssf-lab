#!/usr/bin/env node
/**
 * SSF/CAEP Event Receiver (Mock Okta)
 * Receives and processes security events from the MCP server
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

class SSFReceiver {
    constructor(port = 8082) {
        this.app = express();
        this.port = port;
        this.eventLog = [];
        this.setupMiddleware();
        this.setupRoutes();
    }

    setupMiddleware() {
        this.app.use(helmet());
        this.app.use(cors());
        this.app.use(express.json({ limit: '1mb' }));
        
        // Request logging
        this.app.use((req, res, next) => {
            console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
            next();
        });
    }

    setupRoutes() {
        // SSF Configuration endpoint (for discovery)
        this.app.get('/.well-known/ssf-configuration', (req, res) => {
            res.json({
                issuer: 'https://ssf-lab-receiver.example.com',
                delivery_methods_supported: ['push'],
                token_endpoint: 'https://ssf-lab-receiver.example.com/token',
                event_types_supported: [
                    'https://schemas.openid.net/secevent/caep/event-type/session-risk-change'
                ],
                authorization_schemes_supported: ['none'] // For lab purposes
            });
        });

        // Main event reception endpoint  
        this.app.post('/events', (req, res) => {
            try {
                const event = req.body;
                this.processEvent(event);
                res.status(200).json({ status: 'received' });
            } catch (error) {
                console.error('❌ Error processing event:', error.message);
                res.status(400).json({ error: 'Invalid event format' });
            }
        });

        // Dashboard endpoint for viewing events
        this.app.get('/', (req, res) => {
            const html = this.generateDashboard();
            res.send(html);
        });

        // API endpoint for event history
        this.app.get('/api/events', (req, res) => {
            res.json({
                total_events: this.eventLog.length,
                events: this.eventLog.slice(-10) // Last 10 events
            });
        });
    }

    processEvent(event) {
        // Validate SSF SET structure
        if (!event.iss || !event.jti || !event.events) {
            throw new Error('Invalid SSF SET structure');
        }

        const timestamp = new Date().toISOString();
        const eventTypes = Object.keys(event.events);
        
        console.log('\n🚨 SSF EVENT RECEIVED');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log(`📅 Timestamp: ${timestamp}`);
        console.log(`🏷️  Event ID: ${event.jti}`);
        console.log(`👤 Subject: ${event.sub_id?.email || 'Unknown'}`);
        console.log(`📊 Event Types: ${eventTypes.join(', ')}`);
        
        // Process CAEP events
        eventTypes.forEach(eventType => {
            if (eventType.includes('session-risk-change')) {
                const eventData = event.events[eventType];
                console.log(`⚠️  Risk Level: ${eventData.risk_level?.toUpperCase()}`);
                console.log(`📝 Reason: ${eventData.reason_admin?.en}`);
                
                // Simulate policy action
                this.simulatePolicyAction(eventData);
            }
        });
        
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

        // Store in event log
        this.eventLog.push({
            id: event.jti,
            timestamp,
            issuer: event.iss,
            subject: event.sub_id,
            events: event.events,
            processed: true
        });

        // Keep only last 100 events
        if (this.eventLog.length > 100) {
            this.eventLog.shift();
        }
    }

    simulatePolicyAction(eventData) {
        const riskLevel = eventData.risk_level;
        
        switch (riskLevel) {
            case 'high':
                console.log('🔒 POLICY ACTION: Session terminated');
                console.log('📧 POLICY ACTION: Security team notified');
                break;
            case 'medium':
                console.log('⚠️  POLICY ACTION: Additional authentication required');
                break;
            case 'low':
                console.log('📝 POLICY ACTION: Event logged for review');
                break;
            default:
                console.log('📊 POLICY ACTION: Standard monitoring');
        }
    }

    generateDashboard() {
        const recentEvents = this.eventLog.slice(-10).reverse();
        
        return `
<!DOCTYPE html>
<html>
<head>
    <title>SSF/CAEP Event Receiver Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #e1e5e9; padding-bottom: 20px; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #dc3545; }
        .event-list { margin-top: 20px; }
        .event-item { background: #fff; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; margin-bottom: 10px; }
        .event-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .event-id { font-family: monospace; background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
        .risk-high { color: #dc3545; font-weight: bold; }
        .risk-medium { color: #fd7e14; font-weight: bold; }
        .risk-low { color: #198754; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ SSF/CAEP Event Receiver</h1>
            <p>Mock Okta receiver for SSF security events</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">${this.eventLog.length}</div>
                <div>Total Events</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${this.eventLog.filter(e => Date.now() - new Date(e.timestamp).getTime() < 3600000).length}</div>
                <div>Last Hour</div>
            </div>
        </div>
        
        <div class="event-list">
            <h3>Recent Security Events</h3>
            ${recentEvents.length === 0 ? '<p>No events received yet. Try accessing sensitive files through the MCP server!</p>' : ''}
            ${recentEvents.map(event => `
                <div class="event-item">
                    <div class="event-header">
                        <span class="event-id">${event.id}</span>
                        <span>${event.timestamp}</span>
                    </div>
                    ${Object.entries(event.events).map(([type, data]) => `
                        <div>
                            <strong>Risk Level:</strong> 
                            <span class="risk-${data.risk_level}">${data.risk_level?.toUpperCase()}</span>
                        </div>
                        <div><strong>Reason:</strong> ${data.reason_admin?.en}</div>
                        <div><strong>Subject:</strong> ${event.subject?.email}</div>
                    `).join('')}
                </div>
            `).join('')}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 10 seconds
        setTimeout(() => location.reload(), 10000);
    </script>
</body>
</html>`;
    }

    start() {
        this.app.listen(this.port, () => {
            console.log('🚀 SSF/CAEP Event Receiver Started');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log(`📊 Dashboard: http://localhost:${this.port}`);
            console.log(`🔗 Events API: http://localhost:${this.port}/api/events`);
            console.log(`⚙️  Config: http://localhost:${this.port}/.well-known/ssf-configuration`);
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
            console.log('🎯 Ready to receive SSF security events!');
            console.log('');
        });
    }
}

// Start the receiver
const receiver = new SSFReceiver();
receiver.start();