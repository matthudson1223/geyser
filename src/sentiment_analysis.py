"""
Sentiment and News Analysis Module for Equity Research Report Generator.

This module handles:
- News sentiment analysis
- Analyst recommendations
- Earnings history and surprises
- Macro and industry factors
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import yfinance as yf

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_WEB_LIBS = True
except ImportError:
    HAS_WEB_LIBS = False


class SentimentAnalyzer:
    """Analyzes sentiment and qualitative factors for a stock."""

    def __init__(self, ticker: str, data: Dict[str, Any]):
        """
        Initialize SentimentAnalyzer with company data.

        Args:
            ticker: Stock ticker symbol
            data: Collected company data
        """
        self.ticker = ticker.upper()
        self.data = data
        self.stock = yf.Ticker(self.ticker)

    def analyze_analyst_recommendations(self) -> Dict[str, Any]:
        """
        Analyze analyst recommendations and ratings.

        Returns:
            Dictionary with analyst recommendation analysis
        """
        result = {
            "has_coverage": False,
            "total_analysts": 0,
            "recommendation_breakdown": {},
            "consensus": "",
            "mean_rating": None,
            "recent_changes": [],
            "price_targets": {},
        }

        try:
            # Get recommendations
            recommendations = self.data.get("analyst_recommendations", pd.DataFrame())

            if recommendations is not None and not recommendations.empty:
                result["has_coverage"] = True

                # Get the most recent recommendations (last 30 days)
                if "period" in recommendations.columns:
                    recent = recommendations[recommendations["period"] == "0m"]
                else:
                    recent = recommendations.tail(10)

                # Count recommendation types
                if "strongBuy" in recommendations.columns:
                    # New format from yfinance
                    latest = recommendations.iloc[0] if len(recommendations) > 0 else None
                    if latest is not None:
                        result["recommendation_breakdown"] = {
                            "Strong Buy": int(latest.get("strongBuy", 0)),
                            "Buy": int(latest.get("buy", 0)),
                            "Hold": int(latest.get("hold", 0)),
                            "Sell": int(latest.get("sell", 0)),
                            "Strong Sell": int(latest.get("strongSell", 0)),
                        }
                        result["total_analysts"] = sum(result["recommendation_breakdown"].values())
                elif "To Grade" in recommendations.columns:
                    # Old format
                    grade_counts = recommendations["To Grade"].value_counts().to_dict()
                    result["recommendation_breakdown"] = grade_counts
                    result["total_analysts"] = len(recommendations)

                # Calculate mean rating (1 = Strong Buy, 5 = Strong Sell)
                breakdown = result["recommendation_breakdown"]
                if result["total_analysts"] > 0:
                    weighted_sum = (
                        breakdown.get("Strong Buy", 0) * 1 +
                        breakdown.get("Buy", 0) * 2 +
                        breakdown.get("Hold", 0) * 3 +
                        breakdown.get("Sell", 0) * 4 +
                        breakdown.get("Strong Sell", 0) * 5
                    )
                    result["mean_rating"] = weighted_sum / result["total_analysts"]

                    # Determine consensus
                    if result["mean_rating"] <= 1.5:
                        result["consensus"] = "Strong Buy"
                    elif result["mean_rating"] <= 2.5:
                        result["consensus"] = "Buy"
                    elif result["mean_rating"] <= 3.5:
                        result["consensus"] = "Hold"
                    elif result["mean_rating"] <= 4.5:
                        result["consensus"] = "Sell"
                    else:
                        result["consensus"] = "Strong Sell"

            # Get price targets from info
            info = self.stock.info
            result["price_targets"] = {
                "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
                "target_mean": info.get("targetMeanPrice"),
                "target_low": info.get("targetLowPrice"),
                "target_high": info.get("targetHighPrice"),
                "target_median": info.get("targetMedianPrice"),
                "number_of_analysts": info.get("numberOfAnalystOpinions"),
            }

            # Calculate upside/downside
            if result["price_targets"]["current_price"] and result["price_targets"]["target_mean"]:
                current = result["price_targets"]["current_price"]
                target = result["price_targets"]["target_mean"]
                result["price_targets"]["upside_pct"] = ((target / current) - 1) * 100

        except Exception as e:
            result["error"] = str(e)

        return result

    def analyze_earnings_history(self) -> Dict[str, Any]:
        """
        Analyze historical earnings surprises.

        Returns:
            Dictionary with earnings history analysis
        """
        result = {
            "has_data": False,
            "quarters_analyzed": 0,
            "beat_count": 0,
            "miss_count": 0,
            "meet_count": 0,
            "beat_rate": None,
            "avg_surprise_pct": None,
            "earnings_data": [],
            "trend": "",
        }

        try:
            # Try to get earnings history
            earnings = self.data.get("earnings_history", pd.DataFrame())

            if earnings is not None and not earnings.empty:
                result["has_data"] = True
                result["quarters_analyzed"] = len(earnings)

                surprises = []
                for _, row in earnings.iterrows():
                    eps_actual = row.get("epsActual")
                    eps_estimate = row.get("epsEstimate")

                    if pd.notna(eps_actual) and pd.notna(eps_estimate):
                        surprise_pct = ((eps_actual - eps_estimate) / abs(eps_estimate)) * 100 if eps_estimate != 0 else 0
                        surprises.append(surprise_pct)

                        if surprise_pct > 1:
                            result["beat_count"] += 1
                        elif surprise_pct < -1:
                            result["miss_count"] += 1
                        else:
                            result["meet_count"] += 1

                        result["earnings_data"].append({
                            "actual": eps_actual,
                            "estimate": eps_estimate,
                            "surprise_pct": surprise_pct,
                        })

                if surprises:
                    result["avg_surprise_pct"] = np.mean(surprises)
                    result["beat_rate"] = result["beat_count"] / result["quarters_analyzed"]

                    # Determine trend
                    if len(surprises) >= 4:
                        recent = surprises[:2]  # Most recent 2 quarters
                        older = surprises[2:4]  # Previous 2 quarters

                        if np.mean(recent) > np.mean(older):
                            result["trend"] = "Improving"
                        elif np.mean(recent) < np.mean(older):
                            result["trend"] = "Deteriorating"
                        else:
                            result["trend"] = "Stable"

            # Also try earnings_dates for upcoming earnings
            earnings_dates = self.data.get("earnings_dates", pd.DataFrame())
            if earnings_dates is not None and not earnings_dates.empty:
                # Filter for future dates
                now = datetime.now()
                future_dates = []
                for idx in earnings_dates.index:
                    if hasattr(idx, 'to_pydatetime'):
                        date = idx.to_pydatetime()
                        if date > now:
                            future_dates.append(date)

                if future_dates:
                    result["next_earnings_date"] = min(future_dates)

        except Exception as e:
            result["error"] = str(e)

        return result

    def analyze_insider_activity(self) -> Dict[str, Any]:
        """
        Analyze recent insider trading activity.

        Returns:
            Dictionary with insider activity analysis
        """
        result = {
            "has_data": False,
            "total_transactions": 0,
            "net_shares": 0,
            "buy_transactions": 0,
            "sell_transactions": 0,
            "net_sentiment": "",
            "recent_transactions": [],
        }

        try:
            transactions = self.data.get("insider_transactions", pd.DataFrame())

            if transactions is not None and not transactions.empty:
                result["has_data"] = True
                result["total_transactions"] = len(transactions)

                # Filter for last 90 days
                ninety_days_ago = datetime.now() - timedelta(days=90)

                recent = []
                net_shares = 0

                for _, row in transactions.iterrows():
                    # Check transaction type
                    trans_type = str(row.get("Text", "")).lower()
                    shares = row.get("Shares", 0)

                    if "buy" in trans_type or "purchase" in trans_type:
                        result["buy_transactions"] += 1
                        net_shares += shares if pd.notna(shares) else 0
                    elif "sell" in trans_type or "sale" in trans_type:
                        result["sell_transactions"] += 1
                        net_shares -= shares if pd.notna(shares) else 0

                    recent.append({
                        "insider": row.get("Insider", "Unknown"),
                        "position": row.get("Position", "Unknown"),
                        "transaction": row.get("Text", "Unknown"),
                        "shares": shares,
                        "value": row.get("Value", None),
                    })

                result["recent_transactions"] = recent[:10]  # Limit to 10 most recent
                result["net_shares"] = net_shares

                # Determine sentiment
                if result["buy_transactions"] > result["sell_transactions"] * 2:
                    result["net_sentiment"] = "Strongly Bullish"
                elif result["buy_transactions"] > result["sell_transactions"]:
                    result["net_sentiment"] = "Bullish"
                elif result["sell_transactions"] > result["buy_transactions"] * 2:
                    result["net_sentiment"] = "Strongly Bearish"
                elif result["sell_transactions"] > result["buy_transactions"]:
                    result["net_sentiment"] = "Bearish"
                else:
                    result["net_sentiment"] = "Neutral"

        except Exception as e:
            result["error"] = str(e)

        return result

    def analyze_institutional_ownership(self) -> Dict[str, Any]:
        """
        Analyze institutional ownership patterns.

        Returns:
            Dictionary with institutional ownership analysis
        """
        result = {
            "has_data": False,
            "total_institutional_holders": 0,
            "top_holders": [],
            "institutional_ownership_pct": None,
        }

        try:
            holders = self.data.get("institutional_holders", pd.DataFrame())

            if holders is not None and not holders.empty:
                result["has_data"] = True
                result["total_institutional_holders"] = len(holders)

                # Get top 10 holders
                for _, row in holders.head(10).iterrows():
                    result["top_holders"].append({
                        "holder": row.get("Holder", "Unknown"),
                        "shares": row.get("Shares", 0),
                        "value": row.get("Value", 0),
                        "pct_held": row.get("% Out", row.get("pctHeld", None)),
                    })

            # Get institutional ownership percentage from info
            info = self.stock.info
            result["institutional_ownership_pct"] = info.get("heldPercentInstitutions")
            result["insider_ownership_pct"] = info.get("heldPercentInsiders")

        except Exception as e:
            result["error"] = str(e)

        return result

    def calculate_momentum_score(self) -> Dict[str, Any]:
        """
        Calculate technical momentum indicators.

        Returns:
            Dictionary with momentum analysis
        """
        result = {
            "price_momentum": {},
            "volume_analysis": {},
            "technical_signals": [],
            "overall_momentum": "",
            "momentum_score": 5,  # Neutral score of 5 out of 10
        }

        try:
            overview = self.data.get("overview", {})
            return_metrics = self.data.get("return_metrics", {})
            history = self.data.get("historical_prices", pd.DataFrame())

            # Price momentum
            result["price_momentum"] = {
                "return_1m": return_metrics.get("return_1m"),
                "return_3m": return_metrics.get("return_3m"),
                "return_6m": return_metrics.get("return_6m"),
                "return_1y": return_metrics.get("return_1y"),
                "return_ytd": return_metrics.get("return_ytd"),
            }

            # Calculate momentum score based on returns
            score = 5  # Start neutral
            signals = []

            # 1-month return
            r1m = return_metrics.get("return_1m", 0) or 0
            if r1m > 0.10:
                score += 1
                signals.append("Strong 1M momentum (+10%+)")
            elif r1m > 0.05:
                score += 0.5
                signals.append("Positive 1M momentum (+5%+)")
            elif r1m < -0.10:
                score -= 1
                signals.append("Weak 1M momentum (-10%+)")
            elif r1m < -0.05:
                score -= 0.5
                signals.append("Negative 1M momentum (-5%+)")

            # Price vs moving averages
            current_price = overview.get("current_price")
            ma50 = overview.get("fifty_day_avg")
            ma200 = overview.get("two_hundred_day_avg")

            if current_price and ma50:
                if current_price > ma50:
                    score += 0.5
                    signals.append("Price above 50-day MA")
                else:
                    score -= 0.5
                    signals.append("Price below 50-day MA")

            if current_price and ma200:
                if current_price > ma200:
                    score += 0.5
                    signals.append("Price above 200-day MA")
                else:
                    score -= 0.5
                    signals.append("Price below 200-day MA")

            # Golden/Death cross
            if ma50 and ma200:
                if ma50 > ma200:
                    score += 0.5
                    signals.append("Golden cross (50MA > 200MA)")
                else:
                    score -= 0.5
                    signals.append("Death cross (50MA < 200MA)")

            # 52-week position
            pct_from_high = overview.get("pct_from_52w_high", 0) or 0
            pct_from_low = overview.get("pct_from_52w_low", 0) or 0

            if pct_from_high > -5:
                score += 0.5
                signals.append("Near 52-week high")
            elif pct_from_high < -30:
                score -= 0.5
                signals.append("Significantly below 52-week high (>30%)")

            # Clamp score between 1 and 10
            score = max(1, min(10, score))
            result["momentum_score"] = round(score, 1)
            result["technical_signals"] = signals

            # Overall momentum assessment
            if score >= 7:
                result["overall_momentum"] = "Strong Bullish"
            elif score >= 6:
                result["overall_momentum"] = "Bullish"
            elif score >= 4:
                result["overall_momentum"] = "Neutral"
            elif score >= 3:
                result["overall_momentum"] = "Bearish"
            else:
                result["overall_momentum"] = "Strong Bearish"

            # RSI analysis if available
            if not history.empty and "RSI_14" in history.columns:
                latest_rsi = history["RSI_14"].iloc[-1]
                result["rsi"] = latest_rsi
                if latest_rsi > 70:
                    signals.append(f"RSI overbought ({latest_rsi:.0f})")
                elif latest_rsi < 30:
                    signals.append(f"RSI oversold ({latest_rsi:.0f})")

        except Exception as e:
            result["error"] = str(e)

        return result

    def get_sentiment_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive sentiment analysis summary.

        Returns:
            Dictionary with all sentiment analysis results
        """
        summary = {
            "ticker": self.ticker,
            "analyst_recommendations": self.analyze_analyst_recommendations(),
            "earnings_history": self.analyze_earnings_history(),
            "insider_activity": self.analyze_insider_activity(),
            "institutional_ownership": self.analyze_institutional_ownership(),
            "momentum": self.calculate_momentum_score(),
        }

        # Calculate overall sentiment score
        scores = []

        # Analyst sentiment (weight: 30%)
        analyst = summary["analyst_recommendations"]
        if analyst["mean_rating"]:
            # Convert 1-5 scale (1=buy, 5=sell) to 1-10 scale (10=very bullish)
            analyst_score = 10 - (analyst["mean_rating"] - 1) * 2.25
            scores.append(("analyst", analyst_score, 0.30))

        # Earnings momentum (weight: 25%)
        earnings = summary["earnings_history"]
        if earnings["beat_rate"] is not None:
            earnings_score = 5 + earnings["beat_rate"] * 5  # 50% beat rate = 7.5
            if earnings.get("avg_surprise_pct", 0) > 5:
                earnings_score += 1
            scores.append(("earnings", min(10, earnings_score), 0.25))

        # Price momentum (weight: 25%)
        momentum = summary["momentum"]
        scores.append(("momentum", momentum["momentum_score"], 0.25))

        # Insider sentiment (weight: 10%)
        insider = summary["insider_activity"]
        if insider["net_sentiment"]:
            insider_scores = {
                "Strongly Bullish": 9,
                "Bullish": 7,
                "Neutral": 5,
                "Bearish": 3,
                "Strongly Bearish": 1,
            }
            scores.append(("insider", insider_scores.get(insider["net_sentiment"], 5), 0.10))

        # Upside potential (weight: 10%)
        if analyst.get("price_targets", {}).get("upside_pct") is not None:
            upside = analyst["price_targets"]["upside_pct"]
            if upside > 30:
                upside_score = 9
            elif upside > 15:
                upside_score = 7
            elif upside > 0:
                upside_score = 6
            elif upside > -15:
                upside_score = 4
            else:
                upside_score = 2
            scores.append(("upside", upside_score, 0.10))

        # Calculate weighted average
        if scores:
            total_weight = sum(w for _, _, w in scores)
            weighted_sum = sum(s * w for _, s, w in scores)
            summary["overall_sentiment_score"] = round(weighted_sum / total_weight, 1)

            # Classify overall sentiment
            score = summary["overall_sentiment_score"]
            if score >= 7.5:
                summary["overall_sentiment"] = "Very Bullish"
            elif score >= 6:
                summary["overall_sentiment"] = "Bullish"
            elif score >= 4.5:
                summary["overall_sentiment"] = "Neutral"
            elif score >= 3:
                summary["overall_sentiment"] = "Bearish"
            else:
                summary["overall_sentiment"] = "Very Bearish"
        else:
            summary["overall_sentiment_score"] = 5
            summary["overall_sentiment"] = "Neutral (Limited Data)"

        summary["score_components"] = scores

        return summary


if __name__ == "__main__":
    # Test the sentiment analyzer
    from data_collector import DataCollector

    ticker = "NVDA"
    print(f"Testing sentiment analysis for {ticker}")

    collector = DataCollector(ticker)
    data = collector.get_all_data()

    analyzer = SentimentAnalyzer(ticker, data)
    summary = analyzer.get_sentiment_summary()

    print("\n=== Analyst Recommendations ===")
    analyst = summary["analyst_recommendations"]
    print(f"Consensus: {analyst.get('consensus', 'N/A')}")
    print(f"Mean Rating: {analyst.get('mean_rating', 'N/A')}")
    print(f"Total Analysts: {analyst.get('total_analysts', 'N/A')}")

    if analyst.get("price_targets"):
        pt = analyst["price_targets"]
        print(f"\nPrice Targets:")
        print(f"  Current: ${pt.get('current_price', 'N/A')}")
        print(f"  Mean Target: ${pt.get('target_mean', 'N/A')}")
        print(f"  Upside: {pt.get('upside_pct', 'N/A'):.1f}%")

    print("\n=== Earnings History ===")
    earnings = summary["earnings_history"]
    print(f"Beat Rate: {earnings.get('beat_rate', 'N/A')}")
    print(f"Avg Surprise: {earnings.get('avg_surprise_pct', 'N/A')}%")
    print(f"Trend: {earnings.get('trend', 'N/A')}")

    print("\n=== Momentum ===")
    momentum = summary["momentum"]
    print(f"Overall Momentum: {momentum.get('overall_momentum', 'N/A')}")
    print(f"Momentum Score: {momentum.get('momentum_score', 'N/A')}/10")
    print("Signals:")
    for signal in momentum.get("technical_signals", []):
        print(f"  - {signal}")

    print("\n=== Overall Sentiment ===")
    print(f"Sentiment: {summary.get('overall_sentiment', 'N/A')}")
    print(f"Score: {summary.get('overall_sentiment_score', 'N/A')}/10")
