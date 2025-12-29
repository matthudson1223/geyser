# Equity Research Report Generator

A comprehensive Python tool for generating institutional-quality equity research reports. Performs fundamental analysis, peer comparison, sentiment analysis, and produces professional investment recommendations.

## Features

- **Comprehensive Data Collection**: Fetches company data, historical prices, and financial statements via yfinance
- **Financial Analysis**: Calculates 40+ financial ratios across valuation, profitability, growth, and health metrics
- **Peer Comparison**: Automatically identifies and compares against industry peers
- **Sentiment Analysis**: Analyzes analyst recommendations, earnings history, and technical momentum
- **Interactive Visualizations**: Generates professional charts using Plotly
- **Automated Scoring**: Quantitative investment scoring system with weighted categories
- **Full Research Reports**: Produces markdown reports with executive summary, analysis, and recommendations

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd geyser

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Option 1: Command Line

```bash
# Analyze default ticker (NVDA)
python run_analysis.py

# Analyze any ticker
python run_analysis.py AAPL
python run_analysis.py MSFT
python run_analysis.py GOOGL
```

#### Option 2: Jupyter Notebook

Open `equity_research_report.ipynb` and change the `TICKER` variable in the first code cell:

```python
TICKER = "NVDA"  # Change this to any valid stock ticker
```

Then run all cells to generate the complete analysis.

#### Option 3: Python Script

```python
from run_analysis import run_analysis

# Run analysis for any ticker
results = run_analysis("AAPL")

# Access results
print(f"Recommendation: {results['scores']['recommendation']}")
print(f"Score: {results['scores']['total_score']}/10")
```

## Configuration

Edit `src/config.py` to customize:

- **Default ticker**: Change `TICKER = "NVDA"` to your preferred default
- **Peer mappings**: Add custom peer groups for specific tickers
- **Scoring weights**: Adjust category weights for the investment score
- **Analysis parameters**: Configure years of history, chart settings, etc.

## Output

The tool generates:

1. **Markdown Report** (`output/{TICKER}_research_report.md`)
   - Executive Summary
   - Company Overview
   - Financial Analysis
   - Peer Comparison
   - Sentiment Analysis
   - Bull/Bear Cases
   - Investment Recommendation

2. **Visualizations** (`output/charts/`)
   - Price chart with moving averages
   - Financial trends (Revenue, Net Income, FCF)
   - Margin analysis
   - Peer valuation comparison
   - Growth vs. Valuation scatter
   - Sentiment gauge
   - Score breakdown

## Scoring System

The investment score (1-10) is calculated from six weighted categories:

| Category | Weight |
|----------|--------|
| Valuation | 25% |
| Growth | 20% |
| Profitability | 20% |
| Financial Health | 15% |
| Momentum/Sentiment | 10% |
| Quality/Moat | 10% |

### Recommendation Thresholds

- **Strong Buy**: Score >= 8.0
- **Buy**: Score 6.5-7.9
- **Hold**: Score 5.0-6.4
- **Sell**: Score 3.5-4.9
- **Strong Sell**: Score < 3.5

## Project Structure

```
geyser/
├── run_analysis.py           # Main command-line entry point
├── equity_research_report.ipynb  # Interactive Jupyter notebook
├── requirements.txt          # Python dependencies
├── src/
│   ├── __init__.py
│   ├── config.py            # Configuration and settings
│   ├── data_collector.py    # Data fetching from yfinance
│   ├── financial_analysis.py # Financial ratio calculations
│   ├── peer_comparison.py   # Peer analysis
│   ├── sentiment_analysis.py # Sentiment and momentum
│   ├── visualizations.py    # Chart generation
│   └── report_generator.py  # Report assembly and scoring
└── output/
    ├── charts/              # Generated visualizations
    └── {TICKER}_research_report.md  # Generated reports
```

## Dependencies

- `yfinance`: Financial data API
- `pandas`: Data manipulation
- `numpy`: Numerical computations
- `matplotlib`: Static charts
- `plotly`: Interactive visualizations
- `kaleido`: Chart export
- `tabulate`: Table formatting
- `requests`, `beautifulsoup4`: Web scraping (optional)

## Supported Tickers

The tool works with any publicly traded stock available on Yahoo Finance:

- US stocks (AAPL, MSFT, GOOGL, AMZN, etc.)
- International stocks (with appropriate suffix: .L, .TO, .HK, etc.)
- ETFs (SPY, QQQ, etc.)

## Pre-configured Peer Groups

The tool includes predefined peer groups for major companies:

- **Tech/Semiconductors**: NVDA, AMD, INTC, QCOM, AVGO
- **Big Tech**: AAPL, MSFT, GOOGL, META, AMZN
- **Banks**: JPM, BAC, WFC, GS, MS
- **Pharma**: JNJ, PFE, MRK, LLY, ABBV
- **Retail**: WMT, COST, TGT, HD, LOW
- And more...

For tickers not in the mapping, peers are dynamically selected based on sector.

## Limitations

- Data sourced from Yahoo Finance (may have gaps or delays)
- Historical data typically limited to 5 years
- Peer comparison based on predefined or sector-based groupings
- Sentiment analysis limited to available yfinance data
- Charts require display environment (notebook or file export)

## Example Output

```
============================================================
  ANALYSIS COMPLETE: NVDA
============================================================

  Company: NVIDIA Corporation
  Sector: Technology
  Industry: Semiconductors

  Current Price: $XXX.XX
  Market Cap: $X.XT

  Investment Score: 7.5/10
  Recommendation: Buy

  Report: output/NVDA_research_report.md
============================================================
```

## Disclaimer

This tool is for informational and educational purposes only. It does not constitute financial advice, investment recommendations, or an offer to buy or sell securities. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.

## License

MIT License
