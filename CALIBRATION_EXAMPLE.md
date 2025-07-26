# Temperature Calibration Usage Guide

This application now supports temperature calibration to adjust readings from your Temper device for better accuracy.

## How It Works

The calibration system uses linear interpolation between calibration points to adjust raw temperature readings from the device to actual temperatures.

## Configuration

Edit the `TEMPERATURE_CALIBRATION_DATA` array in `config.py`:

### Simple Offset Correction (Single Point)

If your device consistently reads high or low by a fixed amount:

```python
# Device reads 2°C higher than actual
TEMPERATURE_CALIBRATION_DATA = [{"temp": 20, "actual": 18}]
```

### Linear Calibration (Two Points)

For more accurate calibration using two reference points:

```python
# Device reads 5°C when actual is 0°C, device reads 25°C when actual is 20°C
TEMPERATURE_CALIBRATION_DATA = [
    {"temp": 5, "actual": 0},
    {"temp": 25, "actual": 20}
]
```

### Multi-Point Calibration

For complex calibration curves, use multiple points:

```python
TEMPERATURE_CALIBRATION_DATA = [
    {"temp": 0, "actual": -2},
    {"temp": 10, "actual": 8},
    {"temp": 20, "actual": 18},
    {"temp": 30, "actual": 28}
]
```

## How to Calibrate Your Device

1. **Gather Reference Data**: Use a calibrated thermometer to measure actual temperatures
2. **Record Device Readings**: Note what your Temper device reads at the same time
3. **Create Calibration Points**: Create `{"temp": device_reading, "actual": true_temperature}` entries
4. **Update Configuration**: Add the calibration data to `config.py`
5. **Restart Application**: Restart the temperature monitoring service

## Example Calibration Process

1. Place both your Temper device and a reference thermometer in ice water (0°C)
   - Temper device reads: 5°C
   - Reference thermometer: 0°C
   - Calibration point: `{"temp": 5, "actual": 0}`

2. Place both devices in room temperature environment
   - Temper device reads: 25°C  
   - Reference thermometer: 20°C
   - Calibration point: `{"temp": 25, "actual": 20}`

3. Update config.py:
```python
TEMPERATURE_CALIBRATION_DATA = [
    {"temp": 5, "actual": 0},
    {"temp": 25, "actual": 20}
]
```

## Behavior

- **No calibration data**: Raw temperature readings are used unchanged
- **Single point**: Simple offset is applied to all readings
- **Multiple points**: Linear interpolation between points, extrapolation beyond range
- **Automatic sorting**: Calibration points are automatically sorted by device temperature

The calibration is applied automatically to all temperature readings before they are stored in the database or displayed on the web interface.