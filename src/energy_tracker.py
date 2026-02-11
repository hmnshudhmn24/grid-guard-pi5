# Copyright 2024 GridGuard-Pi5 Contributors
# Licensed under the Apache License, Version 2.0

"""Energy consumption tracker"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EnergyTracker:
    """Tracks energy consumption"""
    
    def __init__(self, config):
        self.config = config
        self.energy_totals = {}
        self.cost_per_kwh = config.get('cost_per_kwh', 0.12)
        self.last_update = datetime.now()
    
    def update(self, readings):
        """Update energy consumption"""
        now = datetime.now()
        time_delta = (now - self.last_update).total_seconds() / 3600  # hours
        
        for circuit_id, data in readings.items():
            if circuit_id not in self.energy_totals:
                self.energy_totals[circuit_id] = 0.0
            
            # Energy = Power (kW) × Time (h)
            energy_kwh = (data['power'] / 1000) * time_delta
            self.energy_totals[circuit_id] += energy_kwh
        
        self.last_update = now
    
    def get_today_total(self):
        """Get today's total energy and cost"""
        total_kwh = sum(self.energy_totals.values())
        total_cost = total_kwh * self.cost_per_kwh
        
        return {
            'energy_kwh': total_kwh,
            'cost': total_cost,
            'currency': 'USD'
        }
