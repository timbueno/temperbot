import unittest
import json
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from app.views import app
from app.database import store_temperature, init_db
from config import TEMPERATURE_THRESHOLD, TEMPERATURE_NORMAL_MARGIN

class TestAPI(unittest.TestCase):
    def setUp(self):
        """Set up test client and test data."""
        # Use a test database
        self.test_db_path = '/tmp/test_temperature.db'
        os.environ['DB_PATH'] = self.test_db_path
        init_db()
        
        self.app = app.test_client()
        self.app.testing = True
        
        # Store some test data
        self.test_temp = 22.5
        store_temperature(self.test_temp)
        
    def tearDown(self):
        """Clean up test database after each test."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
    def test_get_temperature_history(self):
        """Test the temperature history endpoint."""
        response = self.app.get('/temperature/history')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        self.assertIn('temperature', data[0])
        self.assertIn('collected_at', data[0])
        
    def test_get_temperature_history_time_range(self):
        """Test temperature history endpoint with time range parameters."""
        # Clear the test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        init_db()
        
        # Store a reading with specific timestamp
        test_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        with patch('app.database.datetime') as mock_datetime:
            mock_datetime.now.return_value = test_time
            store_temperature(23.0)
            
        # Test with time range that includes the reading
        # Format times in ISO format with Z suffix
        start_time = (test_time - timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time = (test_time + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ')
        response = self.app.get(f'/temperature/history?start_time={start_time}&end_time={end_time}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['temperature'], 23.0)
        
    def test_get_temperature_history_invalid_dates(self):
        """Test temperature history endpoint with invalid date parameters."""
        # Test with invalid start_time
        response = self.app.get('/temperature/history?start_time=invalid')
        self.assertEqual(response.status_code, 400)
        
        # Test with invalid end_time
        response = self.app.get('/temperature/history?end_time=invalid')
        self.assertEqual(response.status_code, 400)
        
        # Test with start_time after end_time
        now = datetime.now(timezone.utc)
        start_time = (now + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        end_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        response = self.app.get(f'/temperature/history?start_time={start_time}&end_time={end_time}')
        self.assertEqual(response.status_code, 400)
        
    def test_get_latest_temperature(self):
        """Test the latest temperature endpoint."""
        response = self.app.get('/temperature/latest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('temperature', data)
        self.assertIn('collected_at', data)
        self.assertIn('is_alert', data)
        self.assertIn('is_normal', data)
        self.assertEqual(data['temperature'], self.test_temp)
        
    def test_get_latest_temperature_no_data(self):
        """Test latest temperature endpoint when no data is available."""
        # Clear the test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        init_db()
        
        response = self.app.get('/temperature/latest')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No temperature readings available')
            
    def test_temperature_display_page(self):
        """Test the main temperature display page."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TemperBot', response.data)
        self.assertIn(str(self.test_temp).encode(), response.data)
        
    def test_temperature_alert_states(self):
        """Test temperature alert states in latest temperature endpoint."""
        # Test temperature above threshold
        store_temperature(TEMPERATURE_THRESHOLD + 1)
        response = self.app.get('/temperature/latest')
        data = json.loads(response.data)
        self.assertTrue(data['is_alert'])
        self.assertFalse(data['is_normal'])
        
        # Test temperature below normal margin
        store_temperature(TEMPERATURE_THRESHOLD - TEMPERATURE_NORMAL_MARGIN - 0.1)
        response = self.app.get('/temperature/latest')
        data = json.loads(response.data)
        self.assertFalse(data['is_alert'])
        self.assertTrue(data['is_normal'])
        
        # Test temperature in hysteresis zone
        store_temperature(TEMPERATURE_THRESHOLD - TEMPERATURE_NORMAL_MARGIN + 0.5)
        response = self.app.get('/temperature/latest')
        data = json.loads(response.data)
        self.assertFalse(data['is_alert'])
        self.assertFalse(data['is_normal'])

if __name__ == '__main__':
    unittest.main() 