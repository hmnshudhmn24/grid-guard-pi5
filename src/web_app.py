# Copyright 2024 GridGuard-Pi5 Contributors
# Licensed under the Apache License, Version 2.0

"""Web dashboard and API"""

from flask import Flask, render_template_string, jsonify
import logging

logger = logging.getLogger(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GridGuard-Pi5</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header { text-align: center; color: white; margin-bottom: 30px; }
        h1 { font-size: 2.8em; margin-bottom: 10px; }
        .warning { background: #ff9800; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        .card h2 { color: #667eea; margin-bottom: 15px; }
        .metric { font-size: 2.5em; font-weight: bold; color: #667eea; margin: 10px 0; }
        .reading-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
        .reading-item { padding: 12px; background: #f8f9fa; border-radius: 8px; }
        .reading-label { font-size: 0.85em; color: #666; }
        .reading-value { font-size: 1.8em; font-weight: bold; color: #667eea; margin-top: 5px; }
        .unit { font-size: 0.6em; color: #999; }
        .status-ok { color: #4caf50; }
        .status-warning { color: #ff9800; }
        .status-critical { color: #f44336; }
        .fault-item {
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 4px solid;
            background: #fff3cd;
            border-left-color: #ff9800;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚡ GridGuard-Pi5</h1>
            <div>Smart Electrical Monitoring System</div>
            <div class="warning">⚠️ CAUTION: Monitoring live electrical circuits</div>
        </header>
        
        <div class="dashboard">
            <div class="card">
                <h2>System Status</h2>
                <p>Status: <span id="status" class="status-ok">Operational</span></p>
                <p>Last Update: <span id="last-update">--</span></p>
            </div>
            
            <div class="card" style="grid-column: span 2;">
                <h2>Circuit Readings</h2>
                <div id="circuits" class="reading-grid">
                    <p>Loading...</p>
                </div>
            </div>
            
            <div class="card">
                <h2>Energy Today</h2>
                <div class="metric" id="energy-kwh">0.00 <span class="unit">kWh</span></div>
                <div id="energy-cost">Cost: $0.00</div>
            </div>
            
            <div class="card">
                <h2>Recent Faults</h2>
                <div id="faults">No faults detected</div>
            </div>
        </div>
    </div>
    
    <script>
        async function updateDashboard() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                document.getElementById('status').textContent = data.status;
                document.getElementById('last-update').textContent = new Date(data.timestamp).toLocaleTimeString();
                
                // Update circuits
                const circuitsHtml = Object.entries(data.readings || {}).map(([id, reading]) => `
                    <div class="reading-item">
                        <div class="reading-label">Circuit ${id}</div>
                        <div class="reading-value">${reading.voltage.toFixed(1)} <span class="unit">V</span></div>
                        <div>${reading.current.toFixed(2)} A | ${reading.power.toFixed(0)} W</div>
                    </div>
                `).join('');
                document.getElementById('circuits').innerHTML = circuitsHtml || '<p>No data</p>';
                
                // Update energy
                if (data.energy_today) {
                    document.getElementById('energy-kwh').innerHTML = `${data.energy_today.energy_kwh.toFixed(2)} <span class="unit">kWh</span>`;
                    document.getElementById('energy-cost').textContent = `Cost: $${data.energy_today.cost.toFixed(2)}`;
                }
                
                // Update faults
                const faultsHtml = (data.recent_faults || []).map(fault => `
                    <div class="fault-item">
                        <strong>${fault.fault_type}</strong> - Circuit ${fault.circuit_id}<br>
                        ${fault.description}
                    </div>
                `).join('');
                document.getElementById('faults').innerHTML = faultsHtml || '<p>No faults detected</p>';
                
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        updateDashboard();
        setInterval(updateDashboard, 2000);
    </script>
</body>
</html>
"""


def create_app(gridguard):
    """Create Flask application"""
    app = Flask(__name__)
    app.config['gridguard'] = gridguard
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/status')
    def get_status():
        try:
            status = gridguard.get_status()
            return jsonify(status)
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy', 'version': '1.0.0'})
    
    return app
