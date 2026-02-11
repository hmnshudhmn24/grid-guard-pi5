# Contributing to GridGuard-Pi5

Thank you for your interest in contributing!

## Safety First

All contributions must maintain the safety-first approach:
- Include appropriate safety warnings
- Never encourage unsafe practices
- Validate all electrical calculations
- Test thoroughly before release

## How to Contribute

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

## Development Setup

```bash
git clone https://github.com/yourusername/gridguard-pi5.git
cd gridguard-pi5
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Code Style

- Follow PEP 8
- Add docstrings to all functions
- Include safety comments where applicable
- Test on actual Raspberry Pi 5

## Testing

```bash
pytest tests/ -v
```

## Sensor Integration

When adding new sensors:
1. Add sensor class in `src/sensors.py`
2. Update configuration schema
3. Add calibration instructions
4. Test with simulation mode
5. Test with actual hardware
6. Update documentation

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
