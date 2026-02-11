# Copyright 2024 GridGuard-Pi5 Contributors
# Licensed under the Apache License, Version 2.0

"""Database operations"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    """Handles database operations"""
    
    def __init__(self, config):
        self.config = config
        db_path = config.get('path', 'data/gridguard.db')
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        logger.info(f"Database initialized: {db_path}")
    
    def _create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                circuit_id INTEGER,
                voltage REAL,
                current REAL,
                power REAL,
                power_factor REAL,
                frequency REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faults (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                circuit_id INTEGER,
                fault_type TEXT,
                severity TEXT,
                description TEXT,
                value REAL,
                resolved BOOLEAN DEFAULT 0
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_faults_timestamp ON faults(timestamp)")
        
        self.conn.commit()
    
    def save_reading(self, circuit_id, data, analysis):
        """Save power reading"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO readings (circuit_id, voltage, current, power, power_factor, frequency)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            circuit_id,
            data['voltage'],
            data['current'],
            data['power'],
            data['power_factor'],
            data['frequency']
        ))
        self.conn.commit()
    
    def save_fault(self, fault):
        """Save detected fault"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO faults (timestamp, circuit_id, fault_type, severity, description, value)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            fault['timestamp'],
            fault['circuit_id'],
            fault['type'],
            fault['severity'],
            fault['description'],
            fault.get('value')
        ))
        self.conn.commit()
    
    def get_recent_faults(self, limit=10):
        """Get recent faults"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM faults 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database closed")
