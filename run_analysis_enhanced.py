#!/usr/bin/env python3
"""
Enhanced Equity Research Report Generator with improved CLI.

Features:
- Environment configuration support
- Comprehensive logging
- Data caching with TTL
- Input validation
- Progress indicators
- Better error handling
- Multiple output formats
"""

import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from tqdm import tqdm
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration and infrastructure
from src.config_loader import load_config, get_config, TICKER, OUTPUT_DIR, CHARTS_DIR
from src.logger import init_logging, get_logger
from src.cache_manager import init_cache, get_cache
from src.validators import sanitize_ticker, validate_financial_data, ValidationError
from src.exceptions import DataCollectionError, AnalysisError, ReportGenerationError

# Import analysis modules
from src.data_collector import DataCollector
from src.financial_analysis import FinancialAnalyzer
from src.peer_comparison import PeerComparison
from src.sentiment_analysis import SentimentAnalyzer
from src.visualizations import ChartGenerator
from src.report_generator import ReportGenerator


def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Set up command-line argument parser.

    Returns:
        ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Generate comprehensive equity research reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s NVDA                    # Analyze NVIDIA
  %(prog)s AAPL --no-cache         # Analyze Apple without cache
  %(prog)s MSFT --config custom.yaml  # Use custom config
  %(prog)s GOOGL --log-level DEBUG    # Enable debug logging
  %(prog)s TSLA --no-charts        # Skip chart generation
  %(prog)s --clear-cache           # Clear cache and exit
        """,
    )

    parser.add_argument(
        "ticker",
        nargs="?",
        default=None,
        help=f"Stock ticker symbol (default: {TICKER})",
    )

    parser.add_argument(
        "--config",
        type=str,
        metavar="FILE",
        help="Path to YAML configuration file",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching (fetch fresh data)",
    )

    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all cached data and exit",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="Skip chart generation",
    )

    parser.add_argument(
        "--chart-format",
        choices=["html", "png", "svg"],
        default="html",
        help="Chart output format (default: html)",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        metavar="DIR",
        help=f"Output directory (default: {OUTPUT_DIR})",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output (equivalent to --log-level DEBUG)",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Quiet mode (minimal output)",
    )

    return parser


def print_banner():
    """Print application banner."""
    banner = f"""
{Fore.CYAN}{'=' * 60}
  GEYSER - Equity Research Report Generator
  Version 1.0.0
{'=' * 60}{Style.RESET_ALL}
    """
    print(banner)


def print_summary(results: Dict[str, Any]):
    """
    Print analysis summary.

    Args:
        results: Analysis results dictionary
    """
    ticker = results["ticker"]
    analysis = results["analysis"]
    scores = results["scores"]

    # Determine color based on recommendation
    rec = scores["recommendation"]
    if "Strong Buy" in rec or "Buy" in rec:
        rec_color = Fore.GREEN
    elif "Hold" in rec:
        rec_color = Fore.YELLOW
    else:
        rec_color = Fore.RED

    summary = f"""
{Fore.CYAN}{'=' * 60}
  ANALYSIS COMPLETE: {ticker}
{'=' * 60}{Style.RESET_ALL}

  Company: {analysis.get('company_name', 'N/A')}
  Sector: {analysis.get('sector', 'N/A')}
  Industry: {analysis.get('industry', 'N/A')}

  Current Price: ${analysis.get('current_price', 0):.2f}
  Market Cap: ${analysis.get('market_cap', 0) / 1e9:.2f}B

  {Fore.YELLOW}Investment Score: {scores['total_score']}/10{Style.RESET_ALL}
  {rec_color}Recommendation: {rec}{Style.RESET_ALL}

  Report: {results['report_path']}
  Charts: {CHARTS_DIR}/

{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}
    """
    print(summary)


def run_analysis(
    ticker: str,
    enable_cache: bool = True,
    save_charts: bool = True,
    chart_format: str = "html",
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run complete equity research analysis for a given ticker.

    Args:
        ticker: Stock ticker symbol
        enable_cache: Whether to use caching
        save_charts: Whether to save charts to files
        chart_format: Format for chart files (png, html, svg)
        output_dir: Custom output directory

    Returns:
        Dictionary containing all analysis results

    Raises:
        ValidationError: If ticker is invalid
        DataCollectionError: If data collection fails
        AnalysisError: If analysis fails
        ReportGenerationError: If report generation fails
    """
    logger = get_logger()

    # Validate and sanitize ticker
    try:
        ticker = sanitize_ticker(ticker)
    except ValidationError as e:
        logger.error(f"Invalid ticker: {e}")
        raise

    logger.info(f"Starting analysis for {ticker}")

    # Determine output directory
    final_output_dir = output_dir or OUTPUT_DIR
    charts_dir = os.path.join(final_output_dir, "charts")

    # Create output directories
    os.makedirs(final_output_dir, exist_ok=True)
    os.makedirs(charts_dir, exist_ok=True)

    # Initialize cache
    cache = get_cache()
    if not enable_cache:
        logger.info("Caching disabled - fetching fresh data")

    # Progress bar setup
    total_steps = 6
    progress = tqdm(total=total_steps, desc="Analysis Progress", unit="step")

    try:
        # Step 1: Data Collection
        progress.set_description("Collecting data from Yahoo Finance")
        collector = DataCollector(ticker)
        data = collector.get_all_data()
        progress.update(1)

        # Validate data quality
        warnings = validate_financial_data(data)
        for warning in warnings:
            logger.warning(f"Data quality issue: {warning}")

        # Step 2: Financial Analysis
        progress.set_description("Running financial analysis")
        analyzer = FinancialAnalyzer(data)
        analysis = analyzer.get_comprehensive_analysis()
        analysis["historical_prices"] = data.get("historical_prices")
        progress.update(1)

        # Step 3: Peer Comparison
        progress.set_description("Performing peer comparison")
        peer_comp = PeerComparison(ticker, data)
        peers = peer_comp.identify_peers()
        peer_comp.collect_peer_data()
        peer_summary = peer_comp.get_peer_summary()
        progress.update(1)

        # Step 4: Sentiment Analysis
        progress.set_description("Analyzing sentiment and momentum")
        sentiment_analyzer = SentimentAnalyzer(ticker, data)
        sentiment = sentiment_analyzer.get_sentiment_summary()
        progress.update(1)

        # Step 5: Generate Charts
        if save_charts:
            progress.set_description("Generating visualizations")
            chart_gen = ChartGenerator(ticker, charts_dir)

            charts = chart_gen.save_all_charts(
                analysis=analysis,
                peer_comparison=peer_summary.get("comparison_matrix"),
                sentiment=sentiment,
                scores=None,  # Will be set after report generation
                format=chart_format,
            )
            logger.info(f"Saved {len(charts)} charts to {charts_dir}/")
        progress.update(1)

        # Step 6: Generate Report
        progress.set_description("Generating research report")
        report_gen = ReportGenerator(ticker, data, analysis, peer_summary, sentiment)
        report = report_gen.generate_full_report()
        scores = report_gen.get_scores()

        # Save score chart
        if save_charts:
            score_fig = chart_gen.create_recommendation_score_chart(scores)
            if score_fig:
                score_path = os.path.join(
                    charts_dir, f"{ticker}_score_breakdown.{chart_format}"
                )
                if chart_format == "html":
                    score_fig.write_html(score_path)
                else:
                    score_fig.write_image(score_path, scale=2)

        # Save report
        report_path = os.path.join(final_output_dir, f"{ticker}_research_report.md")
        with open(report_path, "w") as f:
            f.write(report)
        logger.info(f"Report saved to: {report_path}")
        progress.update(1)

        progress.close()

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

    except Exception as e:
        progress.close()
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise


def main():
    """Main entry point for command-line usage."""
    parser = setup_argument_parser()
    args = parser.parse_args()

    # Print banner unless in quiet mode
    if not args.quiet:
        print_banner()

    # Determine log level
    log_level = "ERROR" if args.quiet else "DEBUG" if args.verbose else args.log_level

    # Load configuration
    config = load_config(args.config)

    # Initialize logging
    log_file = os.path.join(args.output_dir or OUTPUT_DIR, "analysis.log")
    init_logging(
        level=log_level,
        log_file=log_file,
        log_to_console=not args.quiet,
    )

    logger = get_logger()

    # Initialize cache
    cache_enabled = not args.no_cache
    init_cache(enabled=cache_enabled)

    # Handle cache clearing
    if args.clear_cache:
        logger.info("Clearing cache...")
        cache = get_cache()
        if cache.clear():
            print(f"{Fore.GREEN}✓ Cache cleared successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Failed to clear cache{Style.RESET_ALL}")
        return 0

    # Get ticker
    ticker = args.ticker or TICKER
    if not ticker:
        parser.print_help()
        return 1

    try:
        # Run analysis
        results = run_analysis(
            ticker=ticker,
            enable_cache=cache_enabled,
            save_charts=not args.no_charts,
            chart_format=args.chart_format,
            output_dir=args.output_dir,
        )

        # Print summary unless in quiet mode
        if not args.quiet:
            print_summary(results)

        return 0

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        print(f"{Fore.RED}✗ Invalid input: {e}{Style.RESET_ALL}")
        return 1

    except DataCollectionError as e:
        logger.error(f"Data collection error: {e}")
        print(f"{Fore.RED}✗ Failed to collect data: {e}{Style.RESET_ALL}")
        return 1

    except (AnalysisError, ReportGenerationError) as e:
        logger.error(f"Analysis error: {e}")
        print(f"{Fore.RED}✗ Analysis failed: {e}{Style.RESET_ALL}")
        return 1

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        print(f"\n{Fore.YELLOW}Analysis interrupted{Style.RESET_ALL}")
        return 130

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"{Fore.RED}✗ Unexpected error: {e}{Style.RESET_ALL}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
