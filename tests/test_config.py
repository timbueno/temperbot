import unittest
import os
from datetime import timedelta
from config import (
    DB_PATH,
    DATA_RETENTION_PERIOD,
    POLL_INTERVAL_MINUTES,
    TEMPERATURE_THRESHOLD,
    TEMPERATURE_NORMAL_MARGIN,
    TEMPERATURE_SOURCE,
    PUSHOVER_USER_KEY,
    PUSHOVER_API_TOKEN,
    NOTIFICATION_COOLDOWN
)

class TestConfig(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Store original environment variables
        self.original_env = {}
        for key in os.environ:
            self.original_env[key] = os.environ[key]
            
    def tearDown(self):
        """Restore original environment variables."""
        # Clear all environment variables
        for key in list(os.environ.keys()):
            del os.environ[key]
            
        # Restore original environment variables
        for key, value in self.original_env.items():
            os.environ[key] = value
            
    def test_default_values(self):
        """Test that default values are set correctly when no environment variables are present."""
        # Clear environment variables
        for key in list(os.environ.keys()):
            del os.environ[key]
            
        # Reload config
        import importlib
        import config
        importlib.reload(config)
        
        # Check default values
        self.assertEqual(config.DB_PATH, '/tmp/temperature.db')
        self.assertEqual(config.DATA_RETENTION_PERIOD, timedelta(days=14))
        self.assertEqual(config.POLL_INTERVAL_MINUTES, 1)
        self.assertEqual(config.TEMPERATURE_THRESHOLD, 23.5)
        self.assertEqual(config.TEMPERATURE_NORMAL_MARGIN, 1.0)
        self.assertEqual(config.TEMPERATURE_SOURCE, 'external')
        self.assertEqual(config.NOTIFICATION_COOLDOWN, timedelta(hours=1))
        
    def test_custom_db_path(self):
        """Test custom database path configuration."""
        test_path = '/custom/path/temperature.db'
        os.environ['DB_PATH'] = test_path
        
        # Reload config
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.DB_PATH, test_path)
        
    def test_data_retention_period(self):
        """Test data retention period configuration."""
        os.environ['DATA_RETENTION_DAYS'] = '30'
        
        # Reload config
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.DATA_RETENTION_PERIOD, timedelta(days=30))
        
    def test_poll_interval(self):
        """Test polling interval configuration."""
        os.environ['POLL_INTERVAL_MINUTES'] = '5'
        
        # Reload config
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.POLL_INTERVAL_MINUTES, 5)
        
    def test_temperature_threshold(self):
        """Test temperature threshold configuration."""
        os.environ['TEMPERATURE_THRESHOLD'] = '25.0'
        
        # Reload config
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.TEMPERATURE_THRESHOLD, 25.0)
        
    def test_temperature_normal_margin(self):
        """Test temperature normal margin configuration."""
        os.environ['TEMPERATURE_NORMAL_MARGIN'] = '2.0'
        
        # Reload config
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.TEMPERATURE_NORMAL_MARGIN, 2.0)
        
    def test_temperature_source(self):
        """Test temperature source configuration."""
        os.environ['TEMPERATURE_SOURCE'] = 'internal'
        
        # Reload config
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.TEMPERATURE_SOURCE, 'internal')
        
    def test_notification_cooldown(self):
        """Test notification cooldown configuration."""
        os.environ['NOTIFICATION_COOLDOWN_HOURS'] = '2'
        
        # Reload config
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.NOTIFICATION_COOLDOWN, timedelta(hours=2))
        
    def test_invalid_numeric_values(self):
        """Test handling of invalid numeric values."""
        # Test invalid POLL_INTERVAL_MINUTES
        os.environ['POLL_INTERVAL_MINUTES'] = 'invalid'
        
        # Reload config
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.POLL_INTERVAL_MINUTES, 1)  # Should use default
        
        # Test invalid TEMPERATURE_THRESHOLD
        os.environ['TEMPERATURE_THRESHOLD'] = 'invalid'
        
        # Reload config
        importlib.reload(config)
        
        self.assertEqual(config.TEMPERATURE_THRESHOLD, 23.5)  # Should use default
        
    def test_pushover_credentials(self):
        """Test Pushover credentials configuration."""
        test_user_key = 'test_user_key'
        test_api_token = 'test_api_token'
        
        os.environ['PUSHOVER_USER_KEY'] = test_user_key
        os.environ['PUSHOVER_API_TOKEN'] = test_api_token
        
        # Reload config
        import importlib
        import config
        importlib.reload(config)
        
        self.assertEqual(config.PUSHOVER_USER_KEY, test_user_key)
        self.assertEqual(config.PUSHOVER_API_TOKEN, test_api_token)

if __name__ == '__main__':
    unittest.main() 