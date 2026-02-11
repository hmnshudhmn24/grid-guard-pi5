#!/bin/bash
# Copyright 2024 GridGuard-Pi5 Contributors
# Licensed under the Apache License, Version 2.0

set -e

echo "======================================"
echo "GridGuard-Pi5 Installation"
echo "======================================"
echo ""
echo "⚠️  SAFETY WARNING"
echo "This system works with mains electricity"
echo "Installation must be done by qualified electrician"
echo "======================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Update system
echo "Updating system..."
sudo apt update
sudo apt upgrade -y

# Install dependencies
echo "Installing system dependencies..."
sudo apt install -y \
    python3-pip python3-dev python3-venv \
    i2c-tools python3-smbus \
    postgresql postgresql-contrib \
    nginx

# Enable I2C
echo "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Create virtual environment
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p logs data/{readings,reports} config

# Copy configuration
if [ ! -f config/config.yaml ]; then
    cp config/config.example.yaml config/config.yaml
    print_warning "Created config.yaml - please edit before first use"
fi

# Initialize database
echo "Initializing database..."
python3 scripts/init_db.py

# Install systemd service
echo "Installing systemd service..."
INSTALL_DIR=$(pwd)
cat > gridguard.service << EOF
[Unit]
Description=GridGuard-Pi5 Electrical Monitoring
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/main.py --monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo cp gridguard.service /etc/systemd/system/
sudo systemctl daemon-reload

print_status "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit configuration: nano config/config.yaml"
echo "2. Calibrate sensors: python3 calibrate.py"
echo "3. Test sensors: python3 main.py --test"
echo "4. Start service: sudo systemctl start gridguard"
echo "5. Enable auto-start: sudo systemctl enable gridguard"
echo ""
echo "View logs: sudo journalctl -u gridguard -f"
echo "Web dashboard: http://raspberrypi.local:8080"
