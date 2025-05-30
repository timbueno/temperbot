from datetime import datetime, timezone
from enum import Enum, auto
from config import (
    TEMPERATURE_THRESHOLD,
    TEMPERATURE_NORMAL_MARGIN,
    NOTIFICATION_COOLDOWN
)

class AlertState(Enum):
    """Represents the state of a temperature alert."""
    NO_ALERT = auto()
    ALERT_HIGH = auto()
    ALERT_NORMAL = auto()

# Track the last notification time and alert state
_last_notification_time = None
_is_in_alert_state = False

def check_temperature_alert(temperature: float) -> AlertState:
    """Check if a temperature alert should be sent.
    Uses a hysteresis margin to prevent notification flickering.
    
    Args:
        temperature: Current temperature reading in Celsius
        
    Returns:
        AlertState: The current alert state that should be handled
    """
    global _last_notification_time, _is_in_alert_state
    
    now = datetime.now(timezone.utc)
    
    # Handle temperature above threshold
    if temperature >= TEMPERATURE_THRESHOLD:
        _is_in_alert_state = True
        if _last_notification_time is None or (now - _last_notification_time) >= NOTIFICATION_COOLDOWN:
            _last_notification_time = now
            return AlertState.ALERT_HIGH
        return AlertState.NO_ALERT
    
    # Handle temperature below normal margin
    if temperature <= (TEMPERATURE_THRESHOLD - TEMPERATURE_NORMAL_MARGIN):
        if _is_in_alert_state:
            _is_in_alert_state = False
            _last_notification_time = now
            return AlertState.ALERT_NORMAL
        return AlertState.NO_ALERT
    
    # Temperature is in hysteresis zone
    return AlertState.NO_ALERT 