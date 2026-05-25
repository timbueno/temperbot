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

### Device Access Setup

> **Note:** Different TEMPer device models may have different vendor and product IDs. For a comprehensive list of supported devices and their IDs, please refer to the [temper library documentation](https://github.com/ccwienk/temper). The documentation includes detailed information about various TEMPer models and their corresponding USB identifiers.

To ensure proper access to the temperature sensor and give it a stable name, create a udev rule on the Proxmox host. The TEMPer device can expose more than one `hidraw` interface, and only one of them responds to the firmware and temperature commands. A broad vendor/product rule may point `/dev/temperbot` at the wrong interface.

First, identify the working `hidraw` interface:

```bash
ls -l /sys/class/hidraw/
```

For example, a working TEMPer interface may look like this:

```text
hidraw4 -> ../../devices/.../usb1/1-8/1-8:1.1/0003:3553:A001.0005/hidraw/hidraw4
```

In that example, create `/etc/udev/rules.d/99-temperbot.rules` with the USB interface path `1-8:1.1`:

```udev
KERNEL=="hidraw*", SUBSYSTEM=="hidraw", KERNELS=="1-8:1.1", SYMLINK+="temperbot", MODE="0666"
```

If your device is on a different USB port, replace `1-8:1.1` with the value shown in your `/sys/class/hidraw/` output for the working TEMPer interface. The `:1.1` interface was required for the known working TEMPer device; the `:1.0` interface opened successfully but did not return firmware data.

After creating the rule, reload the udev rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=hidraw
ls -l /dev/temperbot
```

Confirm that `/dev/temperbot` points at the expected `hidraw` node. For the example above:

```text
/dev/temperbot -> hidraw4
```

### Proxmox LXC Configuration

If you're running TemperBot in a Proxmox LXC container, you'll need to configure the container to access the USB temperature sensor. Here's how to set it up:

1. First, identify your USB device on the Proxmox host:
   ```bash
   lsusb
   ```

2. Enable USB and hidraw support in the LXC container:
   - Edit the container's configuration file at `/etc/pve/lxc/<container-id>.conf`
   - Add these lines:
     ```
     lxc.cgroup2.devices.allow: a
     lxc.cap.drop:
     lxc.mount.auto: proc:rw sys:rw
     lxc.cgroup2.devices.allow: c 235:* rwm
     lxc.mount.entry: /dev/temperbot dev/temperbot none bind,optional,create=file
     ```

> **Note:** The `/dev/temperbot` symlink is created by the udev rule above and keeps the LXC config stable even when Proxmox renumbers the underlying `/dev/hidrawN` device after a reboot.

3. Restart the LXC container after making these changes.

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

By default, Docker Compose maps `/dev/temperbot` into the container and sets `TEMPERATURE_DEVICE=/dev/temperbot`. If you use a different stable device path, set it before starting Compose:

```bash
export TEMPERATURE_DEVICE=/dev/my-temper-device
docker-compose up --build
```

If deploying with Portainer, make sure the stack includes the equivalent device mapping and environment variable:

```yaml
devices:
  - "/dev/temperbot:/dev/temperbot"
environment:
  - TEMPERATURE_DEVICE=/dev/temperbot
```

To verify the device from inside the running container:

```bash
printenv TEMPERATURE_DEVICE
ls -l /dev/temperbot /dev/hidraw* 2>/dev/null
tail -100 /var/log/supervisor/poller.out.log
```

If the poller logs `Cannot read device firmware identifier`, `/dev/temperbot` is likely pointing at the wrong HID interface. Re-check the host udev rule and confirm the symlink points at the known working `hidraw` node.

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

## Special Thanks

This project uses the [temper](https://github.com/ccwienk/temper) library for communicating with TEMPer USB temperature sensors. Many thanks to the developers and contributors of this library for their work in making these devices accessible through Python.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 

## License

MIT License

Copyright (c) 2024 TemperBot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 
