#!/usr/bin/env python3
# Copyright 2024 GridGuard-Pi5 Contributors
# Licensed under the Apache License, Version 2.0

"""Initialize database"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import Database

def main():
    print("Initializing GridGuard-Pi5 database...")
    
    config = {
        'type': 'sqlite',
        'path': 'data/gridguard.db'
    }
    
    db = Database(config)
    print("✓ Database initialized successfully!")
    print(f"  Location: {config['path']}")
    db.close()

if __name__ == '__main__':
    main()
