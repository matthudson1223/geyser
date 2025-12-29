"""
Configuration module for Equity Research Report Generator.

Change the TICKER variable to analyze any publicly traded stock.
"""

# =============================================================================
# MAIN CONFIGURATION - CHANGE THIS TO ANALYZE A DIFFERENT STOCK
# =============================================================================

TICKER = "NVDA"  # Change this to any valid stock ticker (e.g., "AAPL", "MSFT", "GOOGL")

# =============================================================================
# ANALYSIS PARAMETERS
# =============================================================================

# Historical data settings
YEARS_OF_HISTORY = 5  # Years of historical price data to fetch
YEARS_OF_FINANCIALS = 4  # Years of financial statements to analyze

# Chart settings
CHART_PRICE_YEARS = 2  # Years of price data for the main chart
MA_SHORT = 50  # Short-term moving average period
MA_LONG = 200  # Long-term moving average period

# Output settings
OUTPUT_DIR = "output"
CHARTS_DIR = "output/charts"

# =============================================================================
# PEER MAPPING - Industry-specific competitor lists
# =============================================================================

# Mapping of tickers to their peer group
# Add custom peer groups as needed
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

# Default peer list for tickers not in the mapping
DEFAULT_PEERS = ["SPY"]  # Will be dynamically populated based on sector

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

# Score thresholds for recommendations
RECOMMENDATION_THRESHOLDS = {
    "strong_buy": 8.0,
    "buy": 6.5,
    "hold": 5.0,
    "sell": 3.5,
    # Below 3.5 = Strong Sell
}

# =============================================================================
# SECTOR ETF MAPPING - For sector comparison
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
