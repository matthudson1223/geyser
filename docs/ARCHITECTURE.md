# Architecture Overview

## System Design

Geyser is designed as a modular Python application for generating comprehensive equity research reports.

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                     User Interface                       │
│                  (CLI / run_analysis.py)                 │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────┼──────────┐
          │          │          │
┌─────────▼────┐  ┌──▼────────┐  ┌──▼──────────┐
│Config Loader │  │  Logger   │  │ Cache Mgr   │
└──────────────┘  └───────────┘  └─────────────┘
          │          │          │
          └──────────┼──────────┘
                     │
          ┌──────────▼──────────┐
          │  Data Collector     │
          │  (yfinance API)     │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────────────────┐
          │                                  │
    ┌─────▼──────┐  ┌─────▼─────────┐  ┌───▼──────────┐
    │ Financial  │  │     Peer      │  │  Sentiment   │
    │  Analysis  │  │  Comparison   │  │   Analysis   │
    └─────┬──────┘  └─────┬─────────┘  └───┬──────────┘
          │                │                 │
          └────────────────┼─────────────────┘
                           │
                  ┌────────▼──────────┐
                  │ Report Generator  │
                  │  (Scoring Engine) │
                  └────────┬──────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼────┐  ┌────▼────┐  ┌───▼──────┐
        │Visualiz. │  │ Markdown│  │   PDF    │
        │  (Charts)│  │ Report  │  │ (Future) │
        └──────────┘  └─────────┘  └──────────┘
```

## Module Descriptions

### 1. Configuration Layer

- **config_loader.py**: Manages configuration from environment variables, YAML files, and defaults
- **Supports**: Hot-reloading, environment-specific configs, validation

### 2. Infrastructure Layer

- **logger.py**: Centralized logging with colored console output and file logging
- **cache_manager.py**: Disk-based caching with TTL support for API responses
- **validators.py**: Input validation and data sanitization
- **exceptions.py**: Custom exception hierarchy

### 3. Data Layer

- **data_collector.py**: Fetches data from Yahoo Finance API
  - Company overview
  - Historical prices
  - Financial statements
  - Analyst data
  - Institutional holdings

### 4. Analysis Layer

- **financial_analysis.py**: Calculates 40+ financial ratios
  - Valuation metrics
  - Profitability ratios
  - Growth rates
  - Financial health indicators

- **peer_comparison.py**: Comparative analysis
  - Identifies industry peers
  - Benchmarking
  - Relative valuation

- **sentiment_analysis.py**: Market sentiment analysis
  - Analyst recommendations
  - Earnings history
  - Technical momentum

### 5. Report Generation Layer

- **report_generator.py**: Assembles final report
  - Scoring engine (weighted categories)
  - Bull/bear case generation
  - Recommendation logic

- **visualizations.py**: Creates interactive charts
  - Price charts with moving averages
  - Financial trends
  - Peer comparison visualizations

## Data Flow

1. **Input**: User provides ticker symbol via CLI
2. **Validation**: Ticker format validated and sanitized
3. **Cache Check**: System checks if recent data exists in cache
4. **Data Collection**: Fresh data fetched from yfinance if needed
5. **Analysis Pipeline**:
   - Financial ratios calculated
   - Peers identified and analyzed
   - Sentiment metrics computed
6. **Scoring**: Quantitative scoring across 6 dimensions
7. **Report Generation**: Markdown report assembled
8. **Visualization**: Charts generated and saved
9. **Output**: Report and charts saved to output directory

## Caching Strategy

- **Company Info**: 24 hours TTL
- **Historical Prices**: 1 hour TTL
- **Financial Statements**: 24 hours TTL
- **Computed Ratios**: Session-based (in-memory)

## Error Handling

- Graceful degradation: Missing data doesn't crash analysis
- Comprehensive logging of warnings and errors
- User-friendly error messages
- Retry logic for transient API failures

## Performance Optimizations

- Parallel peer data fetching (ThreadPoolExecutor)
- DataFrame operations optimized with NumPy vectorization
- Lazy loading of heavy computations
- Disk cache reduces redundant API calls

## Security Considerations

- Input validation prevents injection attacks
- No sensitive data stored in code
- API keys managed via environment variables
- Secure file path handling

## Extensibility

The modular design allows easy addition of:
- New data sources (Alpha Vantage, Financial Modeling Prep)
- Additional analysis modules
- Alternative output formats (PDF, HTML, JSON)
- Custom scoring algorithms
- REST API wrapper
