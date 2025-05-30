from app.temper import Temper
from config import TEMPERATURE_SOURCE

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
            
        return sensor_data[temp_key]
        
    except Exception as e:
        print(f"Error reading temperature: {str(e)}")
        return None 