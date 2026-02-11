# GridGuard-Pi5 Quick Start Guide

## ⚠️ SAFETY FIRST

**DANGER: ELECTRICAL HAZARD**
- Mains electricity can be FATAL
- Installation must be done by licensed electrician
- Never work on live circuits
- Follow local electrical codes

## 🚀 Installation (3 Steps)

### 1. Extract and Navigate
```bash
tar -xzf gridguard-pi5.tar.gz
cd gridguard-pi5
```

### 2. Run Installer
```bash
chmod +x install.sh
sudo ./install.sh
```

### 3. Configure and Calibrate
```bash
# Edit configuration
nano config/config.yaml

# Calibrate sensors (with qualified electrician)
python3 calibrate.py

# Test sensors
python3 main.py --test
```

## 📊 Access Dashboard

Open browser: **http://raspberrypi.local:8080**

Or start manually:
```bash
source venv/bin/activate
python3 main.py --web --port 8080
```

## ⚡ Quick Commands

```bash
# View current status
python3 main.py --status

# Start monitoring
python3 main.py --monitor

# Run diagnostics
python3 main.py --diagnostic

# View statistics
python3 main.py --stats --days 7
```

## 🔧 Troubleshooting

### I2C Not Working
```bash
# Enable I2C
sudo raspi-config
# Interface Options → I2C → Enable

# Test I2C
sudo i2cdetect -y 1
```

### Sensor Errors
```bash
# Check wiring
python3 main.py --test

# Re-calibrate
python3 calibrate.py
```

### Service Issues
```bash
# Check status
sudo systemctl status gridguard

# View logs
sudo journalctl -u gridguard -f

# Restart
sudo systemctl restart gridguard
```

For full documentation, see [README.md](README.md)
