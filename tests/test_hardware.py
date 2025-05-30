import unittest
from unittest.mock import patch, MagicMock
from app.hardware import read_temperature
from config import TEMPERATURE_SOURCE

class TestHardware(unittest.TestCase):
    @patch('app.hardware.Temper')
    def test_read_temperature_success(self, mock_temper):
        """Test successful temperature reading from configured source."""
        # Setup mock
        mock_instance = mock_temper.return_value
        mock_instance.read.return_value = [{
            f'{TEMPERATURE_SOURCE} temperature': 22.5
        }]
        
        # Test reading
        temp = read_temperature()
        self.assertEqual(temp, 22.5)
        
    @patch('app.hardware.Temper')
    def test_read_temperature_no_sensor(self, mock_temper):
        """Test behavior when no sensor is found."""
        # Setup mock to return empty results
        mock_instance = mock_temper.return_value
        mock_instance.read.return_value = []
        
        # Test reading
        temp = read_temperature()
        self.assertIsNone(temp)
        
    @patch('app.hardware.Temper')
    def test_read_temperature_error(self, mock_temper):
        """Test behavior when sensor returns an error."""
        # Setup mock to return error
        mock_instance = mock_temper.return_value
        mock_instance.read.return_value = [{
            'error': 'Sensor error'
        }]
        
        # Test reading
        temp = read_temperature()
        self.assertIsNone(temp)
        
    @patch('app.hardware.Temper')
    def test_read_temperature_missing_source(self, mock_temper):
        """Test behavior when configured temperature source is not available."""
        # Setup mock to return data without the configured source
        mock_instance = mock_temper.return_value
        mock_instance.read.return_value = [{
            'internal temperature': 22.5  # Different from configured source
        }]
        
        # Test reading
        temp = read_temperature()
        self.assertIsNone(temp)
        
    @patch('app.hardware.Temper')
    def test_read_temperature_exception(self, mock_temper):
        """Test behavior when an exception occurs during reading."""
        # Setup mock to raise an exception
        mock_instance = mock_temper.return_value
        mock_instance.read.side_effect = Exception("Hardware error")
        
        # Test reading
        temp = read_temperature()
        self.assertIsNone(temp)
        
    @patch('app.hardware.Temper')
    def test_read_temperature_multiple_sensors(self, mock_temper):
        """Test behavior when multiple sensors are present."""
        # Setup mock to return multiple sensors
        mock_instance = mock_temper.return_value
        mock_instance.read.return_value = [
            {
                f'{TEMPERATURE_SOURCE} temperature': 22.5
            },
            {
                f'{TEMPERATURE_SOURCE} temperature': 23.5
            }
        ]
        
        # Test reading - should get first sensor's reading
        temp = read_temperature()
        self.assertEqual(temp, 22.5)

if __name__ == '__main__':
    unittest.main() 