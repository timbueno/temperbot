import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from app.notifications import send_temperature_alert, _send_notification
from app.alert_checker import check_temperature_alert, AlertState
from config import (
    TEMPERATURE_THRESHOLD,
    TEMPERATURE_NORMAL_MARGIN,
    NOTIFICATION_COOLDOWN
)

class TestNotifications(unittest.TestCase):
    def setUp(self):
        # Reset module state before each test
        import app.alert_checker
        app.alert_checker._last_notification_time = None
        app.alert_checker._is_in_alert_state = False

    @patch('app.notifications._send_notification')
    def test_alert_when_above_threshold(self, mock_send):
        """Test that an alert is sent when temperature exceeds threshold"""
        mock_send.return_value = True
        
        # Test temperature above threshold
        alert_state = check_temperature_alert(TEMPERATURE_THRESHOLD + 1)
        self.assertEqual(alert_state, AlertState.ALERT_HIGH)
        
        if alert_state == AlertState.ALERT_HIGH:
            result = send_temperature_alert(TEMPERATURE_THRESHOLD + 1)
            self.assertTrue(result)
            mock_send.assert_called_once_with(
                "Temperature Alert",
                f"Temperature has exceeded threshold: {TEMPERATURE_THRESHOLD + 1}°C (threshold: {TEMPERATURE_THRESHOLD}°C)"
            )

    @patch('app.notifications._send_notification')
    def test_no_alert_when_below_threshold(self, mock_send):
        """Test that no alert is sent when temperature is below threshold"""
        mock_send.return_value = True
        
        # Test temperature below threshold
        alert_state = check_temperature_alert(TEMPERATURE_THRESHOLD - 0.5)
        self.assertEqual(alert_state, AlertState.NO_ALERT)
        mock_send.assert_not_called()

    @patch('app.notifications._send_notification')
    def test_normal_notification_when_below_margin(self, mock_send):
        """Test that normal notification is sent when temperature drops below margin"""
        mock_send.return_value = True
        
        # First trigger an alert
        alert_state = check_temperature_alert(TEMPERATURE_THRESHOLD + 1)
        self.assertEqual(alert_state, AlertState.ALERT_HIGH)
        if alert_state == AlertState.ALERT_HIGH:
            send_temperature_alert(TEMPERATURE_THRESHOLD + 1)
        mock_send.reset_mock()
        
        # Then test temperature below margin
        alert_state = check_temperature_alert(TEMPERATURE_THRESHOLD - TEMPERATURE_NORMAL_MARGIN - 0.1)
        self.assertEqual(alert_state, AlertState.ALERT_NORMAL)
        if alert_state == AlertState.ALERT_NORMAL:
            send_temperature_alert(TEMPERATURE_THRESHOLD - TEMPERATURE_NORMAL_MARGIN - 0.1, is_normal=True)
            mock_send.assert_called_once_with(
                "Temperature Normal",
                f"Temperature has returned to normal: {TEMPERATURE_THRESHOLD - TEMPERATURE_NORMAL_MARGIN - 0.1}°C (threshold: {TEMPERATURE_THRESHOLD}°C)"
            )

    @patch('app.notifications._send_notification')
    def test_no_notification_in_hysteresis_zone(self, mock_send):
        """Test that no notifications are sent when temperature is in hysteresis zone"""
        mock_send.return_value = True
        
        # First trigger an alert
        alert_state = check_temperature_alert(TEMPERATURE_THRESHOLD + 1)
        self.assertEqual(alert_state, AlertState.ALERT_HIGH)
        if alert_state == AlertState.ALERT_HIGH:
            send_temperature_alert(TEMPERATURE_THRESHOLD + 1)
        mock_send.reset_mock()
        
        # Test temperature in hysteresis zone
        alert_state = check_temperature_alert(TEMPERATURE_THRESHOLD - TEMPERATURE_NORMAL_MARGIN + 0.5)
        self.assertEqual(alert_state, AlertState.NO_ALERT)
        mock_send.assert_not_called()

    @patch('app.notifications._send_notification')
    def test_cooldown_respected_for_alerts(self, mock_send):
        """Test that cooldown period is respected for alert notifications"""
        mock_send.return_value = True
        
        # First alert
        alert_state = check_temperature_alert(TEMPERATURE_THRESHOLD + 1)
        self.assertEqual(alert_state, AlertState.ALERT_HIGH)
        if alert_state == AlertState.ALERT_HIGH:
            send_temperature_alert(TEMPERATURE_THRESHOLD + 1)
        mock_send.reset_mock()
        
        # Simulate time passing but still in cooldown
        with patch('app.alert_checker.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now(timezone.utc) + NOTIFICATION_COOLDOWN - timedelta(minutes=1)
            mock_datetime.timezone = timezone
            
            # Try to send another alert
            alert_state = check_temperature_alert(TEMPERATURE_THRESHOLD + 2)
            self.assertEqual(alert_state, AlertState.NO_ALERT)
            mock_send.assert_not_called()

    @patch('app.notifications._send_notification')
    def test_cooldown_expired_allows_new_alert(self, mock_send):
        """Test that new alerts can be sent after cooldown period expires"""
        # Setup mock to always return True
        mock_send.return_value = True
        
        # Create fixed timestamps for testing
        base_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
        after_cooldown = base_time + NOTIFICATION_COOLDOWN + timedelta(minutes=1)
        
        # First alert
        with patch('app.alert_checker.datetime') as mock_datetime:
            mock_datetime.now.return_value = base_time
            mock_datetime.timezone = timezone
            
            alert_state = check_temperature_alert(TEMPERATURE_THRESHOLD + 1)
            self.assertEqual(alert_state, AlertState.ALERT_HIGH, "First alert should be sent")
            if alert_state == AlertState.ALERT_HIGH:
                send_temperature_alert(TEMPERATURE_THRESHOLD + 1)
            mock_send.reset_mock()
        
        # Second alert after cooldown
        with patch('app.alert_checker.datetime') as mock_datetime:
            mock_datetime.now.return_value = after_cooldown
            mock_datetime.timezone = timezone
            
            alert_state = check_temperature_alert(TEMPERATURE_THRESHOLD + 2)
            self.assertEqual(alert_state, AlertState.ALERT_HIGH, "Second alert should be sent after cooldown")
            if alert_state == AlertState.ALERT_HIGH:
                send_temperature_alert(TEMPERATURE_THRESHOLD + 2)
                mock_send.assert_called_once_with(
                    "Temperature Alert",
                    f"Temperature has exceeded threshold: {TEMPERATURE_THRESHOLD + 2}°C (threshold: {TEMPERATURE_THRESHOLD}°C)"
                )

    @patch('app.notifications.Apprise')
    def test_notification_sending(self, mock_apprise):
        """Test the actual notification sending mechanism"""
        # Setup mock
        mock_instance = MagicMock()
        mock_apprise.return_value = mock_instance
        mock_instance.notify.return_value = True
        
        # Test successful notification
        result = _send_notification("Test Title", "Test Body")
        
        self.assertTrue(result)
        mock_instance.add.assert_called_once()
        mock_instance.notify.assert_called_once_with(
            title="Test Title",
            body="Test Body",
            body_format="text"
        )

    @patch('app.notifications.Apprise')
    def test_notification_failure(self, mock_apprise):
        """Test handling of notification sending failure"""
        # Setup mock to simulate failure
        mock_instance = MagicMock()
        mock_apprise.return_value = mock_instance
        mock_instance.notify.return_value = False
        
        # Test failed notification
        result = _send_notification("Test Title", "Test Body")
        
        self.assertFalse(result)
        mock_instance.notify.assert_called_once()

    @patch('app.notifications.Apprise')
    def test_send_alert_notification(self, mock_apprise):
        """Test sending an alert notification."""
        # Setup mock
        mock_instance = mock_apprise.return_value
        mock_instance.notify.return_value = True
        
        # Test alert notification
        success = send_temperature_alert(TEMPERATURE_THRESHOLD + 1)
        self.assertTrue(success)
        
        # Verify notification was sent with correct parameters
        mock_instance.add.assert_called_once()
        mock_instance.notify.assert_called_once()
        call_args = mock_instance.notify.call_args[1]
        self.assertEqual(call_args['title'], "Temperature Alert")
        self.assertIn(str(TEMPERATURE_THRESHOLD + 1), call_args['body'])
        
    @patch('app.notifications.Apprise')
    def test_send_normal_notification(self, mock_apprise):
        """Test sending a normal notification."""
        # Setup mock
        mock_instance = mock_apprise.return_value
        mock_instance.notify.return_value = True
        
        # Test normal notification
        success = send_temperature_alert(TEMPERATURE_THRESHOLD - 1, is_normal=True)
        self.assertTrue(success)
        
        # Verify notification was sent with correct parameters
        mock_instance.add.assert_called_once()
        mock_instance.notify.assert_called_once()
        call_args = mock_instance.notify.call_args[1]
        self.assertEqual(call_args['title'], "Temperature Normal")
        self.assertIn(str(TEMPERATURE_THRESHOLD - 1), call_args['body'])
        
    @patch('app.notifications.Apprise')
    def test_notification_exception(self, mock_apprise):
        """Test handling of notification exception."""
        # Setup mock to raise exception
        mock_instance = mock_apprise.return_value
        mock_instance.notify.side_effect = Exception("Network error")
        
        # Test exception handling
        success = send_temperature_alert(TEMPERATURE_THRESHOLD + 1)
        self.assertFalse(success)
        
    def test_missing_credentials(self):
        """Test handling of missing Pushover credentials."""
        with patch('app.notifications.PUSHOVER_USER_KEY', None), \
             patch('app.notifications.PUSHOVER_API_TOKEN', None):
            success = send_temperature_alert(TEMPERATURE_THRESHOLD + 1)
            self.assertFalse(success)

if __name__ == '__main__':
    unittest.main() 