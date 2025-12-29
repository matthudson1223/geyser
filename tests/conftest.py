"""
Pytest configuration and fixtures.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_ticker():
    """Sample ticker symbol."""
    return "NVDA"


@pytest.fixture
def sample_historical_data():
    """Sample historical price data."""
    dates = pd.date_range(end=datetime.now(), periods=252, freq="D")
    data = {
        "Open": np.random.uniform(100, 150, 252),
        "High": np.random.uniform(150, 200, 252),
        "Low": np.random.uniform(50, 100, 252),
        "Close": np.random.uniform(100, 150, 252),
        "Volume": np.random.randint(1000000, 10000000, 252),
    }
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def sample_company_overview():
    """Sample company overview data."""
    return {
        "ticker": "NVDA",
        "name": "NVIDIA Corporation",
        "sector": "Technology",
        "industry": "Semiconductors",
        "market_cap": 1000000000000,
        "current_price": 450.00,
        "description": "Leading GPU manufacturer",
    }


@pytest.fixture
def sample_financial_data():
    """Sample financial statement data."""
    columns = [
        datetime(2023, 12, 31),
        datetime(2022, 12, 31),
        datetime(2021, 12, 31),
    ]

    income_data = {
        "Total Revenue": [50000000000, 45000000000, 40000000000],
        "Gross Profit": [35000000000, 30000000000, 25000000000],
        "Operating Income": [20000000000, 18000000000, 15000000000],
        "Net Income": [15000000000, 13000000000, 11000000000],
    }

    balance_data = {
        "Total Assets": [80000000000, 70000000000, 60000000000],
        "Current Assets": [40000000000, 35000000000, 30000000000],
        "Total Liabilities Net Minority Interest": [30000000000, 28000000000, 25000000000],
        "Stockholders Equity": [50000000000, 42000000000, 35000000000],
    }

    cashflow_data = {
        "Operating Cash Flow": [18000000000, 16000000000, 14000000000],
        "Free Cash Flow": [15000000000, 13000000000, 11000000000],
    }

    return {
        "income_statement_annual": pd.DataFrame(income_data, index=columns).T,
        "balance_sheet_annual": pd.DataFrame(balance_data, index=columns).T,
        "cash_flow_annual": pd.DataFrame(cashflow_data, index=columns).T,
    }


@pytest.fixture
def mock_cache(tmp_path):
    """Mock cache manager for testing."""
    from src.cache_manager import CacheManager

    return CacheManager(cache_dir=str(tmp_path / ".cache"), enabled=True)
