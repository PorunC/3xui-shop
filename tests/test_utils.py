"""
Tests for bot utility functions.
"""
import pytest
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import patch, AsyncMock
from aioresponses import aioresponses

from app.bot.utils.formatting import (
    format_size, format_remaining_time, format_device_count, 
    format_subscription_period, to_decimal
)
from app.bot.utils.validation import (
    is_valid_host, is_valid_client_count, is_valid_user_id, is_valid_message_text
)
from app.bot.utils.time import (
    get_current_timestamp, add_days_to_timestamp, days_to_timestamp
)
from app.bot.utils.network import (
    parse_redirect_url, ping_url, extract_base_url
)


class TestFormattingUtils:
    """Tests for formatting utility functions."""

    def test_format_size_unlimited(self):
        """Test formatting unlimited size."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x: x):
            result = format_size(-1)
            assert "∞" in result or "unlimited" in result.lower()

    def test_format_size_zero(self):
        """Test formatting zero size."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x: x):
            result = format_size(0)
            assert "0" in result
            assert "MB" in result

    def test_format_size_mb(self):
        """Test formatting size in MB."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x: x):
            result = format_size(1024 * 1024 * 100)  # 100 MB
            assert "100" in result
            assert "MB" in result

    def test_format_size_gb(self):
        """Test formatting size in GB."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x: x):
            result = format_size(1024 * 1024 * 1024 * 2)  # 2 GB
            assert "2" in result
            assert "GB" in result

    def test_format_size_error_handling(self):
        """Test format_size error handling."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x: x):
            # Test with invalid input type that might cause an error
            result = format_size("invalid")
            assert "0" in result
            assert "MB" in result

    def test_format_remaining_time_unlimited(self):
        """Test formatting unlimited remaining time."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x: x):
            result = format_remaining_time(-1)
            assert "∞" in result or "unlimited" in result.lower()

    def test_format_remaining_time_days(self):
        """Test formatting remaining time in days."""
        # Create timestamp for 2 days from now
        future_time = datetime.now(timezone.utc) + timedelta(days=2, hours=1)
        timestamp = int(future_time.timestamp() * 1000)
        
        with patch('app.bot.utils.formatting._', side_effect=lambda x: x):
            result = format_remaining_time(timestamp)
            assert "2d" in result
            assert "1h" in result

    def test_format_remaining_time_zero(self):
        """Test formatting zero remaining time."""
        # Create timestamp for current time
        timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        with patch('app.bot.utils.formatting._', side_effect=lambda x: x):
            result = format_remaining_time(timestamp)
            assert "m" in result  # Should show minutes

    def test_format_device_count_unlimited(self):
        """Test formatting unlimited device count."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x: x):
            result = format_device_count(-1)
            assert "∞" in result or "unlimited" in result.lower()
            assert "devices" in result

    def test_format_device_count_single(self):
        """Test formatting single device."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x, *args: f"1 device" if x == "1 device" else x):
            result = format_device_count(1)
            assert "1 device" in result

    def test_format_device_count_multiple(self):
        """Test formatting multiple devices."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x, y, count: f"{count} devices"):
            result = format_device_count(5)
            assert "5 devices" in result

    def test_format_subscription_period_unlimited(self):
        """Test formatting unlimited subscription period."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x: x):
            result = format_subscription_period(-1)
            assert "∞" in result or "unlimited" in result.lower()

    def test_format_subscription_period_years(self):
        """Test formatting subscription period in years."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x, y, count: f"{count} years"):
            result = format_subscription_period(730)  # 2 years
            assert "2 years" in result

    def test_format_subscription_period_months(self):
        """Test formatting subscription period in months."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x, y, count: f"{count} months"):
            result = format_subscription_period(90)  # 3 months
            assert "3 months" in result

    def test_format_subscription_period_days(self):
        """Test formatting subscription period in days."""
        with patch('app.bot.utils.formatting._', side_effect=lambda x, y, count: f"{count} days"):
            result = format_subscription_period(15)  # 15 days
            assert "15 days" in result

    def test_to_decimal_float(self):
        """Test converting float to decimal."""
        result = to_decimal(25.99)
        assert isinstance(result, Decimal)
        assert result == Decimal('25.99')

    def test_to_decimal_string(self):
        """Test converting string to decimal."""
        result = to_decimal("100.50")
        assert isinstance(result, Decimal)
        assert result == Decimal('100.50')

    def test_to_decimal_existing_decimal(self):
        """Test converting existing decimal."""
        original = Decimal('50.25')
        result = to_decimal(original)
        assert isinstance(result, Decimal)
        assert result == original

    def test_to_decimal_int(self):
        """Test converting integer to decimal."""
        result = to_decimal(75)
        assert isinstance(result, Decimal)
        assert result == Decimal('75')


class TestValidationUtils:
    """Tests for validation utility functions."""

    def test_is_valid_host_url(self):
        """Test validating URLs."""
        assert is_valid_host("https://example.com") is True
        assert is_valid_host("http://test.example.org") is True
        assert is_valid_host("https://sub.domain.com:8080") is True

    def test_is_valid_host_ip(self):
        """Test validating IP addresses."""
        assert is_valid_host("192.168.1.1") is True
        assert is_valid_host("127.0.0.1") is True
        assert is_valid_host("10.0.0.1") is True

    def test_is_valid_host_invalid(self):
        """Test invalid hosts."""
        assert is_valid_host("invalid") is False
        assert is_valid_host("256.256.256.256") is False
        assert is_valid_host("") is False
        assert is_valid_host("not-a-url") is False

    def test_is_valid_client_count_valid(self):
        """Test valid client counts."""
        assert is_valid_client_count("1") is True
        assert is_valid_client_count("100") is True
        assert is_valid_client_count("9999") is True
        assert is_valid_client_count("10000") is True

    def test_is_valid_client_count_invalid(self):
        """Test invalid client counts."""
        assert is_valid_client_count("0") is False
        assert is_valid_client_count("10001") is False
        assert is_valid_client_count("-1") is False
        assert is_valid_client_count("abc") is False
        assert is_valid_client_count("") is False

    def test_is_valid_user_id_valid(self):
        """Test valid user IDs."""
        assert is_valid_user_id("1") is True
        assert is_valid_user_id("123456789") is True
        assert is_valid_user_id("1000000000000") is True

    def test_is_valid_user_id_invalid(self):
        """Test invalid user IDs."""
        assert is_valid_user_id("0") is False
        assert is_valid_user_id("1000000000001") is False
        assert is_valid_user_id("-1") is False
        assert is_valid_user_id("abc") is False
        assert is_valid_user_id("") is False

    def test_is_valid_message_text_valid(self):
        """Test valid message text."""
        assert is_valid_message_text("Hello") is True
        assert is_valid_message_text("A" * 4096) is True
        assert is_valid_message_text("") is True

    def test_is_valid_message_text_invalid(self):
        """Test invalid message text."""
        assert is_valid_message_text("A" * 4097) is False


class TestTimeUtils:
    """Tests for time utility functions."""

    def test_get_current_timestamp(self):
        """Test getting current timestamp."""
        timestamp = get_current_timestamp()
        assert isinstance(timestamp, int)
        assert timestamp > 0
        
        # Should be reasonably close to current time
        current_time = int(datetime.now(timezone.utc).timestamp() * 1000)
        assert abs(timestamp - current_time) < 1000  # Within 1 second

    def test_add_days_to_timestamp(self):
        """Test adding days to timestamp."""
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        base_timestamp = int(base_time.timestamp() * 1000)
        
        # Add 7 days
        result = add_days_to_timestamp(base_timestamp, 7)
        expected_time = base_time + timedelta(days=7)
        expected_timestamp = int(expected_time.timestamp() * 1000)
        
        assert result == expected_timestamp

    def test_add_negative_days_to_timestamp(self):
        """Test adding negative days to timestamp."""
        base_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        base_timestamp = int(base_time.timestamp() * 1000)
        
        # Subtract 5 days
        result = add_days_to_timestamp(base_timestamp, -5)
        expected_time = base_time - timedelta(days=5)
        expected_timestamp = int(expected_time.timestamp() * 1000)
        
        assert result == expected_timestamp

    def test_days_to_timestamp(self):
        """Test converting days to timestamp."""
        result = days_to_timestamp(30)
        
        # Should be 30 days from now
        expected_time = datetime.now(timezone.utc) + timedelta(days=30)
        expected_timestamp = int(expected_time.timestamp() * 1000)
        
        # Allow for small timing differences
        assert abs(result - expected_timestamp) < 1000  # Within 1 second


class TestNetworkUtils:
    """Tests for network utility functions."""

    def test_parse_redirect_url(self):
        """Test parsing redirect URL query string."""
        query = "param1=value1&param2=value2&param3=value3&empty="
        result = parse_redirect_url(query)
        
        assert result == {
            "param1": "value1",
            "param2": "value2", 
            "param3": "value3"
        }
        # Empty parameter should be excluded
        assert "empty" not in result

    def test_parse_redirect_url_empty(self):
        """Test parsing empty query string."""
        result = parse_redirect_url("")
        assert result == {}

    def test_parse_redirect_url_duplicates(self):
        """Test parsing query string with duplicate keys."""
        query = "key=value1&key=value2"
        result = parse_redirect_url(query)
        # Should take the first value
        assert result == {"key": "value1"}

    async def test_ping_url_success(self):
        """Test successful URL ping."""
        url = "https://httpbin.org/status/200"
        
        with aioresponses() as m:
            m.get(url, status=200)
            result = await ping_url(url)
            
            assert result is not None
            assert isinstance(result, float)
            assert result >= 0

    async def test_ping_url_failure(self):
        """Test failed URL ping."""
        url = "https://httpbin.org/status/500"
        
        with aioresponses() as m:
            m.get(url, status=500)
            result = await ping_url(url)
            
            assert result is None

    async def test_ping_url_exception(self):
        """Test URL ping with exception."""
        url = "https://invalid-url-that-does-not-exist.com"
        
        with aioresponses() as m:
            m.get(url, exception=Exception("Connection error"))
            result = await ping_url(url)
            
            assert result is None

    def test_extract_base_url(self):
        """Test extracting base URL."""
        url = "https://example.com:443/some/path"
        port = 8080
        path = "/api/v1"
        
        result = extract_base_url(url, port, path)
        assert result == "https://example.com:8080/api/v1"

    def test_extract_base_url_with_ip(self):
        """Test extracting base URL with IP address."""
        url = "http://192.168.1.100:80/"
        port = 3000
        path = "/health"
        
        result = extract_base_url(url, port, path)
        assert result == "http://192.168.1.100:3000/health"

    def test_extract_base_url_complex_path(self):
        """Test extracting base URL with complex path."""
        url = "https://api.example.com/v1/users"
        port = 443
        path = "/status/check"
        
        result = extract_base_url(url, port, path)
        assert result == "https://api.example.com:443/status/check"


class TestUtilsIntegration:
    """Integration tests for utility functions working together."""

    def test_time_and_formatting_integration(self):
        """Test time utilities working with formatting utilities."""
        # Create a timestamp for 2 days from now
        future_timestamp = days_to_timestamp(2)
        
        # Format the remaining time
        with patch('app.bot.utils.formatting._', side_effect=lambda x: x):
            formatted = format_remaining_time(future_timestamp)
            assert "d" in formatted or "h" in formatted or "m" in formatted

    def test_validation_and_network_integration(self):
        """Test validation working with network utilities."""
        valid_url = "https://example.com"
        invalid_url = "not-a-url"
        
        assert is_valid_host(valid_url) is True
        assert is_valid_host(invalid_url) is False
        
        # Extract base URL from valid URL
        result = extract_base_url(valid_url, 8080, "/api")
        assert "example.com:8080/api" in result

    def test_decimal_formatting_precision(self):
        """Test decimal formatting maintains precision."""
        values = [25.99, 100.001, 0.12345678901234567890]
        
        for value in values:
            decimal_value = to_decimal(value)
            assert isinstance(decimal_value, Decimal)
            # Should maintain reasonable precision
            assert len(str(decimal_value).split('.')[-1]) <= 18

    async def test_network_timeout_handling(self):
        """Test network utilities handle timeouts properly."""
        url = "https://httpbin.org/delay/10"  # Simulates slow response
        
        with aioresponses() as m:
            m.get(url, exception=Exception("Timeout"))
            result = await ping_url(url, timeout=1)  # Very short timeout
            
            assert result is None