
# 🧱 MVP Build Plan — Temperature Logger

Each task below is a **small, testable unit of work**. You can complete them one-by-one, verifying functionality at each step. This plan assumes the architecture discussed previously (Flask + APScheduler + SQLite in Docker).

---

## ✅ Step 1: Project Setup

### 1.1 Create the Project Directory Structure
- Create folders: `app/`
- Create files: `run.py`, `requirements.txt`, `config.py`

---

## ✅ Step 2: Core Configuration

### 2.1 Create `config.py`
- Add constants: `DB_PATH`, `DATA_RETENTION_PERIOD`, `POLL_INTERVAL_MINUTES`

---

## ✅ Step 3: Database Layer

### 3.1 Implement `init_db()` in `app/database.py`
- Create SQLite database file
- Create `temperature_readings` table with:
  - `id` (auto increment)
  - `temperature` (float)
  - `timestamp` (text)

### 3.2 Implement `store_temperature()` in `app/database.py`
- Insert a temperature + timestamp into DB
- Delete rows older than `DATA_RETENTION_PERIOD`

### 3.3 Implement `fetch_temperature_history()` in `app/database.py`
- Accept a cutoff timestamp
- Return all readings newer than cutoff, ordered by timestamp

---

## ✅ Step 4: Flask API

### 4.1 Create `app/views.py`
- Add a Flask app
- Add route: `GET /temperature/history`
- Use `fetch_temperature_history()` to respond with JSON

### 4.2 Create `run.py`
- Import Flask app from `views.py`
- Run the app

---

## ✅ Step 5: APScheduler Setup

### 5.1 Create `app/scheduler.py`
- Import `BackgroundScheduler`
- Define function `poll_temperature()`:
  - Get timestamp + call `read_temperature()`
  - Store value using `store_temperature()`
- Add job to scheduler (interval = `POLL_INTERVAL_MINUTES`)
- Define `start_scheduler()` to start the scheduler

---

## ✅ Step 6: Mock Sensor Input

### 6.1 Create `my_hardware.py`
- Add function `read_temperature()` that returns a fake float value (e.g., 22.5)

---

## ✅ Step 7: Integrate Scheduler with App

### 7.1 Modify `run.py` to start scheduler
- Use `if os.environ.get("RUN_MAIN") == "true":` to start only once when using Gunicorn

---

## ✅ Step 8: Test API + Polling

### 8.1 Test Locally
- Start app with `python run.py`
- Wait 5+ minutes
- Call `/temperature/history` and verify JSON response

---

## ✅ Step 9: Dockerization

### 9.1 Create `Dockerfile`
- Use `python:3.11-slim`
- Set `WORKDIR /app`
- `COPY . .`
- `RUN pip install -r requirements.txt`
- `CMD gunicorn run:app --bind 0.0.0.0:5000 --preload`

### 9.2 Create `docker-compose.yml`
- One service for `web`
- One service for `scheduler` (using `poller.py`)
- Use a volume for `/tmp` to persist SQLite

---

## ✅ Step 10: Create Scheduler Entrypoint

### 10.1 Create `poller.py`
- Import and run `start_scheduler()`
- Add a `while True: time.sleep(60)` loop to keep it alive

---

## ✅ Step 11: Final Test

### 11.1 Build + Run Docker Containers
- Run `docker-compose up --build`
- Wait 10+ minutes
- Curl `/temperature/history` and confirm values
