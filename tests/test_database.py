import unittest
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from app.database import init_db, store_temperature, fetch_temperature_history, get_latest_temperature
from config import DATA_RETENTION_PERIOD

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up test database before each test."""
        # Use a test database file
        self.test_db_path = '/tmp/test_temperature.db'
        # Remove any existing test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        # Set environment variable before importing database module
        os.environ['DB_PATH'] = self.test_db_path
        # Re-initialize the database
        init_db()
        
    def tearDown(self):
        """Clean up test database after each test."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
    def test_store_and_fetch_temperature(self):
        """Test storing and retrieving temperature readings."""
        # Store a test temperature
        test_temp = 22.5
        store_temperature(test_temp)
        
        # Fetch recent readings
        readings = fetch_temperature_history(
            datetime.now(timezone.utc) - timedelta(minutes=5),
            datetime.now(timezone.utc)
        )
        
        # Verify the reading was stored and retrieved correctly
        self.assertEqual(len(readings), 1)
        self.assertEqual(readings[0]['temperature'], test_temp)
        
    def test_data_retention(self):
        """Test that old data is automatically cleaned up."""
        # Store some old data
        old_time = datetime.now(timezone.utc) - DATA_RETENTION_PERIOD - timedelta(days=1)
        with sqlite3.connect(self.test_db_path) as conn:
            c = conn.cursor()
            c.execute(
                'INSERT INTO temperature_readings (temperature, timestamp) VALUES (?, ?)',
                (22.5, old_time.isoformat())
            )
            conn.commit()
            
        # Store new data to trigger cleanup
        store_temperature(23.0)
        
        # Verify old data is gone
        readings = fetch_temperature_history(
            datetime.now(timezone.utc) - timedelta(days=15),
            datetime.now(timezone.utc)
        )
        self.assertEqual(len(readings), 1)
        self.assertEqual(readings[0]['temperature'], 23.0)
        
    def test_fetch_temperature_history_time_range(self):
        """Test fetching temperature history within a specific time range."""
        # Store multiple readings at different times
        base_time = datetime.now(timezone.utc)
        times = [
            base_time - timedelta(minutes=30),
            base_time - timedelta(minutes=20),
            base_time - timedelta(minutes=10)
        ]
        
        for i, time in enumerate(times):
            with sqlite3.connect(self.test_db_path) as conn:
                c = conn.cursor()
                c.execute(
                    'INSERT INTO temperature_readings (temperature, timestamp) VALUES (?, ?)',
                    (22.0 + i, time.isoformat())
                )
                conn.commit()
        
        # Fetch readings within a specific range that only includes the middle reading
        start_time = base_time - timedelta(minutes=25)  # 25 minutes ago
        end_time = base_time - timedelta(minutes=15)    # 15 minutes ago
        readings = fetch_temperature_history(start_time, end_time)
        
        # Should only get the middle reading
        self.assertEqual(len(readings), 1)
        self.assertEqual(readings[0]['temperature'], 23.0)
        
    def test_store_temperature_validation(self):
        """Test that invalid temperature values are handled properly."""
        # Test with None
        with self.assertRaises(ValueError):
            store_temperature(None)
            
        # Test with non-numeric value
        with self.assertRaises(ValueError):
            store_temperature("not a number")
            
        # Test with extreme values
        with self.assertRaises(ValueError):
            store_temperature(-100)  # Too cold
        with self.assertRaises(ValueError):
            store_temperature(100)   # Too hot
            
    def test_get_latest_temperature(self):
        """Test getting the latest temperature reading."""
        # Initially should be None
        self.assertIsNone(get_latest_temperature())
        
        # Store a reading
        test_temp = 22.5
        store_temperature(test_temp)
        
        # Should now return the stored reading
        latest = get_latest_temperature()
        self.assertIsNotNone(latest)
        self.assertEqual(latest['temperature'], test_temp)

if __name__ == '__main__':
    unittest.main() 