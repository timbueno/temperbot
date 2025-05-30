# TemperBot

A robust temperature monitoring system built with Python, Flask, and Docker. This application periodically reads temperature data from a sensor, stores it in a SQLite database, and provides an API to access the temperature history.

## Features

- 🔄 Automatic temperature polling at configurable intervals
- 💾 SQLite database for temperature data storage
- 🌐 RESTful API for accessing temperature history
- 🐳 Docker containerization for easy deployment
- 🔔 Configurable data retention period
- 🧪 Comprehensive test suite

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)

## Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd temperbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```
   POLL_INTERVAL_MINUTES=5
   DATA_RETENTION_PERIOD=7  # days
   ```

### Docker Deployment

1. Build and run using Docker Compose:
   ```bash
   docker-compose up --build
   ```

## Usage

### Local Development

1. Start the application:
   ```bash
   python3 run.py
   ```

2. In a separate terminal, start the temperature polling service:
   ```bash
   python3 poll_temp.py
   ```

3. Access the API at `http://localhost:5000/temperature/history`

### Docker Deployment

The application runs in two containers:
- Web server (Flask API)
- Temperature polling service

Access the API at `http://localhost:5000/temperature/history`

## API Endpoints

### Health Check
- `GET /health`
  - Returns the health status of the application
  - Response: `{"status": "healthy", "timestamp": "ISO timestamp"}`

### Temperature History
- `GET /temperature/history`
  - Returns temperature readings within a specified time range
  - Query Parameters:
    - `start_time`: ISO format timestamp (default: 14 days ago)
    - `end_time`: ISO format timestamp (default: now)
  - Example: `/temperature/history?start_time=2024-03-01T00:00:00Z&end_time=2024-03-14T23:59:59Z`
  - Response: Array of temperature readings, each containing:
    - `temperature`: Float value of the temperature
    - `collected_at`: ISO timestamp of when the reading was taken

### Latest Temperature
- `GET /temperature/latest`
  - Returns the most recent temperature reading
  - Response includes:
    - `temperature`: Current temperature value
    - `collected_at`: Timestamp of the reading
    - `is_alert`: Boolean indicating if temperature is above threshold
    - `is_normal`: Boolean indicating if temperature is below threshold minus margin

### Hourly Temperatures
- `GET /temperature/hourly`
  - Returns temperature readings from the past hour
  - No query parameters required
  - Response: Array of temperature readings, each containing:
    - `temperature`: Float value of the temperature
    - `collected_at`: ISO timestamp of when the reading was taken

### Web Interface
- `GET /`
  - Displays the latest temperature in a simple HTML page
  - Auto-refreshes based on the polling interval
  - Shows alert status based on temperature thresholds

## Project Structure

```
.
├── app/                    # Application package
├── tests/                  # Test suite
├── config.py              # Configuration settings
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile            # Docker build instructions
├── poll_temp.py          # Temperature polling script
├── requirements.txt      # Python dependencies
└── run.py               # Application entry point
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

The project follows PEP 8 guidelines. Use a linter to ensure code quality.

## License

[Add your license here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 