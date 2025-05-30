from apscheduler.schedulers.background import BackgroundScheduler
from app.hardware import read_temperature
from app.database import store_temperature
from app.alert_checker import check_temperature_alert, AlertState
from app.notifications import send_temperature_alert
from config import POLL_INTERVAL_MINUTES

def poll_temperature():
    """Read temperature from sensor, store in database, and check for alerts."""
    try:
        temperature = read_temperature()
        if temperature is not None:
            store_temperature(temperature)
            # Check if we should send an alert
            alert_state = check_temperature_alert(temperature)
            if alert_state != AlertState.NO_ALERT:
                send_temperature_alert(temperature, is_normal=(alert_state == AlertState.ALERT_NORMAL))
    except Exception as e:
        print(f"Error in poll_temperature: {str(e)}")
        return None

def start_scheduler():
    """Initialize and start the background scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        poll_temperature,
        'cron',
        minute=f'*/{POLL_INTERVAL_MINUTES}',  # Run every N minutes, starting at minute 0
        id='temperature_poller'
    )
    scheduler.start()
    return scheduler 