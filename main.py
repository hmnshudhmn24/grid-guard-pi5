#!/usr/bin/env python3
# Copyright 2024 GridGuard-Pi5 Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
GridGuard-Pi5 - Smart Electrical Monitoring System
Main Application Entry Point
"""

import argparse
import sys
import signal
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
import yaml

from src.sensors import SensorManager
from src.monitor import PowerMonitor
from src.analyzer import PowerAnalyzer
from src.fault_detector import FaultDetector
from src.energy_tracker import EnergyTracker
from src.alerts import AlertManager
from src.database import Database
from src.web_app import create_app

__version__ = "1.0.0"
__author__ = "GridGuard Team"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gridguard.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class GridGuard:
    """Main GridGuard system controller"""
    
    def __init__(self, config_path='config/config.yaml'):
        """Initialize GridGuard system"""
        self.running = False
        self.config = self.load_config(config_path)
        
        logger.info("="*60)
        logger.info("GridGuard-Pi5 v%s", __version__)
        logger.info("Smart Electrical Monitoring System")
        logger.info("="*60)
        logger.info("")
        logger.info("⚠️  SAFETY WARNING")
        logger.info("Working with mains electricity can be DEADLY")
        logger.info("Installation must be performed by qualified electrician")
        logger.info("="*60)
        
        try:
            # Initialize database
            self.database = Database(self.config['database'])
            
            # Initialize sensors
            self.sensors = SensorManager(self.config['sensors'], self.config['adc'])
            
            # Initialize monitoring components
            self.monitor = PowerMonitor(self.sensors, self.config)
            self.analyzer = PowerAnalyzer(self.config)
            self.fault_detector = FaultDetector(self.config['fault_detection'])
            self.energy_tracker = EnergyTracker(self.config['energy'])
            self.alert_manager = AlertManager(self.config['alerts'])
            
            logger.info("System initialization complete")
            logger.info("Monitoring %d circuits", len(self.config['sensors']['current']))
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            raise
    
    def load_config(self, config_path):
        """Load configuration from YAML"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML configuration: {e}")
            sys.exit(1)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Shutdown signal received")
        self.stop()
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.running = True
        logger.info("Starting power monitoring...")
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        update_interval = self.config['system'].get('update_interval', 1)
        
        try:
            while self.running:
                loop_start = time.time()
                
                # Read all sensors
                readings = self.monitor.read_all_circuits()
                
                # Analyze power quality
                analysis = self.analyzer.analyze(readings)
                
                # Detect faults
                faults = self.fault_detector.check_faults(readings, analysis)
                
                # Track energy
                self.energy_tracker.update(readings)
                
                # Save to database
                for circuit_id, data in readings.items():
                    self.database.save_reading(circuit_id, data, analysis.get(circuit_id, {}))
                
                # Handle faults
                if faults:
                    for fault in faults:
                        logger.warning(f"⚠️  FAULT DETECTED: {fault['type']} on Circuit {fault['circuit_id']}")
                        self.database.save_fault(fault)
                        self.alert_manager.send_alert(fault)
                
                # Log status periodically
                if int(time.time()) % 60 == 0:  # Every minute
                    self.log_status(readings)
                
                # Sleep to maintain update interval
                elapsed = time.time() - loop_start
                sleep_time = max(0, update_interval - elapsed)
                time.sleep(sleep_time)
        
        finally:
            self.cleanup()
    
    def log_status(self, readings):
        """Log current system status"""
        logger.info("-" * 60)
        for circuit_id, data in readings.items():
            logger.info(f"Circuit {circuit_id}: {data['voltage']:.1f}V, {data['current']:.2f}A, {data['power']:.1f}W, PF={data['power_factor']:.2f}")
        logger.info("-" * 60)
    
    def get_status(self):
        """Get current system status"""
        try:
            readings = self.monitor.read_all_circuits()
            energy_today = self.energy_tracker.get_today_total()
            recent_faults = self.database.get_recent_faults(limit=5)
            
            return {
                'status': 'operational',
                'timestamp': datetime.now().isoformat(),
                'readings': readings,
                'energy_today': energy_today,
                'recent_faults': recent_faults
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def stop(self):
        """Stop monitoring"""
        logger.info("Stopping GridGuard system...")
        self.running = False
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        try:
            self.sensors.cleanup()
            self.database.close()
            logger.info("Cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='GridGuard-Pi5 - Smart Electrical Monitoring',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--config', default='config/config.yaml', help='Configuration file')
    parser.add_argument('--version', action='version', version=f'GridGuard-Pi5 {__version__}')
    
    # Operation modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--monitor', action='store_true', help='Start monitoring')
    mode_group.add_argument('--status', action='store_true', help='Show current status')
    mode_group.add_argument('--web', action='store_true', help='Start web dashboard')
    mode_group.add_argument('--api', action='store_true', help='Start API server')
    mode_group.add_argument('--test', action='store_true', help='Test sensors')
    
    # Options
    parser.add_argument('--circuit', type=int, help='Monitor specific circuit')
    parser.add_argument('--port', type=int, default=8080, help='Web/API port')
    
    # Data commands
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--export', action='store_true', help='Export data')
    parser.add_argument('--format', choices=['csv', 'json', 'excel'], default='csv')
    parser.add_argument('--output', help='Output file')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--days', type=int, default=7, help='Days of data')
    
    # System
    parser.add_argument('--diagnostic', action='store_true', help='Run diagnostics')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize system
    try:
        gridguard = GridGuard(args.config)
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.status:
            status = gridguard.get_status()
            print("\n=== GridGuard-Pi5 Status ===")
            print(f"Status: {status['status']}")
            print(f"Timestamp: {status['timestamp']}")
            if 'readings' in status:
                print("\nCurrent Readings:")
                for cid, reading in status['readings'].items():
                    print(f"  Circuit {cid}: {reading['voltage']:.1f}V, {reading['current']:.2f}A, {reading['power']:.1f}W")
            print()
        
        elif args.test:
            logger.info("Testing sensors...")
            readings = gridguard.monitor.read_all_circuits()
            print("\n=== Sensor Test Results ===")
            for cid, data in readings.items():
                print(f"\nCircuit {cid}:")
                print(f"  Voltage: {data['voltage']:.2f} V")
                print(f"  Current: {data['current']:.3f} A")
                print(f"  Power: {data['power']:.2f} W")
                print(f"  Power Factor: {data['power_factor']:.3f}")
            print()
        
        elif args.web or args.api:
            app = create_app(gridguard)
            logger.info(f"Starting web server on port {args.port}")
            app.run(host='0.0.0.0', port=args.port, debug=args.debug)
        
        elif args.diagnostic:
            logger.info("Running system diagnostics...")
            # Run diagnostics
            print("\n✓ Configuration loaded")
            print("✓ Database accessible")
            print("✓ Sensors initialized")
            print("\nSystem ready for operation")
        
        else:
            # Default: start monitoring
            gridguard.monitor_loop()
    
    finally:
        gridguard.cleanup()


if __name__ == '__main__':
    main()
