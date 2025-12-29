"""
Validation utilities for Equity Research Report Generator.

Provides input validation and sanitization functions.
"""

import re
from typing import Any, Dict, List, Optional

from .logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_ticker(ticker: str) -> bool:
    """
    Validate stock ticker format.

    Args:
        ticker: Stock ticker symbol

    Returns:
        True if valid, False otherwise

    Raises:
        ValidationError: If ticker format is invalid
    """
    if not ticker or not isinstance(ticker, str):
        raise ValidationError("Ticker must be a non-empty string")

    ticker = ticker.strip().upper()

    # Basic ticker format: 1-5 letters, optionally followed by .XX for exchange
    pattern = r"^[A-Z]{1,5}(\.[A-Z]{1,3})?$"

    if not re.match(pattern, ticker):
        raise ValidationError(
            f"Invalid ticker format: {ticker}. "
            "Expected format: 1-5 letters, optionally followed by .XX for exchange"
        )

    return True


def sanitize_ticker(ticker: str) -> str:
    """
    Sanitize and normalize ticker symbol.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Sanitized ticker symbol

    Raises:
        ValidationError: If ticker is invalid
    """
    if not ticker or not isinstance(ticker, str):
        raise ValidationError("Ticker must be a non-empty string")

    # Strip whitespace and convert to uppercase
    ticker = ticker.strip().upper()

    # Validate format
    validate_ticker(ticker)

    return ticker


def validate_financial_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate financial data completeness and reasonableness.

    Args:
        data: Financial data dictionary

    Returns:
        List of warning messages
    """
    warnings = []

    # Check market cap
    market_cap = data.get("overview", {}).get("market_cap")
    if market_cap is not None and market_cap <= 0:
        warnings.append("Invalid or missing market cap")

    # Check current price
    current_price = data.get("overview", {}).get("current_price")
    if current_price is not None and current_price <= 0:
        warnings.append("Invalid or missing current price")

    # Check for empty dataframes
    if data.get("income_statement_annual") is not None:
        if data["income_statement_annual"].empty:
            warnings.append("Empty income statement data")

    if data.get("balance_sheet_annual") is not None:
        if data["balance_sheet_annual"].empty:
            warnings.append("Empty balance sheet data")

    if data.get("cash_flow_annual") is not None:
        if data["cash_flow_annual"].empty:
            warnings.append("Empty cash flow data")

    # Check historical prices
    if data.get("historical_prices") is not None:
        if data["historical_prices"].empty:
            warnings.append("No historical price data available")
        elif len(data["historical_prices"]) < 30:
            warnings.append("Limited historical price data (< 30 days)")

    return warnings


def validate_numeric_range(
    value: Optional[float],
    name: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_none: bool = True,
) -> bool:
    """
    Validate numeric value is within expected range.

    Args:
        value: Value to validate
        name: Name of the value (for error messages)
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        allow_none: Whether None is acceptable

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    if value is None:
        if allow_none:
            return True
        else:
            raise ValidationError(f"{name} cannot be None")

    if not isinstance(value, (int, float)):
        raise ValidationError(f"{name} must be a number, got {type(value)}")

    if min_value is not None and value < min_value:
        raise ValidationError(f"{name} must be >= {min_value}, got {value}")

    if max_value is not None and value > max_value:
        raise ValidationError(f"{name} must be <= {max_value}, got {value}")

    return True


def validate_dataframe_not_empty(df: Any, name: str = "DataFrame") -> bool:
    """
    Validate that a DataFrame is not None and not empty.

    Args:
        df: DataFrame to validate
        name: Name for error messages

    Returns:
        True if valid

    Raises:
        ValidationError: If validation fails
    """
    if df is None:
        raise ValidationError(f"{name} is None")

    try:
        if df.empty:
            raise ValidationError(f"{name} is empty")
    except AttributeError:
        raise ValidationError(f"{name} is not a DataFrame")

    return True


def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    """
    Safely divide two numbers, handling None and zero division.

    Args:
        numerator: Numerator value
        denominator: Denominator value

    Returns:
        Result of division or None if invalid
    """
    if numerator is None or denominator is None:
        return None

    if denominator == 0:
        logger.debug(f"Division by zero attempted: {numerator} / {denominator}")
        return None

    try:
        return float(numerator) / float(denominator)
    except (TypeError, ValueError) as e:
        logger.warning(f"Error in division: {e}")
        return None


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value between min and max.

    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value

    Returns:
        Clamped value
    """
    return max(min_value, min(max_value, value))
