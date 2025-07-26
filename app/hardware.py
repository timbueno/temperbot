from app.temper import Temper
from config import TEMPERATURE_SOURCE, TEMPERATURE_CALIBRATION_DATA

def apply_temperature_calibration(raw_temperature: float) -> float:
    """Apply calibration to raw temperature reading using linear interpolation.
    
    Args:
        raw_temperature: Raw temperature reading from sensor
        
    Returns:
        Calibrated temperature value
    """
    if not TEMPERATURE_CALIBRATION_DATA or len(TEMPERATURE_CALIBRATION_DATA) == 0:
        return raw_temperature
    
    # Sort calibration data by device temperature
    calibration_points = sorted(TEMPERATURE_CALIBRATION_DATA, key=lambda x: x["temp"])
    
    # If only one calibration point, apply simple offset
    if len(calibration_points) == 1:
        point = calibration_points[0]
        offset = point["actual"] - point["temp"]
        return raw_temperature + offset
    
    # Find the two points to interpolate between
    lower_point = None
    upper_point = None
    
    for point in calibration_points:
        if point["temp"] <= raw_temperature:
            lower_point = point
        if point["temp"] >= raw_temperature and upper_point is None:
            upper_point = point
            break
    
    # If temperature is below the lowest calibration point
    if lower_point is None:
        first_point = calibration_points[0]
        second_point = calibration_points[1]
        # Extrapolate using slope from first two points
        slope = (second_point["actual"] - first_point["actual"]) / (second_point["temp"] - first_point["temp"])
        return first_point["actual"] + slope * (raw_temperature - first_point["temp"])
    
    # If temperature is above the highest calibration point
    if upper_point is None:
        last_point = calibration_points[-1]
        second_last_point = calibration_points[-2]
        # Extrapolate using slope from last two points
        slope = (last_point["actual"] - second_last_point["actual"]) / (last_point["temp"] - second_last_point["temp"])
        return last_point["actual"] + slope * (raw_temperature - last_point["temp"])
    
    # If we have exact match
    if lower_point["temp"] == upper_point["temp"]:
        return lower_point["actual"]
    
    # Linear interpolation between two points
    slope = (upper_point["actual"] - lower_point["actual"]) / (upper_point["temp"] - lower_point["temp"])
    return lower_point["actual"] + slope * (raw_temperature - lower_point["temp"])

def read_temperature() -> float:
    """Read temperature from a USB temperature sensor using the Temper class.
    Returns the temperature in Celsius from the configured source (internal or external).
    If no sensor is found or there's an error, returns None.
    """
    try:
        temper = Temper()
        results = temper.read()
        
        if not results:
            print("No temperature sensors found")
            return None
            
        # Get the first sensor's temperature from configured source
        sensor_data = results[0]
        if 'error' in sensor_data:
            print(f"Error reading sensor: {sensor_data['error']}")
            return None
            
        temp_key = f"{TEMPERATURE_SOURCE} temperature"
        if temp_key not in sensor_data:
            print(f"No {TEMPERATURE_SOURCE} temperature reading available")
            return None
            
        raw_temperature = sensor_data[temp_key]
        calibrated_temperature = apply_temperature_calibration(raw_temperature)
        return calibrated_temperature
        
    except Exception as e:
        print(f"Error reading temperature: {str(e)}")
        return None 