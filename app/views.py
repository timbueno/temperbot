from flask import Flask, jsonify, request, render_template
from app.database import fetch_temperature_history, get_latest_temperature
from datetime import datetime, timezone, timedelta
from config import TEMPERATURE_THRESHOLD, TEMPERATURE_NORMAL_MARGIN, POLL_INTERVAL_MINUTES

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for Docker container monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200

@app.route('/temperature/history')
def get_temperature_history():
    """Return temperature readings within a specified time range.
    
    Query Parameters:
        start_time: ISO format timestamp (default: 14 days ago)
        end_time: ISO format timestamp (default: now)
    
    Example: /temperature/history?start_time=2024-03-01T00:00:00Z&end_time=2024-03-14T23:59:59Z
    """
    # Get current time in UTC
    now = datetime.now(timezone.utc)
    
    # Parse start_time parameter or default to 14 days ago
    start_time = request.args.get('start_time')
    if start_time:
        try:
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid start_time format. Use ISO format (e.g., 2024-03-14T12:00:00Z)"}), 400
    else:
        start_time = now - timedelta(days=14)
    
    # Parse end_time parameter or default to now
    end_time = request.args.get('end_time')
    if end_time:
        try:
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid end_time format. Use ISO format (e.g., 2024-03-14T12:00:00Z)"}), 400
    else:
        end_time = now
    
    # Validate time range
    if start_time > end_time:
        return jsonify({"error": "start_time must be before end_time"}), 400
    
    readings = fetch_temperature_history(start_time, end_time)
    return jsonify(readings)

@app.route('/temperature/latest')
def get_latest():
    """Return the most recent temperature reading."""
    latest = get_latest_temperature()
    if latest is None:
        return jsonify({"error": "No temperature readings available"}), 404
        
    temperature = latest['temperature']
    
    # Check if temperature is above threshold
    is_alert = temperature > TEMPERATURE_THRESHOLD
    is_normal = temperature < (TEMPERATURE_THRESHOLD - TEMPERATURE_NORMAL_MARGIN)
    
    return jsonify({
        "temperature": temperature,
        "collected_at": latest['collected_at'],
        "is_alert": is_alert,
        "is_normal": is_normal
    })

@app.route('/temperature/hourly')
def get_hourly_temperatures():
    """Return temperature readings from the past hour."""
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)
    
    readings = fetch_temperature_history(start_time, end_time)
    return jsonify(readings)

@app.route('/')
def temperature_display():
    """Display the latest temperature in a simple HTML page."""
    latest = get_latest_temperature()
    if not latest:
        return "No temperature readings available", 404
        
    temperature = latest['temperature']
    timestamp = latest['collected_at']
    
    # Check if temperature is above threshold
    is_alert = temperature > TEMPERATURE_THRESHOLD
    is_normal = temperature < (TEMPERATURE_THRESHOLD - TEMPERATURE_NORMAL_MARGIN)
    
    # Calculate refresh interval in milliseconds (poll interval + 10 seconds)
    refresh_interval = (POLL_INTERVAL_MINUTES * 60 + 2) * 1000
    
    return render_template(
        'temperature.html',
        temperature=temperature,
        timestamp=timestamp,
        is_alert=is_alert,
        is_normal=is_normal,
        refresh_interval=refresh_interval,
        temperature_threshold=TEMPERATURE_THRESHOLD
    ) 