"""
Peer Comparison Module for Equity Research Report Generator.

This module handles:
- Identifying peer companies
- Collecting peer data
- Comparative analysis
- Relative valuation assessment
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import yfinance as yf

from .config import get_peers, PEER_MAPPING
from .data_collector import DataCollector


class PeerComparison:
    """Performs peer comparison analysis."""

    def __init__(self, ticker: str, data: Dict[str, Any]):
        """
        Initialize PeerComparison with target company data.

        Args:
            ticker: Target company ticker symbol
            data: Collected data for the target company
        """
        self.ticker = ticker.upper()
        self.data = data
        self.overview = data.get("overview", {})
        self.stats = data.get("key_statistics", {})
        self.peers = []
        self.peer_data = {}

    def identify_peers(self, custom_peers: List[str] = None) -> List[str]:
        """
        Identify peer companies for comparison.

        Args:
            custom_peers: Optional list of custom peer tickers

        Returns:
            List of peer ticker symbols
        """
        if custom_peers:
            self.peers = [p.upper() for p in custom_peers]
        else:
            # Try to get from predefined mapping
            self.peers = get_peers(self.ticker)

            # If not in mapping, try to find peers dynamically based on sector/industry
            if not self.peers or self.peers == ["SPY"]:
                self.peers = self._find_dynamic_peers()

        return self.peers

    def _find_dynamic_peers(self) -> List[str]:
        """Find peers dynamically based on sector and industry."""
        sector = self.overview.get("sector", "")
        industry = self.overview.get("industry", "")

        # This is a simplified approach - in production, you might use
        # a more sophisticated industry classification system
        sector_tickers = {
            "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMD", "INTC"],
            "Financial Services": ["JPM", "BAC", "WFC", "GS", "MS", "C"],
            "Healthcare": ["JNJ", "PFE", "MRK", "ABBV", "LLY", "UNH"],
            "Consumer Cyclical": ["AMZN", "TSLA", "HD", "NKE", "MCD", "SBUX"],
            "Consumer Defensive": ["WMT", "PG", "KO", "PEP", "COST", "CL"],
            "Energy": ["XOM", "CVX", "COP", "EOG", "SLB", "OXY"],
            "Industrials": ["CAT", "DE", "BA", "HON", "UPS", "RTX"],
            "Communication Services": ["GOOGL", "META", "DIS", "NFLX", "T", "VZ"],
            "Utilities": ["NEE", "DUK", "SO", "D", "AEP", "XEL"],
            "Real Estate": ["PLD", "AMT", "CCI", "EQIX", "SPG", "O"],
            "Materials": ["LIN", "APD", "ECL", "SHW", "FCX", "NEM"],
        }

        # Get sector peers
        potential_peers = sector_tickers.get(sector, [])

        # Remove the target ticker and limit to 5 peers
        peers = [p for p in potential_peers if p != self.ticker][:5]

        return peers if peers else ["SPY"]  # Fallback to S&P 500

    def collect_peer_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Collect financial data for all peer companies.

        Returns:
            Dictionary mapping peer tickers to their data
        """
        print(f"\nCollecting peer data for {self.ticker}...")
        print(f"Peers: {', '.join(self.peers)}")

        for peer in self.peers:
            try:
                print(f"  Fetching data for {peer}...")
                collector = DataCollector(peer)

                self.peer_data[peer] = {
                    "overview": collector.get_company_overview(),
                    "stats": collector.get_key_statistics(),
                    "return_metrics": collector.calculate_return_metrics(),
                }
            except Exception as e:
                print(f"  Warning: Could not collect data for {peer}: {e}")
                continue

        print(f"Collected data for {len(self.peer_data)} peers")
        return self.peer_data

    def create_comparison_matrix(self) -> pd.DataFrame:
        """
        Create a comprehensive comparison matrix.

        Returns:
            DataFrame with comparison of key metrics across all companies
        """
        # Define metrics to compare
        metrics = {
            # Valuation
            "P/E (TTM)": ("stats", "pe_trailing"),
            "P/E (Forward)": ("stats", "pe_forward"),
            "PEG Ratio": ("stats", "peg_ratio"),
            "P/B": ("stats", "price_to_book"),
            "P/S": ("stats", "price_to_sales"),
            "EV/EBITDA": ("stats", "ev_to_ebitda"),
            "EV/Revenue": ("stats", "ev_to_revenue"),

            # Profitability
            "Gross Margin": ("stats", "gross_margin"),
            "Operating Margin": ("stats", "operating_margin"),
            "Net Margin": ("stats", "profit_margin"),
            "ROE": ("stats", "roe"),
            "ROA": ("stats", "roa"),

            # Growth
            "Revenue Growth": ("stats", "revenue_growth"),
            "Earnings Growth": ("stats", "earnings_growth"),

            # Financial Health
            "Current Ratio": ("stats", "current_ratio"),
            "Debt/Equity": ("stats", "debt_to_equity"),

            # Market Data
            "Market Cap ($B)": ("overview", "market_cap"),
            "Beta": ("stats", "beta"),

            # Returns
            "1Y Return": ("return_metrics", "return_1y"),
            "YTD Return": ("return_metrics", "return_ytd"),
        }

        # Build comparison data
        comparison_data = {"Metric": list(metrics.keys())}

        # Add target company data
        target_values = []
        for metric_name, (source, key) in metrics.items():
            if source == "overview":
                value = self.overview.get(key)
            elif source == "stats":
                value = self.stats.get(key)
            else:  # return_metrics
                value = self.data.get("return_metrics", {}).get(key)
            target_values.append(value)
        comparison_data[self.ticker] = target_values

        # Add peer data
        for peer in self.peers:
            if peer not in self.peer_data:
                continue

            peer_info = self.peer_data[peer]
            peer_values = []

            for metric_name, (source, key) in metrics.items():
                if source == "overview":
                    value = peer_info.get("overview", {}).get(key)
                elif source == "stats":
                    value = peer_info.get("stats", {}).get(key)
                else:  # return_metrics
                    value = peer_info.get("return_metrics", {}).get(key)
                peer_values.append(value)

            comparison_data[peer] = peer_values

        df = pd.DataFrame(comparison_data)
        df.set_index("Metric", inplace=True)

        # Calculate sector/peer average
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            df["Peer Avg"] = df[numeric_cols[1:]].mean(axis=1)  # Exclude target

        return df

    def format_comparison_table(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Format the comparison table for display.

        Args:
            df: Comparison DataFrame (will create if not provided)

        Returns:
            Formatted DataFrame
        """
        if df is None:
            df = self.create_comparison_matrix()

        formatted_df = df.copy()

        # Format based on metric type
        for idx in formatted_df.index:
            for col in formatted_df.columns:
                value = formatted_df.loc[idx, col]
                if pd.isna(value) or value is None:
                    formatted_df.loc[idx, col] = "N/A"
                elif "Margin" in idx or "ROE" in idx or "ROA" in idx or "Growth" in idx or "Return" in idx:
                    formatted_df.loc[idx, col] = f"{value:.1%}" if isinstance(value, (int, float)) else value
                elif "Market Cap" in idx:
                    formatted_df.loc[idx, col] = f"${value/1e9:.1f}B" if isinstance(value, (int, float)) else value
                elif isinstance(value, float):
                    formatted_df.loc[idx, col] = f"{value:.2f}"

        return formatted_df

    def calculate_relative_valuation(self) -> Dict[str, Any]:
        """
        Assess relative valuation compared to peers.

        Returns:
            Dictionary with relative valuation analysis
        """
        comparison = self.create_comparison_matrix()

        result = {
            "target": self.ticker,
            "peers": self.peers,
            "valuation_metrics": {},
            "premium_discount": {},
            "assessment": "",
        }

        valuation_metrics = ["P/E (TTM)", "P/E (Forward)", "EV/EBITDA", "P/S", "P/B"]

        for metric in valuation_metrics:
            if metric not in comparison.index:
                continue

            target_value = comparison.loc[metric, self.ticker]
            if pd.isna(target_value) or target_value is None:
                continue

            # Calculate peer average (excluding target)
            peer_values = []
            for peer in self.peers:
                if peer in comparison.columns:
                    val = comparison.loc[metric, peer]
                    if pd.notna(val) and val is not None:
                        peer_values.append(val)

            if not peer_values:
                continue

            peer_avg = np.mean(peer_values)

            # Calculate premium/discount
            if peer_avg > 0:
                premium_pct = ((target_value / peer_avg) - 1) * 100
            else:
                premium_pct = 0

            result["valuation_metrics"][metric] = {
                "target": target_value,
                "peer_avg": peer_avg,
                "peer_min": min(peer_values),
                "peer_max": max(peer_values),
            }

            result["premium_discount"][metric] = premium_pct

        # Generate assessment
        avg_premium = np.mean(list(result["premium_discount"].values())) if result["premium_discount"] else 0

        if avg_premium > 30:
            result["assessment"] = "Significant Premium"
            result["assessment_detail"] = f"Trading at {avg_premium:.0f}% premium to peers on average"
        elif avg_premium > 10:
            result["assessment"] = "Moderate Premium"
            result["assessment_detail"] = f"Trading at {avg_premium:.0f}% premium to peers on average"
        elif avg_premium > -10:
            result["assessment"] = "In-Line"
            result["assessment_detail"] = f"Trading roughly in-line with peers ({avg_premium:+.0f}%)"
        elif avg_premium > -30:
            result["assessment"] = "Moderate Discount"
            result["assessment_detail"] = f"Trading at {abs(avg_premium):.0f}% discount to peers on average"
        else:
            result["assessment"] = "Significant Discount"
            result["assessment_detail"] = f"Trading at {abs(avg_premium):.0f}% discount to peers on average"

        result["avg_premium_discount"] = avg_premium

        return result

    def is_valuation_justified(self) -> Dict[str, Any]:
        """
        Determine if the valuation premium/discount is justified.

        Returns:
            Dictionary with justification analysis
        """
        comparison = self.create_comparison_matrix()
        relative_val = self.calculate_relative_valuation()

        justification = {
            "valuation_status": relative_val["assessment"],
            "factors_supporting": [],
            "factors_against": [],
            "conclusion": "",
        }

        # Check growth metrics
        growth_metrics = ["Revenue Growth", "Earnings Growth"]
        for metric in growth_metrics:
            if metric in comparison.index:
                target = comparison.loc[metric, self.ticker]
                peer_avg = comparison.loc[metric, "Peer Avg"] if "Peer Avg" in comparison.columns else None

                if pd.notna(target) and pd.notna(peer_avg):
                    if target > peer_avg * 1.2:  # 20% higher growth
                        justification["factors_supporting"].append(
                            f"Higher {metric.lower()} ({target:.1%} vs peer avg {peer_avg:.1%})"
                        )
                    elif target < peer_avg * 0.8:  # 20% lower growth
                        justification["factors_against"].append(
                            f"Lower {metric.lower()} ({target:.1%} vs peer avg {peer_avg:.1%})"
                        )

        # Check profitability metrics
        profit_metrics = ["Net Margin", "ROE", "ROA"]
        for metric in profit_metrics:
            if metric in comparison.index:
                target = comparison.loc[metric, self.ticker]
                peer_avg = comparison.loc[metric, "Peer Avg"] if "Peer Avg" in comparison.columns else None

                if pd.notna(target) and pd.notna(peer_avg) and peer_avg != 0:
                    if target > peer_avg * 1.2:
                        justification["factors_supporting"].append(
                            f"Higher {metric.lower()} ({target:.1%} vs peer avg {peer_avg:.1%})"
                        )
                    elif target < peer_avg * 0.8:
                        justification["factors_against"].append(
                            f"Lower {metric.lower()} ({target:.1%} vs peer avg {peer_avg:.1%})"
                        )

        # Generate conclusion
        supporting = len(justification["factors_supporting"])
        against = len(justification["factors_against"])

        if relative_val["avg_premium_discount"] > 10:  # Trading at premium
            if supporting > against:
                justification["conclusion"] = "Premium appears JUSTIFIED by superior fundamentals"
            elif against > supporting:
                justification["conclusion"] = "Premium may be UNJUSTIFIED - fundamentals don't support valuation"
            else:
                justification["conclusion"] = "Premium justification is MIXED - some fundamentals support, others don't"
        elif relative_val["avg_premium_discount"] < -10:  # Trading at discount
            if against > supporting:
                justification["conclusion"] = "Discount appears JUSTIFIED by weaker fundamentals"
            elif supporting > against:
                justification["conclusion"] = "Discount may be UNJUSTIFIED - could be undervalued opportunity"
            else:
                justification["conclusion"] = "Discount justification is MIXED"
        else:
            justification["conclusion"] = "Valuation is roughly in-line with peers and fundamentals"

        return justification

    def get_peer_summary(self) -> Dict[str, Any]:
        """
        Get a complete peer comparison summary.

        Returns:
            Dictionary with all peer comparison analysis
        """
        summary = {
            "ticker": self.ticker,
            "peers": self.peers,
            "comparison_matrix": self.create_comparison_matrix(),
            "formatted_comparison": self.format_comparison_table(),
            "relative_valuation": self.calculate_relative_valuation(),
            "valuation_justification": self.is_valuation_justified(),
        }

        return summary


if __name__ == "__main__":
    # Test the peer comparison module
    from data_collector import DataCollector

    ticker = "NVDA"
    print(f"Testing peer comparison for {ticker}")

    # Collect target company data
    collector = DataCollector(ticker)
    data = collector.get_all_data()

    # Create peer comparison
    peer_comp = PeerComparison(ticker, data)
    peers = peer_comp.identify_peers()
    print(f"\nIdentified peers: {peers}")

    # Collect peer data
    peer_comp.collect_peer_data()

    # Create comparison matrix
    print("\n=== Comparison Matrix ===")
    comparison = peer_comp.format_comparison_table()
    print(comparison.to_string())

    # Relative valuation
    print("\n=== Relative Valuation ===")
    rel_val = peer_comp.calculate_relative_valuation()
    print(f"Assessment: {rel_val['assessment']}")
    print(f"Detail: {rel_val['assessment_detail']}")

    print("\nPremium/Discount by Metric:")
    for metric, pct in rel_val["premium_discount"].items():
        print(f"  {metric}: {pct:+.1f}%")

    # Valuation justification
    print("\n=== Valuation Justification ===")
    justification = peer_comp.is_valuation_justified()
    print(f"Conclusion: {justification['conclusion']}")

    if justification["factors_supporting"]:
        print("\nFactors Supporting Valuation:")
        for factor in justification["factors_supporting"]:
            print(f"  + {factor}")

    if justification["factors_against"]:
        print("\nFactors Against Valuation:")
        for factor in justification["factors_against"]:
            print(f"  - {factor}")
