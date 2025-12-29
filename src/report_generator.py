"""
Report Generator Module for Equity Research Report Generator.

This module handles:
- Investment thesis generation (bull/bear cases)
- Scoring and recommendation system
- Report assembly and formatting
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
from tabulate import tabulate

from .config import SCORE_WEIGHTS, RECOMMENDATION_THRESHOLDS


class ScoringEngine:
    """Calculates investment scores and generates recommendations."""

    def __init__(self, analysis: Dict[str, Any], peer_summary: Dict[str, Any],
                 sentiment: Dict[str, Any]):
        """
        Initialize ScoringEngine.

        Args:
            analysis: Financial analysis results
            peer_summary: Peer comparison summary
            sentiment: Sentiment analysis results
        """
        self.analysis = analysis
        self.peer_summary = peer_summary
        self.sentiment = sentiment
        self.ticker = analysis.get("ticker", "Unknown")

    def score_valuation(self) -> Dict[str, Any]:
        """
        Score the stock's valuation.

        Returns:
            Dictionary with valuation score and rationale
        """
        score = 5.0  # Start neutral
        factors = []

        valuation = self.analysis.get("valuation", {})
        relative_val = self.peer_summary.get("relative_valuation", {})

        # P/E analysis
        pe = valuation.get("pe_trailing")
        pe_forward = valuation.get("pe_forward")

        if pe:
            if pe < 15:
                score += 1.5
                factors.append(f"Low P/E ({pe:.1f}x) suggests value")
            elif pe < 25:
                score += 0.5
                factors.append(f"Reasonable P/E ({pe:.1f}x)")
            elif pe > 50:
                score -= 1.5
                factors.append(f"High P/E ({pe:.1f}x) suggests premium valuation")
            elif pe > 35:
                score -= 0.5
                factors.append(f"Elevated P/E ({pe:.1f}x)")

        # Forward P/E vs trailing (earnings growth expected?)
        if pe and pe_forward:
            if pe_forward < pe * 0.8:
                score += 0.5
                factors.append("Forward P/E significantly lower - growth expected")
            elif pe_forward > pe * 1.2:
                score -= 0.5
                factors.append("Forward P/E higher - potential earnings decline")

        # PEG ratio
        peg = valuation.get("peg_ratio")
        if peg:
            if peg < 1:
                score += 1
                factors.append(f"Attractive PEG ratio ({peg:.2f})")
            elif peg > 2:
                score -= 0.5
                factors.append(f"High PEG ratio ({peg:.2f})")

        # Relative valuation vs peers
        avg_premium = relative_val.get("avg_premium_discount", 0)
        if avg_premium < -20:
            score += 1
            factors.append(f"Trading at {abs(avg_premium):.0f}% discount to peers")
        elif avg_premium < -10:
            score += 0.5
            factors.append(f"Trading at slight discount to peers")
        elif avg_premium > 30:
            score -= 1
            factors.append(f"Significant premium ({avg_premium:.0f}%) vs peers")
        elif avg_premium > 15:
            score -= 0.5
            factors.append(f"Premium valuation vs peers")

        # FCF yield
        fcf_yield = valuation.get("fcf_yield")
        if fcf_yield:
            if fcf_yield > 0.06:
                score += 0.5
                factors.append(f"Strong FCF yield ({fcf_yield:.1%})")
            elif fcf_yield < 0.02:
                score -= 0.5
                factors.append(f"Low FCF yield ({fcf_yield:.1%})")

        score = max(1, min(10, score))

        return {
            "score": round(score, 1),
            "weight": SCORE_WEIGHTS["valuation"],
            "weighted": round(score * SCORE_WEIGHTS["valuation"], 2),
            "factors": factors,
        }

    def score_growth(self) -> Dict[str, Any]:
        """
        Score the stock's growth profile.

        Returns:
            Dictionary with growth score and rationale
        """
        score = 5.0
        factors = []

        growth = self.analysis.get("growth", {})

        # Revenue growth
        rev_growth = growth.get("revenue_growth_1y") or growth.get("revenue_growth_yoy")
        if rev_growth:
            if rev_growth > 0.30:
                score += 2
                factors.append(f"Excellent revenue growth ({rev_growth:.1%})")
            elif rev_growth > 0.15:
                score += 1
                factors.append(f"Strong revenue growth ({rev_growth:.1%})")
            elif rev_growth > 0.05:
                score += 0.5
                factors.append(f"Moderate revenue growth ({rev_growth:.1%})")
            elif rev_growth < 0:
                score -= 1
                factors.append(f"Revenue declining ({rev_growth:.1%})")

        # Revenue CAGR
        rev_cagr = growth.get("revenue_cagr_3y")
        if rev_cagr:
            if rev_cagr > 0.20:
                score += 1
                factors.append(f"Strong 3-year revenue CAGR ({rev_cagr:.1%})")
            elif rev_cagr < 0.05:
                score -= 0.5
                factors.append(f"Slow revenue growth over 3 years")

        # EPS growth
        eps_growth = growth.get("eps_growth_1y")
        if eps_growth:
            if eps_growth > 0.25:
                score += 1
                factors.append(f"Strong EPS growth ({eps_growth:.1%})")
            elif eps_growth < 0:
                score -= 1
                factors.append(f"EPS declining ({eps_growth:.1%})")

        # FCF growth
        fcf_growth = growth.get("fcf_growth_1y")
        if fcf_growth:
            if fcf_growth > 0.20:
                score += 0.5
                factors.append(f"Strong FCF growth ({fcf_growth:.1%})")
            elif fcf_growth < -0.20:
                score -= 0.5
                factors.append(f"FCF declining significantly")

        score = max(1, min(10, score))

        return {
            "score": round(score, 1),
            "weight": SCORE_WEIGHTS["growth"],
            "weighted": round(score * SCORE_WEIGHTS["growth"], 2),
            "factors": factors,
        }

    def score_profitability(self) -> Dict[str, Any]:
        """
        Score the stock's profitability.

        Returns:
            Dictionary with profitability score and rationale
        """
        score = 5.0
        factors = []

        prof = self.analysis.get("profitability", {})

        # Gross margin
        gross_margin = prof.get("gross_margin")
        if gross_margin:
            if gross_margin > 0.60:
                score += 1.5
                factors.append(f"Excellent gross margin ({gross_margin:.1%})")
            elif gross_margin > 0.40:
                score += 0.5
                factors.append(f"Good gross margin ({gross_margin:.1%})")
            elif gross_margin < 0.20:
                score -= 1
                factors.append(f"Low gross margin ({gross_margin:.1%})")

        # Operating margin
        op_margin = prof.get("operating_margin")
        if op_margin:
            if op_margin > 0.25:
                score += 1
                factors.append(f"Strong operating margin ({op_margin:.1%})")
            elif op_margin > 0.15:
                score += 0.5
                factors.append(f"Healthy operating margin ({op_margin:.1%})")
            elif op_margin < 0.05:
                score -= 1
                factors.append(f"Thin operating margin ({op_margin:.1%})")

        # ROE
        roe = prof.get("roe")
        if roe:
            if roe > 0.25:
                score += 1
                factors.append(f"Excellent ROE ({roe:.1%})")
            elif roe > 0.15:
                score += 0.5
                factors.append(f"Good ROE ({roe:.1%})")
            elif roe < 0.08:
                score -= 0.5
                factors.append(f"Low ROE ({roe:.1%})")

        # ROIC
        roic = prof.get("roic")
        if roic:
            if roic > 0.20:
                score += 1
                factors.append(f"High ROIC ({roic:.1%}) - efficient capital allocation")
            elif roic < 0.08:
                score -= 0.5
                factors.append(f"Low ROIC ({roic:.1%})")

        score = max(1, min(10, score))

        return {
            "score": round(score, 1),
            "weight": SCORE_WEIGHTS["profitability"],
            "weighted": round(score * SCORE_WEIGHTS["profitability"], 2),
            "factors": factors,
        }

    def score_financial_health(self) -> Dict[str, Any]:
        """
        Score the stock's financial health.

        Returns:
            Dictionary with financial health score and rationale
        """
        score = 5.0
        factors = []

        health = self.analysis.get("financial_health", {})

        # Current ratio
        current_ratio = health.get("current_ratio")
        if current_ratio:
            if current_ratio > 2:
                score += 1
                factors.append(f"Strong current ratio ({current_ratio:.2f})")
            elif current_ratio > 1.5:
                score += 0.5
                factors.append(f"Healthy current ratio ({current_ratio:.2f})")
            elif current_ratio < 1:
                score -= 1
                factors.append(f"Low current ratio ({current_ratio:.2f}) - liquidity risk")

        # Debt/Equity
        de_ratio = health.get("debt_to_equity")
        if de_ratio is not None:
            if de_ratio < 30:
                score += 1
                factors.append(f"Low leverage (D/E: {de_ratio:.0f}%)")
            elif de_ratio < 100:
                score += 0.5
                factors.append(f"Moderate leverage (D/E: {de_ratio:.0f}%)")
            elif de_ratio > 200:
                score -= 1
                factors.append(f"High leverage (D/E: {de_ratio:.0f}%)")

        # Interest coverage
        int_coverage = health.get("interest_coverage")
        if int_coverage:
            if int_coverage > 10:
                score += 1
                factors.append(f"Excellent interest coverage ({int_coverage:.1f}x)")
            elif int_coverage > 5:
                score += 0.5
                factors.append(f"Good interest coverage ({int_coverage:.1f}x)")
            elif int_coverage < 2:
                score -= 1
                factors.append(f"Low interest coverage ({int_coverage:.1f}x) - debt risk")

        # Altman Z-Score
        z_score = health.get("altman_z_score")
        if z_score:
            if z_score > 3:
                score += 0.5
                factors.append(f"Strong Altman Z-Score ({z_score:.2f}) - low bankruptcy risk")
            elif z_score < 1.8:
                score -= 1
                factors.append(f"Low Altman Z-Score ({z_score:.2f}) - elevated risk")

        score = max(1, min(10, score))

        return {
            "score": round(score, 1),
            "weight": SCORE_WEIGHTS["financial_health"],
            "weighted": round(score * SCORE_WEIGHTS["financial_health"], 2),
            "factors": factors,
        }

    def score_momentum_sentiment(self) -> Dict[str, Any]:
        """
        Score momentum and market sentiment.

        Returns:
            Dictionary with momentum/sentiment score and rationale
        """
        score = 5.0
        factors = []

        momentum = self.sentiment.get("momentum", {})
        analyst = self.sentiment.get("analyst_recommendations", {})
        earnings = self.sentiment.get("earnings_history", {})

        # Technical momentum
        momentum_score = momentum.get("momentum_score", 5)
        score = momentum_score  # Start with technical score

        for signal in momentum.get("technical_signals", [])[:3]:
            factors.append(signal)

        # Analyst sentiment
        mean_rating = analyst.get("mean_rating")
        if mean_rating:
            if mean_rating <= 2:
                score += 1
                factors.append("Strong analyst buy consensus")
            elif mean_rating <= 2.5:
                score += 0.5
                factors.append("Positive analyst sentiment")
            elif mean_rating >= 4:
                score -= 1
                factors.append("Bearish analyst sentiment")

        # Price target upside
        upside = analyst.get("price_targets", {}).get("upside_pct")
        if upside is not None:
            if upside > 20:
                score += 0.5
                factors.append(f"Significant upside to price target ({upside:.0f}%)")
            elif upside < -10:
                score -= 0.5
                factors.append(f"Below analyst price target ({upside:.0f}%)")

        # Earnings momentum
        beat_rate = earnings.get("beat_rate")
        if beat_rate is not None:
            if beat_rate >= 0.75:
                score += 0.5
                factors.append(f"Strong earnings beat rate ({beat_rate:.0%})")
            elif beat_rate < 0.5:
                score -= 0.5
                factors.append(f"Weak earnings beat rate ({beat_rate:.0%})")

        score = max(1, min(10, score))

        return {
            "score": round(score, 1),
            "weight": SCORE_WEIGHTS["momentum_sentiment"],
            "weighted": round(score * SCORE_WEIGHTS["momentum_sentiment"], 2),
            "factors": factors,
        }

    def score_quality_moat(self) -> Dict[str, Any]:
        """
        Score business quality and competitive moat.

        Returns:
            Dictionary with quality/moat score and rationale
        """
        score = 5.0
        factors = []

        prof = self.analysis.get("profitability", {})
        health = self.analysis.get("financial_health", {})
        growth = self.analysis.get("growth", {})

        # Consistent profitability (high margins suggest moat)
        gross_margin = prof.get("gross_margin", 0) or 0
        op_margin = prof.get("operating_margin", 0) or 0

        if gross_margin > 0.50 and op_margin > 0.20:
            score += 1.5
            factors.append("High margins suggest pricing power/moat")
        elif gross_margin > 0.40 and op_margin > 0.15:
            score += 0.5
            factors.append("Healthy margins indicate competitive position")

        # ROE/ROIC consistency (high returns suggest moat)
        roe = prof.get("roe", 0) or 0
        roic = prof.get("roic", 0) or 0

        if roe > 0.20 and roic > 0.15:
            score += 1
            factors.append("High ROE & ROIC suggest durable competitive advantage")

        # Revenue growth consistency
        rev_cagr = growth.get("revenue_cagr_3y")
        if rev_cagr and rev_cagr > 0.10:
            score += 0.5
            factors.append("Consistent revenue growth demonstrates market position")

        # Low debt (quality companies often have clean balance sheets)
        de_ratio = health.get("debt_to_equity", 100) or 100
        if de_ratio < 50:
            score += 0.5
            factors.append("Conservative capital structure")

        # Cash generation
        fcf = self.analysis.get("valuation", {}).get("fcf_yield", 0) or 0
        if fcf > 0.04:
            score += 0.5
            factors.append("Strong free cash flow generation")

        score = max(1, min(10, score))

        return {
            "score": round(score, 1),
            "weight": SCORE_WEIGHTS["quality_moat"],
            "weighted": round(score * SCORE_WEIGHTS["quality_moat"], 2),
            "factors": factors,
        }

    def calculate_total_score(self) -> Dict[str, Any]:
        """
        Calculate the total investment score.

        Returns:
            Dictionary with all scores and total
        """
        valuation = self.score_valuation()
        growth = self.score_growth()
        profitability = self.score_profitability()
        health = self.score_financial_health()
        momentum = self.score_momentum_sentiment()
        quality = self.score_quality_moat()

        total_score = (
            valuation["weighted"] +
            growth["weighted"] +
            profitability["weighted"] +
            health["weighted"] +
            momentum["weighted"] +
            quality["weighted"]
        )

        # Determine recommendation
        if total_score >= RECOMMENDATION_THRESHOLDS["strong_buy"]:
            recommendation = "Strong Buy"
        elif total_score >= RECOMMENDATION_THRESHOLDS["buy"]:
            recommendation = "Buy"
        elif total_score >= RECOMMENDATION_THRESHOLDS["hold"]:
            recommendation = "Hold"
        elif total_score >= RECOMMENDATION_THRESHOLDS["sell"]:
            recommendation = "Sell"
        else:
            recommendation = "Strong Sell"

        return {
            "ticker": self.ticker,
            "total_score": round(total_score, 1),
            "recommendation": recommendation,
            "categories": {
                "Valuation": valuation,
                "Growth": growth,
                "Profitability": profitability,
                "Financial Health": health,
                "Momentum/Sentiment": momentum,
                "Quality/Moat": quality,
            },
            "all_factors": {
                "valuation": valuation["factors"],
                "growth": growth["factors"],
                "profitability": profitability["factors"],
                "health": health["factors"],
                "momentum": momentum["factors"],
                "quality": quality["factors"],
            },
        }


class ThesisGenerator:
    """Generates bull and bear case investment theses."""

    def __init__(self, analysis: Dict[str, Any], peer_summary: Dict[str, Any],
                 sentiment: Dict[str, Any], scores: Dict[str, Any]):
        """
        Initialize ThesisGenerator.

        Args:
            analysis: Financial analysis results
            peer_summary: Peer comparison summary
            sentiment: Sentiment analysis results
            scores: Scoring results
        """
        self.analysis = analysis
        self.peer_summary = peer_summary
        self.sentiment = sentiment
        self.scores = scores
        self.ticker = analysis.get("ticker", "Unknown")

    def generate_bull_case(self) -> List[str]:
        """
        Generate bull case arguments.

        Returns:
            List of bull case points
        """
        bull_points = []
        factors = self.scores.get("all_factors", {})

        # Collect positive factors from all categories
        for category, category_factors in factors.items():
            for factor in category_factors:
                # Include factors that are positive
                if any(word in factor.lower() for word in
                       ["strong", "excellent", "high", "good", "healthy", "low p/e",
                        "attractive", "growth", "beat", "bullish", "upside", "above"]):
                    bull_points.append(factor)

        # Add additional bull case points based on analysis
        growth = self.analysis.get("growth", {})
        valuation = self.analysis.get("valuation", {})
        prof = self.analysis.get("profitability", {})

        # Growth catalysts
        rev_growth = growth.get("revenue_growth_1y", 0) or 0
        if rev_growth > 0.15:
            if f"revenue growth" not in " ".join(bull_points).lower():
                bull_points.append(f"Revenue growing at {rev_growth:.1%} YoY")

        # Margin expansion opportunity
        trends = prof.get("margin_trends", {})
        if trends.get("operating_margin"):
            margins = [m for m in trends["operating_margin"] if m is not None]
            if len(margins) >= 2 and margins[0] > margins[-1]:
                bull_points.append("Operating margins expanding year-over-year")

        # Undervaluation vs peers
        relative = self.peer_summary.get("relative_valuation", {})
        if relative.get("avg_premium_discount", 0) < -15:
            bull_points.append(f"Trading at discount to peers despite comparable fundamentals")

        # Analyst upside
        analyst = self.sentiment.get("analyst_recommendations", {})
        upside = analyst.get("price_targets", {}).get("upside_pct", 0) or 0
        if upside > 15:
            bull_points.append(f"Analyst consensus implies {upside:.0f}% upside potential")

        # Remove duplicates and limit to top 5
        unique_points = list(dict.fromkeys(bull_points))
        return unique_points[:5]

    def generate_bear_case(self) -> List[str]:
        """
        Generate bear case arguments.

        Returns:
            List of bear case points
        """
        bear_points = []
        factors = self.scores.get("all_factors", {})

        # Collect negative factors from all categories
        for category, category_factors in factors.items():
            for factor in category_factors:
                if any(word in factor.lower() for word in
                       ["low", "weak", "declining", "high p/e", "elevated", "risk",
                        "bearish", "below", "miss", "thin", "concern"]):
                    bear_points.append(factor)

        # Add additional bear case points based on analysis
        valuation = self.analysis.get("valuation", {})
        health = self.analysis.get("financial_health", {})

        # Valuation concerns
        pe = valuation.get("pe_trailing")
        if pe and pe > 35:
            if "p/e" not in " ".join(bear_points).lower():
                bear_points.append(f"Trading at {pe:.0f}x earnings - limited margin of safety")

        # Relative premium
        relative = self.peer_summary.get("relative_valuation", {})
        if relative.get("avg_premium_discount", 0) > 20:
            bear_points.append("Premium valuation relative to peers may not be sustainable")

        # Leverage concerns
        de = health.get("debt_to_equity")
        if de and de > 100:
            bear_points.append(f"Elevated debt levels (D/E: {de:.0f}%) increase risk")

        # Growth deceleration
        growth = self.analysis.get("growth", {})
        rev_1y = growth.get("revenue_growth_1y", 0) or 0
        rev_3y_cagr = growth.get("revenue_cagr_3y", 0) or 0
        if rev_3y_cagr > 0 and rev_1y < rev_3y_cagr * 0.7:
            bear_points.append("Revenue growth decelerating vs historical trend")

        # Analyst downside
        analyst = self.sentiment.get("analyst_recommendations", {})
        upside = analyst.get("price_targets", {}).get("upside_pct", 0) or 0
        if upside < -10:
            bear_points.append(f"Trading above analyst price target ({upside:.0f}%)")

        # Remove duplicates and limit to top 5
        unique_points = list(dict.fromkeys(bear_points))
        return unique_points[:5]

    def generate_key_metrics_to_monitor(self) -> List[str]:
        """
        Generate list of key metrics to monitor.

        Returns:
            List of KPIs to track
        """
        metrics = [
            "Quarterly revenue growth and guidance",
            "Operating margin trends",
            "Free cash flow generation",
        ]

        # Add sector-specific metrics
        industry = self.analysis.get("industry", "").lower()

        if "software" in industry or "tech" in industry:
            metrics.append("Customer acquisition and retention rates")
            metrics.append("R&D spending as % of revenue")
        elif "semiconductor" in industry:
            metrics.append("Data center/AI segment growth")
            metrics.append("Gross margin trends by segment")
        elif "retail" in industry:
            metrics.append("Same-store sales growth")
            metrics.append("Inventory turnover")
        elif "bank" in industry or "financial" in industry:
            metrics.append("Net interest margin")
            metrics.append("Loan loss provisions")

        # Add valuation-specific monitors
        pe = self.analysis.get("valuation", {}).get("pe_trailing", 0) or 0
        if pe > 30:
            metrics.append("Earnings growth to justify premium valuation")

        # Add balance sheet monitors if relevant
        health = self.analysis.get("financial_health", {})
        if (health.get("debt_to_equity") or 0) > 80:
            metrics.append("Debt reduction progress and interest expense")

        return metrics[:7]


class ReportGenerator:
    """Generates the final equity research report."""

    def __init__(self, ticker: str, data: Dict[str, Any], analysis: Dict[str, Any],
                 peer_summary: Dict[str, Any], sentiment: Dict[str, Any]):
        """
        Initialize ReportGenerator.

        Args:
            ticker: Stock ticker symbol
            data: Raw collected data
            analysis: Financial analysis results
            peer_summary: Peer comparison summary
            sentiment: Sentiment analysis results
        """
        self.ticker = ticker.upper()
        self.data = data
        self.analysis = analysis
        self.peer_summary = peer_summary
        self.sentiment = sentiment

        # Calculate scores
        self.scoring_engine = ScoringEngine(analysis, peer_summary, sentiment)
        self.scores = self.scoring_engine.calculate_total_score()

        # Generate theses
        self.thesis_gen = ThesisGenerator(analysis, peer_summary, sentiment, self.scores)

    def format_number(self, value: float, format_type: str = "number") -> str:
        """Format a number for display."""
        if value is None:
            return "N/A"

        if format_type == "currency":
            if abs(value) >= 1e12:
                return f"${value/1e12:.2f}T"
            elif abs(value) >= 1e9:
                return f"${value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                return f"${value/1e6:.2f}M"
            else:
                return f"${value:,.0f}"
        elif format_type == "percent":
            return f"{value:.1%}"
        elif format_type == "ratio":
            return f"{value:.2f}x"
        else:
            return f"{value:,.2f}"

    def generate_executive_summary(self) -> str:
        """Generate the executive summary section."""
        overview = self.data.get("overview", {})
        rec = self.scores["recommendation"]
        score = self.scores["total_score"]

        # Key stats table
        stats = [
            ["Current Price", self.format_number(overview.get("current_price"), "currency")],
            ["Market Cap", self.format_number(overview.get("market_cap"), "currency")],
            ["P/E (TTM)", self.format_number(self.analysis.get("valuation", {}).get("pe_trailing"), "ratio")],
            ["Revenue Growth", self.format_number(self.analysis.get("growth", {}).get("revenue_growth_1y"), "percent")],
            ["Net Margin", self.format_number(self.analysis.get("profitability", {}).get("net_margin"), "percent")],
            ["Investment Score", f"{score}/10"],
            ["Recommendation", rec],
        ]

        stats_table = tabulate(stats, tablefmt="pipe", headers=["Metric", "Value"])

        summary = f"""
# {self.ticker} Equity Research Report
## Executive Summary

**Company:** {overview.get('name', self.ticker)}
**Sector:** {overview.get('sector', 'N/A')} | **Industry:** {overview.get('industry', 'N/A')}

**Investment Recommendation: {rec}** (Score: {score}/10)

{stats_table}

*Report generated on {datetime.now().strftime('%B %d, %Y')}*

---
"""
        return summary

    def generate_company_overview(self) -> str:
        """Generate the company overview section."""
        overview = self.data.get("overview", {})

        section = f"""
## Company Overview

### Business Description

{overview.get('description', 'Business description not available.')}

### Key Facts

| Attribute | Value |
|-----------|-------|
| Headquarters | {overview.get('country', 'N/A')} |
| Employees | {overview.get('employees', 'N/A'):,} |
| Website | {overview.get('website', 'N/A')} |
| Market Cap | {self.format_number(overview.get('market_cap'), 'currency')} |
| Enterprise Value | {self.format_number(overview.get('enterprise_value'), 'currency')} |

### Price Performance

| Metric | Value |
|--------|-------|
| 52-Week High | {self.format_number(overview.get('fifty_two_week_high'), 'currency')} |
| 52-Week Low | {self.format_number(overview.get('fifty_two_week_low'), 'currency')} |
| % From 52W High | {self.format_number(overview.get('pct_from_52w_high'), 'percent')} |
| 50-Day MA | {self.format_number(overview.get('fifty_day_avg'), 'currency')} |
| 200-Day MA | {self.format_number(overview.get('two_hundred_day_avg'), 'currency')} |

---
"""
        return section

    def generate_financial_analysis(self) -> str:
        """Generate the financial analysis section."""
        val = self.analysis.get("valuation", {})
        prof = self.analysis.get("profitability", {})
        growth = self.analysis.get("growth", {})
        health = self.analysis.get("financial_health", {})

        section = f"""
## Financial Analysis

### Valuation Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| P/E (TTM) | {self.format_number(val.get('pe_trailing'), 'ratio')} | {'Premium' if (val.get('pe_trailing') or 0) > 25 else 'Fair' if (val.get('pe_trailing') or 0) > 15 else 'Value'} |
| P/E (Forward) | {self.format_number(val.get('pe_forward'), 'ratio')} | - |
| PEG Ratio | {self.format_number(val.get('peg_ratio'), 'ratio')} | {'Attractive' if (val.get('peg_ratio') or 99) < 1 else 'Fair' if (val.get('peg_ratio') or 99) < 2 else 'Expensive'} |
| P/B | {self.format_number(val.get('price_to_book'), 'ratio')} | - |
| P/S | {self.format_number(val.get('price_to_sales'), 'ratio')} | - |
| EV/EBITDA | {self.format_number(val.get('ev_to_ebitda'), 'ratio')} | - |
| P/FCF | {self.format_number(val.get('price_to_fcf'), 'ratio')} | - |

### Profitability Metrics

| Metric | Value |
|--------|-------|
| Gross Margin | {self.format_number(prof.get('gross_margin'), 'percent')} |
| Operating Margin | {self.format_number(prof.get('operating_margin'), 'percent')} |
| Net Margin | {self.format_number(prof.get('net_margin'), 'percent')} |
| ROE | {self.format_number(prof.get('roe'), 'percent')} |
| ROA | {self.format_number(prof.get('roa'), 'percent')} |
| ROIC | {self.format_number(prof.get('roic'), 'percent')} |

### Growth Metrics

| Metric | Value |
|--------|-------|
| Revenue Growth (YoY) | {self.format_number(growth.get('revenue_growth_1y'), 'percent')} |
| Revenue CAGR (3Y) | {self.format_number(growth.get('revenue_cagr_3y'), 'percent')} |
| EPS Growth (YoY) | {self.format_number(growth.get('eps_growth_1y'), 'percent')} |
| FCF Growth (YoY) | {self.format_number(growth.get('fcf_growth_1y'), 'percent')} |

### Financial Health

| Metric | Value | Assessment |
|--------|-------|------------|
| Current Ratio | {self.format_number(health.get('current_ratio'), 'ratio')} | {'Strong' if (health.get('current_ratio') or 0) > 1.5 else 'Adequate' if (health.get('current_ratio') or 0) > 1 else 'Weak'} |
| Debt/Equity | {self.format_number((health.get('debt_to_equity') or 0) / 100, 'ratio') if health.get('debt_to_equity') else 'N/A'} | {'Low' if (health.get('debt_to_equity') or 0) < 50 else 'Moderate' if (health.get('debt_to_equity') or 0) < 100 else 'High'} |
| Interest Coverage | {self.format_number(health.get('interest_coverage'), 'ratio')} | {'Strong' if (health.get('interest_coverage') or 0) > 5 else 'Adequate' if (health.get('interest_coverage') or 0) > 2 else 'Weak'} |
| Altman Z-Score | {self.format_number(health.get('altman_z_score'))} | {'Safe' if (health.get('altman_z_score') or 0) > 3 else 'Gray Zone' if (health.get('altman_z_score') or 0) > 1.8 else 'Distress'} |

---
"""
        return section

    def generate_peer_comparison(self) -> str:
        """Generate the peer comparison section."""
        comparison = self.peer_summary.get("formatted_comparison", pd.DataFrame())
        relative = self.peer_summary.get("relative_valuation", {})
        justification = self.peer_summary.get("valuation_justification", {})

        # Convert comparison DataFrame to markdown table
        if not comparison.empty:
            comp_table = comparison.to_markdown()
        else:
            comp_table = "Peer comparison data not available."

        section = f"""
## Peer Comparison

### Peers Analyzed
{', '.join(self.peer_summary.get('peers', ['N/A']))}

### Comparative Metrics

{comp_table}

### Relative Valuation Assessment

**Status:** {relative.get('assessment', 'N/A')}
**Detail:** {relative.get('assessment_detail', 'N/A')}

### Valuation Justification Analysis

**Conclusion:** {justification.get('conclusion', 'N/A')}

**Factors Supporting Valuation:**
"""
        for factor in justification.get("factors_supporting", []):
            section += f"\n- {factor}"

        section += "\n\n**Factors Against Valuation:**"
        for factor in justification.get("factors_against", []):
            section += f"\n- {factor}"

        section += "\n\n---\n"
        return section

    def generate_sentiment_analysis(self) -> str:
        """Generate the sentiment analysis section."""
        analyst = self.sentiment.get("analyst_recommendations", {})
        earnings = self.sentiment.get("earnings_history", {})
        momentum = self.sentiment.get("momentum", {})

        section = f"""
## Sentiment & Catalyst Analysis

### Analyst Recommendations

| Metric | Value |
|--------|-------|
| Consensus | {analyst.get('consensus', 'N/A')} |
| Total Analysts | {analyst.get('total_analysts', 'N/A')} |
| Mean Rating | {self.format_number(analyst.get('mean_rating'))} (1=Strong Buy, 5=Strong Sell) |

### Price Targets

| Metric | Value |
|--------|-------|
| Current Price | {self.format_number(analyst.get('price_targets', {}).get('current_price'), 'currency')} |
| Mean Target | {self.format_number(analyst.get('price_targets', {}).get('target_mean'), 'currency')} |
| Low Target | {self.format_number(analyst.get('price_targets', {}).get('target_low'), 'currency')} |
| High Target | {self.format_number(analyst.get('price_targets', {}).get('target_high'), 'currency')} |
| Implied Upside | {self.format_number(analyst.get('price_targets', {}).get('upside_pct'), 'percent') if analyst.get('price_targets', {}).get('upside_pct') else 'N/A'} |

### Earnings Performance

| Metric | Value |
|--------|-------|
| Quarters Analyzed | {earnings.get('quarters_analyzed', 'N/A')} |
| Beat Rate | {self.format_number(earnings.get('beat_rate'), 'percent') if earnings.get('beat_rate') is not None else 'N/A'} |
| Avg Surprise | {self.format_number((earnings.get('avg_surprise_pct') or 0) / 100, 'percent') if earnings.get('avg_surprise_pct') is not None else 'N/A'} |
| Trend | {earnings.get('trend', 'N/A')} |

### Technical Momentum

**Overall Assessment:** {momentum.get('overall_momentum', 'N/A')}
**Momentum Score:** {momentum.get('momentum_score', 'N/A')}/10

**Signals:**
"""
        for signal in momentum.get("technical_signals", []):
            section += f"\n- {signal}"

        section += f"""

### Overall Sentiment Score: {self.sentiment.get('overall_sentiment_score', 'N/A')}/10 ({self.sentiment.get('overall_sentiment', 'N/A')})

---
"""
        return section

    def generate_investment_thesis(self) -> str:
        """Generate the bull/bear case section."""
        bull_case = self.thesis_gen.generate_bull_case()
        bear_case = self.thesis_gen.generate_bear_case()
        key_metrics = self.thesis_gen.generate_key_metrics_to_monitor()

        section = """
## Investment Thesis

### Bull Case

"""
        for i, point in enumerate(bull_case, 1):
            section += f"{i}. {point}\n"

        section += """
### Bear Case

"""
        for i, point in enumerate(bear_case, 1):
            section += f"{i}. {point}\n"

        section += """
### Key Metrics to Monitor

"""
        for metric in key_metrics:
            section += f"- {metric}\n"

        section += "\n---\n"
        return section

    def generate_recommendation(self) -> str:
        """Generate the recommendation section."""
        categories = self.scores.get("categories", {})

        # Build scoring matrix
        score_table = [["Category", "Weight", "Score", "Weighted"]]
        for cat, data in categories.items():
            score_table.append([
                cat,
                f"{data['weight']:.0%}",
                f"{data['score']:.1f}",
                f"{data['weighted']:.2f}",
            ])

        score_table.append(["**TOTAL**", "100%", "", f"**{self.scores['total_score']:.1f}**"])

        table_str = tabulate(score_table, headers="firstrow", tablefmt="pipe")

        section = f"""
## Valuation & Recommendation

### Quantitative Scoring Matrix

{table_str}

### Final Recommendation: **{self.scores['recommendation']}**

#### Score Interpretation:
- **Strong Buy** (≥8.0): Compelling risk/reward, high conviction
- **Buy** (6.5-7.9): Favorable outlook, attractive entry point
- **Hold** (5.0-6.4): Fairly valued, maintain position
- **Sell** (3.5-4.9): Unfavorable risk/reward
- **Strong Sell** (<3.5): Significant downside risk

### Investment Commentary

"""
        # Generate nuanced commentary
        score = self.scores["total_score"]
        rec = self.scores["recommendation"]

        if score >= 7.5:
            commentary = f"""{self.ticker} presents a compelling investment opportunity with strong fundamentals
across multiple dimensions. The company demonstrates """
        elif score >= 6:
            commentary = f"""{self.ticker} offers an attractive risk/reward profile for investors seeking exposure
to the {self.analysis.get('sector', 'sector')}. While not without risks, the company shows """
        elif score >= 5:
            commentary = f"""{self.ticker} appears fairly valued at current levels. The company has """
        else:
            commentary = f"""{self.ticker} faces headwinds that warrant caution. Investors should consider """

        # Add specific strengths/weaknesses
        strengths = []
        weaknesses = []

        for cat, data in categories.items():
            if data["score"] >= 7:
                strengths.append(cat.lower())
            elif data["score"] < 4:
                weaknesses.append(cat.lower())

        if strengths:
            commentary += f"notable strengths in {', '.join(strengths)}. "
        if weaknesses:
            commentary += f"However, concerns remain around {', '.join(weaknesses)}. "

        # Add investor profile
        commentary += f"\n\n**Ideal Investor Profile:** "
        if score >= 7:
            commentary += "Growth-oriented investors with medium to high risk tolerance."
        elif score >= 5:
            commentary += "Balanced investors seeking core portfolio holdings."
        else:
            commentary += "Risk-averse investors may want to avoid or reduce exposure."

        # Add position sizing guidance
        commentary += f"\n\n**Position Sizing Consideration:** "
        if score >= 8:
            commentary += "High conviction - suitable for larger portfolio allocation (3-5%)."
        elif score >= 6.5:
            commentary += "Moderate conviction - consider standard position size (1-3%)."
        elif score >= 5:
            commentary += "Lower conviction - smaller position size warranted (0.5-1%)."
        else:
            commentary += "Low conviction - avoid or minimal position only."

        section += commentary

        section += "\n\n---\n"
        return section

    def generate_disclaimer(self) -> str:
        """Generate the disclaimer section."""
        return """
## Disclaimer

*This report is for informational purposes only and does not constitute financial advice,
investment recommendations, or an offer to buy or sell any securities. The analysis is based
on publicly available data from Yahoo Finance and may contain errors or inaccuracies.
Past performance is not indicative of future results. Always conduct your own research and
consult with a qualified financial advisor before making investment decisions.*

*Data source: Yahoo Finance (yfinance)*
*Report generated using automated analysis tools*
"""

    def generate_full_report(self) -> str:
        """Generate the complete equity research report."""
        report = ""

        report += self.generate_executive_summary()
        report += self.generate_company_overview()
        report += self.generate_financial_analysis()
        report += self.generate_peer_comparison()
        report += self.generate_sentiment_analysis()
        report += self.generate_investment_thesis()
        report += self.generate_recommendation()
        report += self.generate_disclaimer()

        return report

    def get_scores(self) -> Dict[str, Any]:
        """Get the scoring results."""
        return self.scores


if __name__ == "__main__":
    # Test the report generator
    from data_collector import DataCollector
    from financial_analysis import FinancialAnalyzer
    from peer_comparison import PeerComparison
    from sentiment_analysis import SentimentAnalyzer

    ticker = "NVDA"
    print(f"Testing report generation for {ticker}")

    # Collect data
    print("\nCollecting data...")
    collector = DataCollector(ticker)
    data = collector.get_all_data()

    # Financial analysis
    print("Running financial analysis...")
    analyzer = FinancialAnalyzer(data)
    analysis = analyzer.get_comprehensive_analysis()

    # Peer comparison
    print("Running peer comparison...")
    peer_comp = PeerComparison(ticker, data)
    peer_comp.identify_peers()
    peer_comp.collect_peer_data()
    peer_summary = peer_comp.get_peer_summary()

    # Sentiment analysis
    print("Running sentiment analysis...")
    sentiment_analyzer = SentimentAnalyzer(ticker, data)
    sentiment = sentiment_analyzer.get_sentiment_summary()

    # Generate report
    print("\nGenerating report...")
    report_gen = ReportGenerator(ticker, data, analysis, peer_summary, sentiment)
    report = report_gen.generate_full_report()

    # Save report
    with open(f"output/{ticker}_research_report.md", "w") as f:
        f.write(report)

    print(f"\nReport saved to output/{ticker}_research_report.md")
    print(f"\nRecommendation: {report_gen.scores['recommendation']}")
    print(f"Score: {report_gen.scores['total_score']}/10")
