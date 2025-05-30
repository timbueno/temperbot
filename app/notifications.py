from apprise import Apprise
from config import (
    PUSHOVER_USER_KEY, 
    PUSHOVER_API_TOKEN, 
    TEMPERATURE_THRESHOLD,
    TEMPERATURE_NORMAL_MARGIN,
    NOTIFICATION_COOLDOWN
)
from datetime import datetime, timezone

# Track the last notification time and alert state
_last_notification_time = None
_is_in_alert_state = False

def send_temperature_alert(temperature: float, is_normal: bool = False) -> bool:
    """Send a Pushover notification about temperature status.
    
    Args:
        temperature: Current temperature reading in Celsius
        is_normal: If True, sends a normal notification instead of an alert
        
    Returns:
        bool: True if notification was sent successfully
    """
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        print("Pushover credentials not configured")
        return False
        
    if is_normal:
        return _send_notification(
            "Temperature Normal",
            f"Temperature has returned to normal: {temperature}°C (threshold: {TEMPERATURE_THRESHOLD}°C)"
        )
    else:
        return _send_notification(
            "Temperature Alert",
            f"Temperature has exceeded threshold: {temperature}°C (threshold: {TEMPERATURE_THRESHOLD}°C)"
        )

def _send_notification(title: str, body: str) -> bool:
    """Helper function to send a notification.
    
    Args:
        title: Notification title
        body: Notification body
        
    Returns:
        bool: True if notification was sent successfully
    """
    # Initialize Apprise
    apobj = Apprise()
    
    # Add Pushover notification
    # Format: pover://user_key@api_token
    pushover_url = f"pover://{PUSHOVER_USER_KEY}@{PUSHOVER_API_TOKEN}"
    apobj.add(pushover_url)
    
    try:
        success = apobj.notify(
            title=title,
            body=body,
            body_format="text"
        )
        print(f"Notification sent successfully: {success}")
        return success
    except Exception as e:
        print(f"Failed to send notification: {str(e)}")
        return False 