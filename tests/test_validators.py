"""
Tests for validation utilities.
"""

import pytest
from src.validators import (
    ValidationError,
    validate_ticker,
    sanitize_ticker,
    validate_numeric_range,
    safe_divide,
    clamp,
)


class TestTickerValidation:
    """Tests for ticker validation."""

    def test_valid_tickers(self):
        """Test valid ticker formats."""
        valid_tickers = ["AAPL", "MSFT", "GOOGL", "BRK.B", "BABA", "TSM"]
        for ticker in valid_tickers:
            assert validate_ticker(ticker) is True

    def test_invalid_tickers(self):
        """Test invalid ticker formats."""
        invalid_tickers = [
            "",
            "   ",
            "TOOLONG",
            "123",
            "ABC@",
            "A.TOOLONG",
        ]
        for ticker in invalid_tickers:
            with pytest.raises(ValidationError):
                validate_ticker(ticker)

    def test_sanitize_ticker(self):
        """Test ticker sanitization."""
        assert sanitize_ticker("  aapl  ") == "AAPL"
        assert sanitize_ticker("msft") == "MSFT"
        assert sanitize_ticker("BRK.B") == "BRK.B"

    def test_sanitize_invalid_ticker(self):
        """Test sanitization of invalid ticker."""
        with pytest.raises(ValidationError):
            sanitize_ticker("INVALID@")


class TestNumericValidation:
    """Tests for numeric validation."""

    def test_validate_numeric_range_valid(self):
        """Test valid numeric ranges."""
        assert validate_numeric_range(5, "test", 0, 10) is True
        assert validate_numeric_range(0, "test", 0, 10) is True
        assert validate_numeric_range(10, "test", 0, 10) is True

    def test_validate_numeric_range_none(self):
        """Test None handling."""
        assert validate_numeric_range(None, "test", allow_none=True) is True

        with pytest.raises(ValidationError):
            validate_numeric_range(None, "test", allow_none=False)

    def test_validate_numeric_range_invalid(self):
        """Test invalid ranges."""
        with pytest.raises(ValidationError):
            validate_numeric_range(-1, "test", min_value=0)

        with pytest.raises(ValidationError):
            validate_numeric_range(11, "test", max_value=10)

    def test_safe_divide(self):
        """Test safe division."""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(10, 0) is None
        assert safe_divide(None, 2) is None
        assert safe_divide(10, None) is None

    def test_clamp(self):
        """Test value clamping."""
        assert clamp(5, 0, 10) == 5
        assert clamp(-1, 0, 10) == 0
        assert clamp(11, 0, 10) == 10
