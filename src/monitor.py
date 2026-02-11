# Copyright 2024 GridGuard-Pi5 Contributors
# Licensed under the Apache License, Version 2.0

"""Power monitoring module"""

import logging
import math

logger = logging.getLogger(__name__)


class PowerMonitor:
    """Real-time power monitoring"""
    
    def __init__(self, sensors, config):
        self.sensors = sensors
        self.config = config
        self.nominal_voltage = config['electrical']['nominal_voltage']
    
    def read_all_circuits(self):
        """Read all configured circuits"""
        readings = {}
        
        # Read voltage (common for all circuits)
        voltage = self.sensors.read_voltage()
        
        # Read each current sensor
        for i, current_config in enumerate(self.config['sensors']['current']):
            circuit_id = i + 1
            current = self.sensors.read_current(current_config)
            
            # Calculate power metrics
            apparent_power = voltage * current
            power_factor = 0.95  # Assumed (would need phase measurement for actual)
            real_power = apparent_power * power_factor
            reactive_power = apparent_power * math.sin(math.acos(power_factor))
            
            readings[circuit_id] = {
                'voltage': voltage,
                'current': current,
                'power': real_power,
                'apparent_power': apparent_power,
                'reactive_power': reactive_power,
                'power_factor': power_factor,
                'frequency': 60.0  # Assumed
            }
        
        return readings
    
    def read_circuit(self, circuit_id):
        """Read specific circuit"""
        all_readings = self.read_all_circuits()
        return all_readings.get(circuit_id)
