"""
Data Collection Module for Equity Research Report Generator.

This module handles all data fetching from yfinance including:
- Company profile and overview
- Historical price data
- Financial statements
- Key statistics and ratios
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import warnings

warnings.filterwarnings('ignore')


class DataCollector:
    """Collects financial data for equity research analysis."""

    def __init__(self, ticker: str):
        """
        Initialize DataCollector with a stock ticker.

        Args:
            ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL')
        """
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
        self._info = None
        self._history = None
        self._financials = None

    @property
    def info(self) -> Dict[str, Any]:
        """Get cached company info."""
        if self._info is None:
            self._info = self.stock.info
        return self._info

    def get_company_overview(self) -> Dict[str, Any]:
        """
        Get company profile and overview information.

        Returns:
            Dictionary containing company overview data
        """
        info = self.info

        overview = {
            "ticker": self.ticker,
            "name": info.get("longName", info.get("shortName", self.ticker)),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "country": info.get("country", "N/A"),
            "website": info.get("website", "N/A"),
            "employees": info.get("fullTimeEmployees", "N/A"),
            "description": info.get("longBusinessSummary", "N/A"),

            # Market data
            "market_cap": info.get("marketCap", None),
            "enterprise_value": info.get("enterpriseValue", None),
            "shares_outstanding": info.get("sharesOutstanding", None),
            "float_shares": info.get("floatShares", None),
            "shares_short": info.get("sharesShort", None),
            "short_ratio": info.get("shortRatio", None),
            "short_percent_of_float": info.get("shortPercentOfFloat", None),

            # Price data
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", None)),
            "previous_close": info.get("previousClose", None),
            "open": info.get("open", None),
            "day_low": info.get("dayLow", None),
            "day_high": info.get("dayHigh", None),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", None),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", None),
            "fifty_day_avg": info.get("fiftyDayAverage", None),
            "two_hundred_day_avg": info.get("twoHundredDayAverage", None),
            "avg_volume": info.get("averageVolume", None),
            "avg_volume_10d": info.get("averageVolume10days", None),

            # Dividends
            "dividend_rate": info.get("dividendRate", None),
            "dividend_yield": info.get("dividendYield", None),
            "ex_dividend_date": info.get("exDividendDate", None),
            "payout_ratio": info.get("payoutRatio", None),

            # Key executives (if available)
            "executives": info.get("companyOfficers", []),
        }

        # Calculate distance from 52-week high/low
        if overview["current_price"] and overview["fifty_two_week_high"]:
            overview["pct_from_52w_high"] = (
                (overview["current_price"] - overview["fifty_two_week_high"])
                / overview["fifty_two_week_high"] * 100
            )
        else:
            overview["pct_from_52w_high"] = None

        if overview["current_price"] and overview["fifty_two_week_low"]:
            overview["pct_from_52w_low"] = (
                (overview["current_price"] - overview["fifty_two_week_low"])
                / overview["fifty_two_week_low"] * 100
            )
        else:
            overview["pct_from_52w_low"] = None

        return overview

    def get_historical_prices(self, years: int = 5) -> pd.DataFrame:
        """
        Get historical price and volume data.

        Args:
            years: Number of years of historical data to fetch

        Returns:
            DataFrame with OHLCV data and calculated metrics
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        history = self.stock.history(start=start_date, end=end_date)

        if history.empty:
            return pd.DataFrame()

        # Calculate returns
        history["Daily_Return"] = history["Close"].pct_change()
        history["Cumulative_Return"] = (1 + history["Daily_Return"]).cumprod() - 1

        # Calculate moving averages
        history["MA_50"] = history["Close"].rolling(window=50).mean()
        history["MA_200"] = history["Close"].rolling(window=200).mean()

        # Calculate volatility (20-day rolling)
        history["Volatility_20d"] = history["Daily_Return"].rolling(window=20).std() * np.sqrt(252)

        # Calculate RSI (14-day)
        delta = history["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        history["RSI_14"] = 100 - (100 / (1 + rs))

        self._history = history
        return history

    def calculate_return_metrics(self, history: pd.DataFrame = None) -> Dict[str, float]:
        """
        Calculate various return metrics.

        Args:
            history: Historical price DataFrame (optional, will fetch if not provided)

        Returns:
            Dictionary of return metrics
        """
        if history is None:
            history = self.get_historical_prices()

        if history.empty:
            return {}

        metrics = {}

        # Daily returns stats
        daily_returns = history["Daily_Return"].dropna()
        metrics["avg_daily_return"] = daily_returns.mean()
        metrics["daily_volatility"] = daily_returns.std()
        metrics["annualized_volatility"] = daily_returns.std() * np.sqrt(252)

        # Period returns
        if len(history) >= 21:  # ~1 month
            metrics["return_1m"] = history["Close"].iloc[-1] / history["Close"].iloc[-21] - 1
        if len(history) >= 63:  # ~3 months
            metrics["return_3m"] = history["Close"].iloc[-1] / history["Close"].iloc[-63] - 1
        if len(history) >= 126:  # ~6 months
            metrics["return_6m"] = history["Close"].iloc[-1] / history["Close"].iloc[-126] - 1
        if len(history) >= 252:  # ~1 year
            metrics["return_1y"] = history["Close"].iloc[-1] / history["Close"].iloc[-252] - 1
        if len(history) >= 756:  # ~3 years
            metrics["return_3y"] = history["Close"].iloc[-1] / history["Close"].iloc[-756] - 1
            metrics["cagr_3y"] = (history["Close"].iloc[-1] / history["Close"].iloc[-756]) ** (1/3) - 1
        if len(history) >= 1260:  # ~5 years
            metrics["return_5y"] = history["Close"].iloc[-1] / history["Close"].iloc[-1260] - 1
            metrics["cagr_5y"] = (history["Close"].iloc[-1] / history["Close"].iloc[-1260]) ** (1/5) - 1

        # YTD return
        current_year = datetime.now().year
        ytd_data = history[history.index.year == current_year]
        if not ytd_data.empty:
            metrics["return_ytd"] = ytd_data["Close"].iloc[-1] / ytd_data["Close"].iloc[0] - 1

        # Max drawdown
        cumulative_max = history["Close"].cummax()
        drawdown = (history["Close"] - cumulative_max) / cumulative_max
        metrics["max_drawdown"] = drawdown.min()

        # Sharpe ratio (assuming risk-free rate of 4%)
        risk_free_rate = 0.04
        excess_return = metrics.get("return_1y", 0) - risk_free_rate
        if metrics.get("annualized_volatility", 0) > 0:
            metrics["sharpe_ratio_1y"] = excess_return / metrics["annualized_volatility"]

        return metrics

    def get_income_statement(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get income statement data (annual and quarterly).

        Returns:
            Tuple of (annual, quarterly) income statement DataFrames
        """
        annual = self.stock.income_stmt
        quarterly = self.stock.quarterly_income_stmt

        return annual, quarterly

    def get_balance_sheet(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get balance sheet data (annual and quarterly).

        Returns:
            Tuple of (annual, quarterly) balance sheet DataFrames
        """
        annual = self.stock.balance_sheet
        quarterly = self.stock.quarterly_balance_sheet

        return annual, quarterly

    def get_cash_flow(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get cash flow statement data (annual and quarterly).

        Returns:
            Tuple of (annual, quarterly) cash flow DataFrames
        """
        annual = self.stock.cash_flow
        quarterly = self.stock.quarterly_cash_flow

        return annual, quarterly

    def get_key_statistics(self) -> Dict[str, Any]:
        """
        Get key financial statistics and ratios from yfinance.

        Returns:
            Dictionary of key statistics
        """
        info = self.info

        stats = {
            # Valuation ratios
            "pe_trailing": info.get("trailingPE", None),
            "pe_forward": info.get("forwardPE", None),
            "peg_ratio": info.get("pegRatio", None),
            "price_to_book": info.get("priceToBook", None),
            "price_to_sales": info.get("priceToSalesTrailing12Months", None),
            "ev_to_ebitda": info.get("enterpriseToEbitda", None),
            "ev_to_revenue": info.get("enterpriseToRevenue", None),

            # Profitability
            "profit_margin": info.get("profitMargins", None),
            "operating_margin": info.get("operatingMargins", None),
            "gross_margin": info.get("grossMargins", None),
            "roe": info.get("returnOnEquity", None),
            "roa": info.get("returnOnAssets", None),

            # Growth
            "revenue_growth": info.get("revenueGrowth", None),
            "earnings_growth": info.get("earningsGrowth", None),
            "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth", None),

            # Financial health
            "current_ratio": info.get("currentRatio", None),
            "quick_ratio": info.get("quickRatio", None),
            "debt_to_equity": info.get("debtToEquity", None),

            # Per share data
            "eps_trailing": info.get("trailingEps", None),
            "eps_forward": info.get("forwardEps", None),
            "book_value": info.get("bookValue", None),
            "revenue_per_share": info.get("revenuePerShare", None),

            # Cash flow
            "operating_cash_flow": info.get("operatingCashflow", None),
            "free_cash_flow": info.get("freeCashflow", None),

            # Beta
            "beta": info.get("beta", None),
        }

        return stats

    def get_analyst_recommendations(self) -> pd.DataFrame:
        """
        Get analyst recommendations and ratings.

        Returns:
            DataFrame with analyst recommendations
        """
        try:
            recommendations = self.stock.recommendations
            return recommendations if recommendations is not None else pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def get_earnings_history(self) -> pd.DataFrame:
        """
        Get earnings history (actual vs estimated).

        Returns:
            DataFrame with earnings history
        """
        try:
            earnings = self.stock.earnings_history
            return earnings if earnings is not None else pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def get_earnings_dates(self) -> pd.DataFrame:
        """
        Get upcoming and past earnings dates.

        Returns:
            DataFrame with earnings dates
        """
        try:
            dates = self.stock.earnings_dates
            return dates if dates is not None else pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def get_institutional_holders(self) -> pd.DataFrame:
        """
        Get institutional holders data.

        Returns:
            DataFrame with institutional holders
        """
        try:
            holders = self.stock.institutional_holders
            return holders if holders is not None else pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def get_insider_transactions(self) -> pd.DataFrame:
        """
        Get insider transactions data.

        Returns:
            DataFrame with insider transactions
        """
        try:
            transactions = self.stock.insider_transactions
            return transactions if transactions is not None else pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    def get_all_data(self) -> Dict[str, Any]:
        """
        Collect all available data for the ticker.

        Returns:
            Dictionary containing all collected data
        """
        print(f"Collecting data for {self.ticker}...")

        # Get historical prices first
        history = self.get_historical_prices()

        # Get financial statements
        income_annual, income_quarterly = self.get_income_statement()
        balance_annual, balance_quarterly = self.get_balance_sheet()
        cashflow_annual, cashflow_quarterly = self.get_cash_flow()

        all_data = {
            "ticker": self.ticker,
            "overview": self.get_company_overview(),
            "historical_prices": history,
            "return_metrics": self.calculate_return_metrics(history),
            "key_statistics": self.get_key_statistics(),
            "income_statement_annual": income_annual,
            "income_statement_quarterly": income_quarterly,
            "balance_sheet_annual": balance_annual,
            "balance_sheet_quarterly": balance_quarterly,
            "cash_flow_annual": cashflow_annual,
            "cash_flow_quarterly": cashflow_quarterly,
            "analyst_recommendations": self.get_analyst_recommendations(),
            "earnings_history": self.get_earnings_history(),
            "earnings_dates": self.get_earnings_dates(),
            "institutional_holders": self.get_institutional_holders(),
            "insider_transactions": self.get_insider_transactions(),
        }

        print(f"Data collection complete for {self.ticker}")
        return all_data


def collect_peer_data(peers: list) -> Dict[str, Dict[str, Any]]:
    """
    Collect data for multiple peer companies.

    Args:
        peers: List of peer ticker symbols

    Returns:
        Dictionary mapping ticker to collected data
    """
    peer_data = {}

    for peer in peers:
        try:
            print(f"  Collecting peer data: {peer}")
            collector = DataCollector(peer)
            peer_data[peer] = {
                "overview": collector.get_company_overview(),
                "key_statistics": collector.get_key_statistics(),
                "return_metrics": collector.calculate_return_metrics(),
            }
        except Exception as e:
            print(f"  Warning: Could not collect data for {peer}: {e}")
            continue

    return peer_data


if __name__ == "__main__":
    # Test the data collector
    collector = DataCollector("NVDA")
    data = collector.get_all_data()

    print("\n=== Company Overview ===")
    overview = data["overview"]
    print(f"Name: {overview['name']}")
    print(f"Sector: {overview['sector']}")
    print(f"Industry: {overview['industry']}")
    print(f"Market Cap: ${overview['market_cap']:,.0f}" if overview['market_cap'] else "Market Cap: N/A")

    print("\n=== Key Statistics ===")
    stats = data["key_statistics"]
    print(f"P/E Ratio: {stats['pe_trailing']:.2f}" if stats['pe_trailing'] else "P/E Ratio: N/A")
    print(f"EV/EBITDA: {stats['ev_to_ebitda']:.2f}" if stats['ev_to_ebitda'] else "EV/EBITDA: N/A")

    print("\n=== Return Metrics ===")
    returns = data["return_metrics"]
    for key, value in returns.items():
        if value is not None:
            print(f"{key}: {value:.2%}" if abs(value) < 100 else f"{key}: {value:.2f}")
