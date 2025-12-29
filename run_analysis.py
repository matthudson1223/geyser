#!/usr/bin/env python3
"""
Equity Research Report Generator

Usage:
    python run_analysis.py [TICKER]

If no ticker is provided, uses the default from config.py (NVDA).

Examples:
    python run_analysis.py           # Analyzes NVDA (default)
    python run_analysis.py AAPL      # Analyzes Apple
    python run_analysis.py MSFT      # Analyzes Microsoft
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import TICKER, OUTPUT_DIR, CHARTS_DIR
from src.data_collector import DataCollector
from src.financial_analysis import FinancialAnalyzer
from src.peer_comparison import PeerComparison
from src.sentiment_analysis import SentimentAnalyzer
from src.visualizations import ChartGenerator
from src.report_generator import ReportGenerator


def run_analysis(ticker: str = None, save_charts: bool = True, chart_format: str = "html"):
    """
    Run complete equity research analysis for a given ticker.

    Args:
        ticker: Stock ticker symbol (uses config default if None)
        save_charts: Whether to save charts to files
        chart_format: Format for chart files (png, html, svg)

    Returns:
        Dictionary containing all analysis results
    """
    # Use provided ticker or default from config
    ticker = (ticker or TICKER).upper()

    print("=" * 60)
    print(f"  EQUITY RESEARCH REPORT: {ticker}")
    print("=" * 60)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create output directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CHARTS_DIR, exist_ok=True)

    # Step 1: Data Collection
    print("\n[1/6] Collecting data from Yahoo Finance...")
    collector = DataCollector(ticker)
    data = collector.get_all_data()

    # Step 2: Financial Analysis
    print("\n[2/6] Running financial analysis...")
    analyzer = FinancialAnalyzer(data)
    analysis = analyzer.get_comprehensive_analysis()
    analysis["historical_prices"] = data.get("historical_prices")

    # Step 3: Peer Comparison
    print("\n[3/6] Performing peer comparison...")
    peer_comp = PeerComparison(ticker, data)
    peers = peer_comp.identify_peers()
    peer_comp.collect_peer_data()
    peer_summary = peer_comp.get_peer_summary()

    # Step 4: Sentiment Analysis
    print("\n[4/6] Analyzing sentiment and momentum...")
    sentiment_analyzer = SentimentAnalyzer(ticker, data)
    sentiment = sentiment_analyzer.get_sentiment_summary()

    # Step 5: Generate Charts
    print("\n[5/6] Generating visualizations...")
    chart_gen = ChartGenerator(ticker, CHARTS_DIR)

    if save_charts:
        charts = chart_gen.save_all_charts(
            analysis=analysis,
            peer_comparison=peer_summary.get("comparison_matrix"),
            sentiment=sentiment,
            scores=None,  # Will be set after report generation
            format=chart_format
        )
        print(f"  Saved {len(charts)} charts to {CHARTS_DIR}/")

    # Step 6: Generate Report
    print("\n[6/6] Generating research report...")
    report_gen = ReportGenerator(ticker, data, analysis, peer_summary, sentiment)
    report = report_gen.generate_full_report()
    scores = report_gen.get_scores()

    # Save score chart
    if save_charts:
        score_fig = chart_gen.create_recommendation_score_chart(scores)
        if score_fig:
            score_path = os.path.join(CHARTS_DIR, f"{ticker}_score_breakdown.{chart_format}")
            if chart_format == "html":
                score_fig.write_html(score_path)
            else:
                score_fig.write_image(score_path, scale=2)

    # Save report
    report_path = os.path.join(OUTPUT_DIR, f"{ticker}_research_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\n  Report saved to: {report_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("  ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\n  Ticker: {ticker}")
    print(f"  Company: {analysis.get('company_name', 'N/A')}")
    print(f"  Sector: {analysis.get('sector', 'N/A')}")
    print(f"\n  Investment Score: {scores['total_score']}/10")
    print(f"  Recommendation: {scores['recommendation']}")
    print(f"\n  Report: {report_path}")
    print(f"  Charts: {CHARTS_DIR}/")
    print("\n" + "=" * 60)

    return {
        "ticker": ticker,
        "data": data,
        "analysis": analysis,
        "peer_summary": peer_summary,
        "sentiment": sentiment,
        "scores": scores,
        "report": report,
        "report_path": report_path,
    }


def main():
    """Main entry point for command-line usage."""
    # Get ticker from command line or use default
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
    else:
        ticker = TICKER
        print(f"No ticker provided. Using default: {ticker}")
        print(f"Usage: python {sys.argv[0]} [TICKER]")

    try:
        results = run_analysis(ticker)
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
