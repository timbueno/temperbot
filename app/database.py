import sqlite3
import os
from datetime import datetime, timezone
from config import DATA_RETENTION_PERIOD

def get_db_path():
    """Get the database path from environment variable or config."""
    return os.getenv('DB_PATH', '/tmp/temperature.db')

def init_db():
    """Initialize the SQLite database and create the temperature_readings table."""
    db_path = get_db_path()
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS temperature_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def store_temperature(temperature: float):
    """Store a temperature reading with current timestamp.
    
    Args:
        temperature: Temperature reading in Celsius
        
    Raises:
        ValueError: If temperature is None, not a number, or outside valid range (-50 to 50°C)
    """
    # Validate temperature value
    if temperature is None:
        raise ValueError("Temperature cannot be None")
    try:
        temperature = float(temperature)
    except (TypeError, ValueError):
        raise ValueError("Temperature must be a number")
        
    # Validate temperature range (-50°C to 50°C)
    if temperature < -50 or temperature > 50:
        raise ValueError("Temperature must be between -50°C and 50°C")
        
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    # Store new reading
    timestamp = datetime.now(timezone.utc).isoformat()
    c.execute(
        'INSERT INTO temperature_readings (temperature, timestamp) VALUES (?, ?)',
        (temperature, timestamp)
    )
    
    # Delete old readings
    cutoff = (datetime.now(timezone.utc) - DATA_RETENTION_PERIOD).isoformat()
    c.execute('DELETE FROM temperature_readings WHERE timestamp < ?', (cutoff,))
    
    conn.commit()
    conn.close()

def fetch_temperature_history(start_time=None, end_time=None):
    """Fetch temperature readings within the specified time range.
    Returns readings in reverse chronological order (newest first).
    
    Args:
        start_time: datetime object for start of range (default: 14 days ago)
        end_time: datetime object for end of range (default: now)
    """
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    # Use provided times or defaults
    if end_time is None:
        end_time = datetime.now(timezone.utc)
    if start_time is None:
        start_time = end_time - DATA_RETENTION_PERIOD
    
    # Convert to ISO format for SQLite
    start_iso = start_time.isoformat()
    end_iso = end_time.isoformat()
    
    c.execute(
        'SELECT temperature, timestamp FROM temperature_readings WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC',
        (start_iso, end_iso)
    )
    
    readings = [
        {"temperature": temp, "collected_at": ts}
        for temp, ts in c.fetchall()
    ]
    
    conn.close()
    return readings

def get_latest_temperature():
    """Fetch the most recent temperature reading.
    Returns None if no readings are available.
    """
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    c.execute(
        'SELECT temperature, timestamp FROM temperature_readings ORDER BY timestamp DESC LIMIT 1'
    )
    
    result = c.fetchone()
    conn.close()
    
    if result is None:
        return None
        
    return {
        "temperature": result[0],
        "collected_at": result[1]
    } 