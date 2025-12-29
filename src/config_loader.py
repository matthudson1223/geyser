"""
Configuration Loader for Equity Research Report Generator.

Supports loading configuration from:
1. Environment variables (.env file)
2. YAML configuration files
3. Default values
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def str_to_bool(value: str) -> bool:
    """Convert string to boolean."""
    return value.lower() in ("true", "1", "yes", "on")


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to YAML config file (optional)
        """
        self.config_data: Dict[str, Any] = {}

        # Load from YAML if provided
        if config_file and os.path.exists(config_file):
            self._load_yaml(config_file)

    def _load_yaml(self, config_file: str) -> None:
        """Load configuration from YAML file."""
        with open(config_file, "r", encoding="utf-8") as f:
            self.config_data = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None, env_var: Optional[str] = None) -> Any:
        """
        Get configuration value with fallback chain: ENV -> YAML -> default.

        Args:
            key: Configuration key
            default: Default value if not found
            env_var: Environment variable name (if different from key)

        Returns:
            Configuration value
        """
        # Try environment variable first
        env_key = env_var or key.upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            # Convert to appropriate type based on default
            if isinstance(default, bool):
                return str_to_bool(env_value)
            elif isinstance(default, int):
                return int(env_value)
            elif isinstance(default, float):
                return float(env_value)
            return env_value

        # Try YAML config
        if key in self.config_data:
            return self.config_data[key]

        # Return default
        return default


# Global configuration instance
_config = Config()


def load_config(config_file: Optional[str] = None) -> Config:
    """
    Load or reload configuration.

    Args:
        config_file: Path to YAML config file (optional)

    Returns:
        Config instance
    """
    global _config
    _config = Config(config_file)
    return _config


def get_config() -> Config:
    """Get the global configuration instance."""
    return _config


# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================

# Default ticker
TICKER = _config.get("default_ticker", "NVDA", "DEFAULT_TICKER")

# Historical data settings
YEARS_OF_HISTORY = _config.get("years_of_history", 5, "YEARS_OF_HISTORY")
YEARS_OF_FINANCIALS = _config.get("years_of_financials", 4, "YEARS_OF_FINANCIALS")

# Chart settings
CHART_PRICE_YEARS = _config.get("chart_price_years", 2, "CHART_PRICE_YEARS")
MA_SHORT = _config.get("ma_short", 50, "MA_SHORT")
MA_LONG = _config.get("ma_long", 200, "MA_LONG")

# Output settings
OUTPUT_DIR = _config.get("output_dir", "output", "OUTPUT_DIR")
CHARTS_DIR = _config.get("charts_dir", "output/charts", "CHARTS_DIR")

# Caching settings
CACHE_ENABLED = _config.get("cache_enabled", True, "CACHE_ENABLED")
CACHE_DIR = _config.get("cache_dir", ".cache", "CACHE_DIR")
CACHE_TTL_HOURS = _config.get("cache_ttl_hours", 24, "CACHE_TTL_HOURS")
CACHE_PRICE_TTL_HOURS = _config.get("cache_price_ttl_hours", 1, "CACHE_PRICE_TTL_HOURS")

# Logging settings
LOG_LEVEL = _config.get("log_level", "INFO", "LOG_LEVEL")
LOG_FILE = _config.get("log_file", "output/analysis.log", "LOG_FILE")
LOG_TO_CONSOLE = _config.get("log_to_console", True, "LOG_TO_CONSOLE")

# Performance settings
PARALLEL_PEER_FETCH = _config.get("parallel_peer_fetch", True, "PARALLEL_PEER_FETCH")
MAX_WORKERS = _config.get("max_workers", 5, "MAX_WORKERS")

# =============================================================================
# PEER MAPPING - Industry-specific competitor lists
# =============================================================================

PEER_MAPPING = {
    # Technology - Semiconductors
    "NVDA": ["AMD", "INTC", "QCOM", "AVGO", "TXN"],
    "AMD": ["NVDA", "INTC", "QCOM", "AVGO", "TXN"],
    "INTC": ["NVDA", "AMD", "QCOM", "AVGO", "TXN"],
    # Technology - Software
    "MSFT": ["AAPL", "GOOGL", "ORCL", "CRM", "ADBE"],
    "ORCL": ["MSFT", "CRM", "SAP", "IBM", "ADBE"],
    "CRM": ["MSFT", "ORCL", "SAP", "WDAY", "NOW"],
    "ADBE": ["MSFT", "CRM", "ORCL", "INTU", "ANSS"],
    # Technology - Big Tech / Consumer Electronics
    "AAPL": ["MSFT", "GOOGL", "AMZN", "META", "SAMSUNG.KS"],
    "GOOGL": ["AAPL", "MSFT", "META", "AMZN", "NFLX"],
    "GOOG": ["AAPL", "MSFT", "META", "AMZN", "NFLX"],
    "META": ["GOOGL", "SNAP", "PINS", "TWTR", "NFLX"],
    "AMZN": ["AAPL", "MSFT", "GOOGL", "WMT", "BABA"],
    # Financials - Banks
    "JPM": ["BAC", "WFC", "C", "GS", "MS"],
    "BAC": ["JPM", "WFC", "C", "GS", "USB"],
    "WFC": ["JPM", "BAC", "C", "USB", "PNC"],
    "GS": ["JPM", "MS", "C", "BAC", "SCHW"],
    "MS": ["GS", "JPM", "C", "BAC", "SCHW"],
    # Healthcare - Pharma
    "JNJ": ["PFE", "MRK", "ABBV", "LLY", "BMY"],
    "PFE": ["JNJ", "MRK", "ABBV", "LLY", "BMY"],
    "MRK": ["JNJ", "PFE", "ABBV", "LLY", "BMY"],
    "LLY": ["JNJ", "PFE", "MRK", "ABBV", "NVO"],
    "ABBV": ["JNJ", "PFE", "MRK", "LLY", "BMY"],
    # Consumer - Retail
    "WMT": ["COST", "TGT", "AMZN", "HD", "LOW"],
    "COST": ["WMT", "TGT", "BJ", "KR", "AMZN"],
    "TGT": ["WMT", "COST", "KR", "DG", "DLTR"],
    "HD": ["LOW", "WMT", "COST", "TGT", "TSCO"],
    "LOW": ["HD", "WMT", "COST", "TGT", "TSCO"],
    # Energy
    "XOM": ["CVX", "COP", "EOG", "SLB", "OXY"],
    "CVX": ["XOM", "COP", "EOG", "SLB", "OXY"],
    # Automotive
    "TSLA": ["F", "GM", "TM", "RIVN", "NIO"],
    "F": ["GM", "TSLA", "TM", "HMC", "STLA"],
    "GM": ["F", "TSLA", "TM", "HMC", "STLA"],
    # Streaming/Entertainment
    "NFLX": ["DIS", "WBD", "PARA", "CMCSA", "ROKU"],
    "DIS": ["NFLX", "WBD", "PARA", "CMCSA", "ROKU"],
}

DEFAULT_PEERS = ["SPY"]

# =============================================================================
# SCORING WEIGHTS
# =============================================================================

SCORE_WEIGHTS = {
    "valuation": 0.25,
    "growth": 0.20,
    "profitability": 0.20,
    "financial_health": 0.15,
    "momentum_sentiment": 0.10,
    "quality_moat": 0.10,
}

RECOMMENDATION_THRESHOLDS = {
    "strong_buy": 8.0,
    "buy": 6.5,
    "hold": 5.0,
    "sell": 3.5,
}

# =============================================================================
# SECTOR ETF MAPPING
# =============================================================================

SECTOR_ETFS = {
    "Technology": "XLK",
    "Financial Services": "XLF",
    "Healthcare": "XLV",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Energy": "XLE",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Communication Services": "XLC",
}


def get_peers(ticker: str) -> list:
    """Get peer companies for a given ticker."""
    return PEER_MAPPING.get(ticker.upper(), DEFAULT_PEERS)


def get_sector_etf(sector: str) -> str:
    """Get the sector ETF for a given sector."""
    return SECTOR_ETFS.get(sector, "SPY")
