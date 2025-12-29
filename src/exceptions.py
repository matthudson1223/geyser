"""
Custom exceptions for Equity Research Report Generator.
"""


class GeyserException(Exception):
    """Base exception for Geyser application."""

    pass


class DataCollectionError(GeyserException):
    """Exception raised when data collection fails."""

    pass


class AnalysisError(GeyserException):
    """Exception raised during financial analysis."""

    pass


class ReportGenerationError(GeyserException):
    """Exception raised during report generation."""

    pass


class CacheError(GeyserException):
    """Exception raised for cache-related errors."""

    pass


class ConfigurationError(GeyserException):
    """Exception raised for configuration errors."""

    pass
