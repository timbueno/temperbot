import unittest
from unittest.mock import patch, MagicMock
from app.hardware import read_temperature, apply_temperature_calibration
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


class TestTemperatureCalibration(unittest.TestCase):
    def test_no_calibration_data(self):
        """Test that with no calibration data, raw temperature is returned unchanged."""
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', []):
            result = apply_temperature_calibration(25.0)
            self.assertEqual(result, 25.0)
    
    def test_empty_calibration_data(self):
        """Test that with empty calibration data, raw temperature is returned unchanged."""
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', None):
            result = apply_temperature_calibration(25.0)
            self.assertEqual(result, 25.0)
    
    def test_single_point_calibration(self):
        """Test calibration with a single point (simple offset)."""
        # Device reads 20°C when actual is 25°C (offset of +5°C)
        calibration_data = [{"temp": 20, "actual": 25}]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', calibration_data):
            # Test exact point
            self.assertEqual(apply_temperature_calibration(20.0), 25.0)
            
            # Test offset applied to other temperatures
            self.assertEqual(apply_temperature_calibration(15.0), 20.0)  # 15 + 5 = 20
            self.assertEqual(apply_temperature_calibration(30.0), 35.0)  # 30 + 5 = 35
            self.assertEqual(apply_temperature_calibration(0.0), 5.0)    # 0 + 5 = 5
    
    def test_two_point_calibration(self):
        """Test calibration with two points (linear interpolation)."""
        # Device reads 5°C when actual is 0°C, device reads 25°C when actual is 20°C
        calibration_data = [
            {"temp": 5, "actual": 0},
            {"temp": 25, "actual": 20}
        ]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', calibration_data):
            # Test exact points
            self.assertEqual(apply_temperature_calibration(5.0), 0.0)
            self.assertEqual(apply_temperature_calibration(25.0), 20.0)
            
            # Test interpolation (halfway between points)
            # Device temp 15°C should be actual temp 10°C
            result = apply_temperature_calibration(15.0)
            self.assertAlmostEqual(result, 10.0, places=5)
            
            # Test interpolation at 1/4 point
            # Device temp 10°C should be actual temp 5°C
            result = apply_temperature_calibration(10.0)
            self.assertAlmostEqual(result, 5.0, places=5)
    
    def test_two_point_extrapolation_below(self):
        """Test extrapolation below the calibration range."""
        calibration_data = [
            {"temp": 5, "actual": 0},
            {"temp": 25, "actual": 20}
        ]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', calibration_data):
            # Test extrapolation below range
            # Device temp 0°C should extrapolate to actual temp -5°C
            result = apply_temperature_calibration(0.0)
            self.assertAlmostEqual(result, -5.0, places=5)
    
    def test_two_point_extrapolation_above(self):
        """Test extrapolation above the calibration range."""
        calibration_data = [
            {"temp": 5, "actual": 0},
            {"temp": 25, "actual": 20}
        ]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', calibration_data):
            # Test extrapolation above range
            # Device temp 30°C should extrapolate to actual temp 25°C
            result = apply_temperature_calibration(30.0)
            self.assertAlmostEqual(result, 25.0, places=5)
    
    def test_multiple_point_calibration(self):
        """Test calibration with multiple points."""
        # More complex calibration curve
        calibration_data = [
            {"temp": 0, "actual": -2},
            {"temp": 10, "actual": 8},
            {"temp": 20, "actual": 18},
            {"temp": 30, "actual": 28}
        ]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', calibration_data):
            # Test exact points
            self.assertEqual(apply_temperature_calibration(0.0), -2.0)
            self.assertEqual(apply_temperature_calibration(10.0), 8.0)
            self.assertEqual(apply_temperature_calibration(20.0), 18.0)
            self.assertEqual(apply_temperature_calibration(30.0), 28.0)
            
            # Test interpolation between 10°C and 20°C
            # Device temp 15°C should be actual temp 13°C
            result = apply_temperature_calibration(15.0)
            self.assertAlmostEqual(result, 13.0, places=5)
            
            # Test interpolation between 0°C and 10°C
            # Device temp 5°C should be actual temp 3°C
            result = apply_temperature_calibration(5.0)
            self.assertAlmostEqual(result, 3.0, places=5)
    
    def test_unsorted_calibration_data(self):
        """Test that calibration data is automatically sorted by device temperature."""
        # Provide calibration data in unsorted order
        calibration_data = [
            {"temp": 25, "actual": 20},
            {"temp": 5, "actual": 0},
            {"temp": 15, "actual": 10}
        ]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', calibration_data):
            # Should still work correctly due to internal sorting
            self.assertEqual(apply_temperature_calibration(5.0), 0.0)
            self.assertEqual(apply_temperature_calibration(25.0), 20.0)
            result = apply_temperature_calibration(15.0)
            self.assertAlmostEqual(result, 10.0, places=5)
    
    def test_duplicate_temperature_points(self):
        """Test behavior with duplicate device temperature points."""
        calibration_data = [
            {"temp": 20, "actual": 18},
            {"temp": 20, "actual": 18}  # Duplicate point
        ]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', calibration_data):
            # Should handle duplicate points gracefully
            result = apply_temperature_calibration(20.0)
            self.assertEqual(result, 18.0)
    
    def test_negative_temperatures(self):
        """Test calibration with negative temperatures."""
        calibration_data = [
            {"temp": -10, "actual": -15},
            {"temp": 10, "actual": 5}
        ]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', calibration_data):
            # Test exact points
            self.assertEqual(apply_temperature_calibration(-10.0), -15.0)
            self.assertEqual(apply_temperature_calibration(10.0), 5.0)
            
            # Test interpolation at 0°C
            # Should be -5°C actual
            result = apply_temperature_calibration(0.0)
            self.assertAlmostEqual(result, -5.0, places=5)


class TestTemperatureCalibrationIntegration(unittest.TestCase):
    """Integration tests for calibration with the full read_temperature function."""
    
    @patch('app.hardware.Temper')
    def test_read_temperature_with_calibration(self, mock_temper):
        """Test that read_temperature applies calibration to sensor readings."""
        # Setup mock to return raw temperature
        mock_instance = mock_temper.return_value
        mock_instance.read.return_value = [{
            f'{TEMPERATURE_SOURCE} temperature': 25.0
        }]
        
        # Setup calibration that subtracts 5°C (device reads high)
        calibration_data = [{"temp": 25, "actual": 20}]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', calibration_data):
            temp = read_temperature()
            self.assertEqual(temp, 20.0)  # Should be calibrated value
    
    @patch('app.hardware.Temper')
    def test_read_temperature_with_complex_calibration(self, mock_temper):
        """Test read_temperature with multi-point calibration."""
        # Setup mock to return raw temperature
        mock_instance = mock_temper.return_value
        mock_instance.read.return_value = [{
            f'{TEMPERATURE_SOURCE} temperature': 15.0
        }]
        
        # Setup two-point calibration
        calibration_data = [
            {"temp": 10, "actual": 8},
            {"temp": 20, "actual": 18}
        ]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', calibration_data):
            temp = read_temperature()
            # 15°C device reading should interpolate to 13°C actual
            self.assertAlmostEqual(temp, 13.0, places=5)
    
    @patch('app.hardware.Temper')
    def test_read_temperature_calibration_with_sensor_error(self, mock_temper):
        """Test that sensor errors are handled before calibration is applied."""
        # Setup mock to return error
        mock_instance = mock_temper.return_value
        mock_instance.read.return_value = [{
            'error': 'Sensor error'
        }]
        
        calibration_data = [{"temp": 25, "actual": 20}]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', calibration_data):
            temp = read_temperature()
            self.assertIsNone(temp)  # Should return None due to sensor error
    
    @patch('app.hardware.Temper')
    def test_read_temperature_no_calibration_integration(self, mock_temper):
        """Test that read_temperature works normally with no calibration data."""
        # Setup mock to return raw temperature
        mock_instance = mock_temper.return_value
        mock_instance.read.return_value = [{
            f'{TEMPERATURE_SOURCE} temperature': 25.0
        }]
        
        with patch('app.hardware.TEMPERATURE_CALIBRATION_DATA', []):
            temp = read_temperature()
            self.assertEqual(temp, 25.0)  # Should be uncalibrated value


if __name__ == '__main__':
    unittest.main() 