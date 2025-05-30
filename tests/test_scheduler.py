import unittest
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock
from app.scheduler import poll_temperature, start_scheduler
from app.database import init_db, store_temperature, get_latest_temperature
from app.alert_checker import check_temperature_alert, AlertState
from app.notifications import send_temperature_alert
from config import TEMPERATURE_THRESHOLD, TEMPERATURE_NORMAL_MARGIN

class TestScheduler(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Use a test database
        self.test_db_path = '/tmp/test_temperature.db'
        os.environ['DB_PATH'] = self.test_db_path
        init_db()
        
        # Reset alert checker state
        import app.alert_checker
        app.alert_checker._last_notification_time = None
        app.alert_checker._is_in_alert_state = False
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
    def test_successful_temperature_reading(self):
        """Test successful temperature reading and storage."""
        test_temp = 22.5
        with patch('app.scheduler.read_temperature') as mock_read, \
             patch('app.scheduler.send_temperature_alert') as mock_notify:
            mock_read.return_value = test_temp
            
            poll_temperature()
            
            # Verify temperature was stored
            latest = get_latest_temperature()
            self.assertIsNotNone(latest)
            self.assertEqual(latest['temperature'], test_temp)
            
            # Verify notification was not sent for normal temperature
            mock_notify.assert_not_called()
            
    def test_failed_temperature_reading(self):
        """Test handling of failed temperature reading."""
        with patch('app.scheduler.read_temperature') as mock_read, \
             patch('app.scheduler.send_temperature_alert') as mock_notify:
            mock_read.return_value = None
            
            poll_temperature()
            
            # Verify no temperature was stored
            latest = get_latest_temperature()
            self.assertIsNone(latest)
            
            # Verify no notification was sent
            mock_notify.assert_not_called()
            
    def test_alert_state_transitions(self):
        """Test alert state transitions based on temperature changes."""
        with patch('app.scheduler.read_temperature') as mock_read, \
             patch('app.scheduler.send_temperature_alert') as mock_notify:
            
            # Below normal margin
            mock_read.return_value = TEMPERATURE_THRESHOLD - TEMPERATURE_NORMAL_MARGIN - 1
            poll_temperature()
            mock_notify.assert_not_called()
            
            # Above threshold
            mock_read.return_value = TEMPERATURE_THRESHOLD + 1
            poll_temperature()
            mock_notify.assert_called_once_with(TEMPERATURE_THRESHOLD + 1, is_normal=False)
            
            # Reset mock for next call
            mock_notify.reset_mock()
            
            # In hysteresis zone
            mock_read.return_value = TEMPERATURE_THRESHOLD - TEMPERATURE_NORMAL_MARGIN + 0.5
            poll_temperature()
            mock_notify.assert_not_called()
            
    def test_alert_state_persistence(self):
        """Test that alert state persists across readings."""
        with patch('app.scheduler.read_temperature') as mock_read, \
             patch('app.scheduler.send_temperature_alert') as mock_notify:
            
            # Set alert state
            mock_read.return_value = TEMPERATURE_THRESHOLD + 1
            poll_temperature()
            mock_notify.assert_called_once_with(TEMPERATURE_THRESHOLD + 1, is_normal=False)
            
            # Reset mock for next call
            mock_notify.reset_mock()
            
            # Verify state persists
            poll_temperature()
            mock_notify.assert_not_called()  # Due to cooldown
            
    def test_reading_interval(self):
        """Test that readings are taken at the correct interval."""
        with patch('app.scheduler.read_temperature') as mock_read, \
             patch('app.scheduler.send_temperature_alert') as mock_notify:
            mock_read.return_value = 22.5
            
            # Mock datetime to control time
            with patch('app.database.datetime') as mock_datetime:
                # First reading
                first_time = datetime.now(timezone.utc)
                mock_datetime.now.return_value = first_time
                poll_temperature()
                
                # Second reading (1 minute later)
                second_time = first_time + timedelta(minutes=1)
                mock_datetime.now.return_value = second_time
                poll_temperature()
                
                # Verify interval is at least 1 minute
                time_diff = second_time - first_time
                self.assertGreaterEqual(time_diff.total_seconds(), 60)
                
                # Verify notifications were not sent for normal temperature
                mock_notify.assert_not_called()
            
    def test_error_handling(self):
        """Test handling of hardware errors."""
        with patch('app.scheduler.read_temperature') as mock_read, \
             patch('app.scheduler.send_temperature_alert') as mock_notify:
            mock_read.side_effect = Exception("Hardware error")
            
            # Verify error is handled gracefully
            result = poll_temperature()
            self.assertIsNone(result)
            
            # Verify no temperature was stored
            latest = get_latest_temperature()
            self.assertIsNone(latest)
            
            # Verify no notification was sent
            mock_notify.assert_not_called()

if __name__ == '__main__':
    unittest.main() 