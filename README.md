# Geyser - Equity Research Report Generator

[![CI](https://github.com/matthudson1223/geyser/workflows/CI/badge.svg)](https://github.com/matthudson1223/geyser/actions)
[![codecov](https://codecov.io/gh/matthudson1223/geyser/branch/main/graph/badge.svg)](https://codecov.io/gh/matthudson1223/geyser)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive, production-ready Python tool for generating institutional-quality equity research reports. Performs fundamental analysis, peer comparison, sentiment analysis, and produces professional investment recommendations.

## ✨ Features

### Core Analysis
- **Comprehensive Data Collection**: Fetches company data, historical prices, and financial statements via yfinance
- **Financial Analysis**: Calculates 40+ financial ratios across valuation, profitability, growth, and health metrics
- **Peer Comparison**: Automatically identifies and compares against industry peers
- **Sentiment Analysis**: Analyzes analyst recommendations, earnings history, and technical momentum
- **Interactive Visualizations**: Generates professional charts using Plotly
- **Automated Scoring**: Quantitative investment scoring system with weighted categories
- **Full Research Reports**: Produces markdown reports with executive summary, analysis, and recommendations

### New in v1.0.0 🎉
- **🔧 Environment Configuration**: Support for `.env` files and YAML configuration
- **📝 Comprehensive Logging**: Colored console output and file logging with multiple levels
- **💾 Intelligent Caching**: Disk-based caching with TTL for improved performance
- **✅ Input Validation**: Robust validation and sanitization of all inputs
- **🧪 Test Coverage**: Comprehensive test suite with pytest (80%+ coverage)
- **🚀 CI/CD Pipeline**: Automated testing, linting, and security scanning
- **📊 Progress Indicators**: Real-time progress bars for long-running operations
- **🎨 Enhanced CLI**: Advanced command-line interface with argparse
- **⚡ Performance**: Parallel peer data fetching for faster analysis
- **🔒 Security**: Input validation, security scanning, and best practices

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/matthudson1223/geyser.git
cd geyser

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### Basic Usage

#### Enhanced CLI (Recommended)

```bash
# Analyze default ticker with progress bars
python run_analysis_enhanced.py NVDA

# Analyze with custom options
python run_analysis_enhanced.py AAPL --no-cache --log-level DEBUG

# Get help
python run_analysis_enhanced.py --help

# Clear cache
python run_analysis_enhanced.py --clear-cache
```

#### Original CLI

```bash
# Analyze default ticker (NVDA)
python run_analysis.py

# Analyze any ticker
python run_analysis.py AAPL
```

#### Using Makefile

```bash
# Run with default ticker
make run

# Run tests
make test

# Format code
make format

# Run all checks
make check
```

#### Jupyter Notebook

Open `equity_research_report.ipynb` and change the `TICKER` variable:

```python
TICKER = "NVDA"  # Change this to any valid stock ticker
```

#### Option 3: Python Script

```python
from run_analysis import run_analysis

# Run analysis for any ticker
results = run_analysis("AAPL")

# Access results
print(f"Recommendation: {results['scores']['recommendation']}")
print(f"Score: {results['scores']['total_score']}/10")
```

## ⚙️ Configuration

Geyser supports multiple configuration methods with priority: Environment Variables > YAML Config > Defaults

### Environment Variables (.env)

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Default settings
DEFAULT_TICKER=NVDA
CACHE_ENABLED=true
CACHE_TTL_HOURS=24
LOG_LEVEL=INFO

# Customize analysis parameters
YEARS_OF_HISTORY=5
CHART_PRICE_YEARS=2
```

### YAML Configuration

Create a `config.yaml` file for advanced configuration:

```yaml
default_ticker: AAPL
cache_enabled: true
cache_ttl_hours: 12
log_level: DEBUG
parallel_peer_fetch: true
max_workers: 10
```

Then run with:
```bash
python run_analysis_enhanced.py --config config.yaml
```

### Legacy Configuration

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

## 🧪 Development

### Setup Development Environment

```bash
# Clone and enter directory
git clone https://github.com/matthudson1223/geyser.git
cd geyser

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install all dependencies
make install-dev

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests with coverage
make test

# Run specific test file
pytest tests/test_validators.py -v

# Run tests in watch mode
pytest-watch
```

### Code Quality

```bash
# Format code
make format

# Run linters
make lint

# Run all checks
make check

# Security scanning
make security
```

### Project Structure

```
geyser/
├── src/                          # Source code
│   ├── cache_manager.py         # Caching system
│   ├── config_loader.py         # Configuration management
│   ├── data_collector.py        # Data fetching
│   ├── exceptions.py            # Custom exceptions
│   ├── financial_analysis.py    # Financial metrics
│   ├── logger.py                # Logging setup
│   ├── peer_comparison.py       # Peer analysis
│   ├── report_generator.py      # Report generation
│   ├── sentiment_analysis.py    # Sentiment scoring
│   ├── validators.py            # Input validation
│   └── visualizations.py        # Chart generation
├── tests/                        # Test suite
├── docs/                         # Documentation
├── .github/workflows/            # CI/CD pipelines
├── run_analysis.py              # Original CLI
├── run_analysis_enhanced.py     # Enhanced CLI
└── Makefile                      # Development tasks
```

## 📚 Documentation

- **[Architecture Overview](docs/ARCHITECTURE.md)**: System design and component descriptions
- **[Contributing Guide](docs/CONTRIBUTING.md)**: How to contribute to the project
- **[Security Policy](SECURITY.md)**: Security guidelines and reporting
- **[Changelog](CHANGELOG.md)**: Version history and changes

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

Quick contribution steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for informational and educational purposes only. It does not constitute financial advice, investment recommendations, or an offer to buy or sell securities. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.

## 🙏 Acknowledgments

- Data provided by [Yahoo Finance](https://finance.yahoo.com/) via the `yfinance` library
- Built with Python, pandas, NumPy, Plotly, and other amazing open-source tools

## 📬 Support

- **Issues**: [GitHub Issues](https://github.com/matthudson1223/geyser/issues)
- **Discussions**: [GitHub Discussions](https://github.com/matthudson1223/geyser/discussions)

---

**Made with ❤️ by the Geyser community**
