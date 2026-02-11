# Copyright 2024 GridGuard-Pi5 Contributors
# Licensed under the Apache License, Version 2.0

"""Fault detection module"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class FaultDetector:
    """Detects electrical faults"""
    
    def __init__(self, config):
        self.config = config
        self.fault_history = []
    
    def check_faults(self, readings, analysis):
        """Check for faults in readings"""
        faults = []
        
        if not self.config.get('enabled', True):
            return faults
        
        for circuit_id, data in readings.items():
            circuit_analysis = analysis.get(circuit_id, {})
            
            # Check overload
            if circuit_analysis.get('current_status') == 'critical':
                faults.append({
                    'circuit_id': circuit_id,
                    'type': 'overload',
                    'severity': 'critical',
                    'description': f"Current {data['current']:.2f}A exceeds safe limit",
                    'timestamp': datetime.now(),
                    'value': data['current']
                })
            
            # Check voltage faults
            voltage_status = circuit_analysis.get('voltage_status')
            if voltage_status in ['critical_low', 'critical_high']:
                faults.append({
                    'circuit_id': circuit_id,
                    'type': 'voltage_fault',
                    'severity': 'critical',
                    'description': f"Voltage {data['voltage']:.1f}V out of safe range",
                    'timestamp': datetime.now(),
                    'value': data['voltage']
                })
        
        return faults
