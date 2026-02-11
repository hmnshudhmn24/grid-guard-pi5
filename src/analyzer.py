# Copyright 2024 GridGuard-Pi5 Contributors
# Licensed under the Apache License, Version 2.0

"""Power quality analyzer"""

import logging

logger = logging.getLogger(__name__)


class PowerAnalyzer:
    """Analyzes power quality metrics"""
    
    def __init__(self, config):
        self.config = config
        self.thresholds = config.get('thresholds', {})
    
    def analyze(self, readings):
        """Analyze all readings"""
        analysis = {}
        
        for circuit_id, data in readings.items():
            analysis[circuit_id] = {
                'voltage_status': self._check_voltage(data['voltage']),
                'current_status': self._check_current(data['current']),
                'power_factor_status': self._check_power_factor(data['power_factor']),
                'load_percentage': (data['current'] / self.thresholds['current']['max']) * 100
            }
        
        return analysis
    
    def _check_voltage(self, voltage):
        """Check voltage status"""
        v_thresholds = self.thresholds.get('voltage', {})
        
        if voltage < v_thresholds.get('critical_min', 100):
            return 'critical_low'
        elif voltage > v_thresholds.get('critical_max', 140):
            return 'critical_high'
        elif voltage < v_thresholds.get('min', 108):
            return 'low'
        elif voltage > v_thresholds.get('max', 132):
            return 'high'
        else:
            return 'normal'
    
    def _check_current(self, current):
        """Check current status"""
        c_thresholds = self.thresholds.get('current', {})
        
        if current > c_thresholds.get('critical', 28):
            return 'critical'
        elif current > c_thresholds.get('warning', 24):
            return 'warning'
        else:
            return 'normal'
    
    def _check_power_factor(self, pf):
        """Check power factor"""
        pf_thresholds = self.thresholds.get('power_factor', {})
        
        if pf < pf_thresholds.get('critical', 0.70):
            return 'critical'
        elif pf < pf_thresholds.get('min', 0.85):
            return 'low'
        else:
            return 'good'
