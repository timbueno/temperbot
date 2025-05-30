
# 🌡️ Temperature Logger — Architecture Summary

## 🧭 Purpose

This system:
- Polls a USB temperature sensor every 5 minutes
- Stores readings with timestamps in SQLite
- Retains the last **14 days** of data
- Serves a Flask API endpoint to access the historical data
- Runs entirely in Docker using a minimal Python stack
- Is safe for production using Gunicorn and optionally a dedicated scheduler container

---

## 🧱 Components

### 1. **Flask API**
- Serves a single endpoint:
  - `GET /temperature/history` → Returns last 14 days of temperature readings.
- Reads from the SQLite database.
- Runs using **Gunicorn** for production-grade concurrency.

### 2. **APScheduler**
- Runs as a background job scheduler **within Python**.
- Every 5 minutes, it:
  - Polls the temperature from a USB sensor (via `read_temperature()`).
  - Stores the data in SQLite.
  - Deletes records older than 14 days.

### 3. **SQLite**
- Stores time-series data in a file (`/tmp/temperature.db`).
- Lightweight, no separate DB server.
- Data is persisted using a Docker volume in production.

### 4. **Dockerized Runtime**
- The app runs inside a Docker container.
- Exposes Flask on port 5000.
- `docker-compose` can run:
  - One container for the Flask web server
  - Another container for the APScheduler poller process

---

## 📦 Folder Structure

\`\`\`
myproject/
├── app/
│   ├── __init__.py
│   ├── views.py         # Flask API
│   ├── scheduler.py     # APScheduler setup
│   └── database.py      # SQLite logic
├── config.py            # All runtime config
├── run.py               # Flask entrypoint
├── poller.py            # Standalone scheduler process (optional)
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
\`\`\`

---

## ⚙️ Configuration (`config.py`)

\`\`\`python
from datetime import timedelta

DB_PATH = "/tmp/temperature.db"
DATA_RETENTION_PERIOD = timedelta(days=14)
POLL_INTERVAL_MINUTES = 5
\`\`\`

---

## 🐳 Docker

### `Dockerfile`

\`\`\`Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000", "--preload"]
\`\`\`

### `docker-compose.yml`

\`\`\`yaml
version: "3.8"
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - sqlite-data:/tmp
    restart: unless-stopped

  scheduler:
    build: .
    command: python poller.py
    volumes:
      - sqlite-data:/tmp
    restart: unless-stopped

volumes:
  sqlite-data:
\`\`\`

---

## 🧠 APScheduler Handling

### ✅ Option 1: Single Process with `RUN_MAIN` Guard
\`\`\`python
if os.environ.get("RUN_MAIN") == "true":
    start_scheduler()
\`\`\`
Use with Gunicorn `--preload`.

### ✅ Option 2: Separate Scheduler Process (`poller.py`)
\`\`\`python
from app.scheduler import start_scheduler

if __name__ == "__main__":
    start_scheduler()
    while True:
        time.sleep(60)
\`\`\`

---

## 🧪 Example API Response

\`\`\`json
[
  { "temperature": 22.4, "collected_at": "2025-05-28T14:00:00Z" },
  { "temperature": 22.1, "collected_at": "2025-05-28T14:05:00Z" }
]
\`\`\`

---

## ✅ Summary Table

| Component      | Tech         | Role                                |
|----------------|--------------|-------------------------------------|
| Web server     | Flask + Gunicorn | Serves API endpoint                 |
| Scheduler      | APScheduler  | Runs polling job every 5 minutes   |
| Database       | SQLite       | Stores and queries temperature logs |
| Broker         | None         | Lightweight, no Redis/Celery needed |
| Deployment     | Docker       | Isolated, reproducible environment |
| Coordination   | Docker Compose | Runs web and scheduler separately |
