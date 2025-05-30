from datetime import timedelta
import os
from dotenv import load_dotenv

def safe_int(value: str, default: int) -> int:
    """Safely convert a string to an integer, returning default if conversion fails."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: str, default: float) -> float:
    """Safely convert a string to a float, returning default if conversion fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_PATH = os.getenv('DB_PATH', '/tmp/temperature.db')

# Data retention
DATA_RETENTION_PERIOD = timedelta(days=safe_int(os.getenv('DATA_RETENTION_DAYS'), 14))

# Polling interval
POLL_INTERVAL_MINUTES = safe_int(os.getenv('POLL_INTERVAL_MINUTES'), 1)

# Temperature alert configuration
TEMPERATURE_THRESHOLD = safe_float(os.getenv('TEMPERATURE_THRESHOLD'), 23.5)
TEMPERATURE_NORMAL_MARGIN = safe_float(os.getenv('TEMPERATURE_NORMAL_MARGIN'), 1.0)

# Temperature source configuration
TEMPERATURE_SOURCE = os.getenv('TEMPERATURE_SOURCE', 'external').lower()  # 'internal' or 'external'

# Pushover configuration
PUSHOVER_USER_KEY = os.getenv('PUSHOVER_USER_KEY', 'your_pushover_user_key_here')
PUSHOVER_API_TOKEN = os.getenv('PUSHOVER_API_TOKEN', 'your_pushover_api_token_here')

# Notification settings
NOTIFICATION_COOLDOWN = timedelta(hours=safe_int(os.getenv('NOTIFICATION_COOLDOWN_HOURS'), 1)) 