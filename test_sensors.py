#!/usr/bin/env python3
# Copyright 2024 GridGuard-Pi5 Contributors
# Licensed under the Apache License, Version 2.0

"""Sensor testing utility"""

import yaml
from src.sensors import SensorManager

def main():
    print("="*60)
    print("GridGuard-Pi5 Sensor Test")
    print("="*60)
    print("")
    
    # Load configuration
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize sensors
    sensors = SensorManager(config['sensors'], config['adc'])
    
    print("Testing sensors...")
    print("")
    
    # Test voltage
    voltage = sensors.read_voltage()
    print(f"Voltage: {voltage:.2f} V")
    
    # Test current sensors
    for i, current_config in enumerate(config['sensors']['current']):
        current = sensors.read_current(current_config)
        print(f"Current (Channel {current_config['channel']}): {current:.3f} A")
    
    print("")
    print("Test complete!")
    
    sensors.cleanup()

if __name__ == '__main__':
    main()
