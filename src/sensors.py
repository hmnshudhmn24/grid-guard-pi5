# Copyright 2024 GridGuard-Pi5 Contributors
# Licensed under the Apache License, Version 2.0

"""Sensor management module"""

import logging
import time
import numpy as np

logger = logging.getLogger(__name__)

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    HAS_ADC = True
except ImportError:
    HAS_ADC = False
    logger.warning("ADS1115 library not available - using simulation mode")


class SensorManager:
    """Manages all sensors"""
    
    def __init__(self, sensor_config, adc_config):
        self.sensor_config = sensor_config
        self.adc_config = adc_config
        self.simulation_mode = not HAS_ADC
        
        if not self.simulation_mode:
            self._init_adc()
        
        logger.info(f"SensorManager initialized ({'simulation' if self.simulation_mode else 'hardware'})")
    
    def _init_adc(self):
        """Initialize ADC"""
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(i2c, address=self.adc_config['i2c_address'])
            logger.info(f"ADS1115 initialized at 0x{self.adc_config['i2c_address']:02x}")
        except Exception as e:
            logger.error(f"Failed to initialize ADC: {e}")
            self.simulation_mode = True
    
    def read_current(self, channel_config):
        """Read current from sensor"""
        if self.simulation_mode:
            return np.random.uniform(5, 15)  # Simulated current
        
        try:
            chan = AnalogIn(self.ads, channel_config['channel'])
            voltage = chan.voltage
            
            # Convert voltage to current
            current = (voltage - channel_config['offset']) / channel_config['sensitivity']
            return abs(current)
        except Exception as e:
            logger.error(f"Error reading current: {e}")
            return 0.0
    
    def read_voltage(self):
        """Read voltage"""
        if self.simulation_mode:
            return np.random.uniform(118, 122)  # Simulated voltage
        
        try:
            v_config = self.sensor_config['voltage']
            chan = AnalogIn(self.ads, v_config['channel'])
            measured_voltage = chan.voltage
            
            # Scale to actual voltage
            actual_voltage = (measured_voltage - v_config.get('offset', 0)) * v_config.get('divider_ratio', 1)
            return actual_voltage
        except Exception as e:
            logger.error(f"Error reading voltage: {e}")
            return 0.0
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Sensor cleanup complete")
