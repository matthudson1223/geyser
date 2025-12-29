"""
Visualization Module for Equity Research Report Generator.

This module generates all charts and visualizations including:
- Price charts with moving averages
- Financial trend charts
- Margin analysis
- Peer comparison charts
- Sentiment gauges
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os


# Set matplotlib style
plt.style.use('seaborn-v0_8-whitegrid')

# Color scheme
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'positive': '#2ca02c',
    'negative': '#d62728',
    'neutral': '#7f7f7f',
    'accent1': '#9467bd',
    'accent2': '#8c564b',
    'accent3': '#e377c2',
    'background': '#f8f9fa',
    'grid': '#e0e0e0',
}


class ChartGenerator:
    """Generates charts and visualizations for equity research reports."""

    def __init__(self, ticker: str, output_dir: str = "output/charts"):
        """
        Initialize ChartGenerator.

        Args:
            ticker: Stock ticker symbol
            output_dir: Directory to save chart files
        """
        self.ticker = ticker.upper()
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def create_price_chart(self, history: pd.DataFrame, years: int = 2) -> go.Figure:
        """
        Create price chart with moving averages and volume.

        Args:
            history: Historical price DataFrame
            years: Number of years to display

        Returns:
            Plotly Figure object
        """
        if history.empty:
            return None

        # Filter for specified years
        # Handle timezone-aware indices
        cutoff = datetime.now() - timedelta(days=years * 365)
        if history.index.tz is not None:
            cutoff = pd.Timestamp(cutoff).tz_localize(history.index.tz)
        df = history[history.index >= cutoff].copy()

        if df.empty:
            df = history.copy()

        # Create subplot with secondary y-axis for volume
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.75, 0.25],
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(f'{self.ticker} Stock Price', 'Volume')
        )

        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color=COLORS['positive'],
                decreasing_line_color=COLORS['negative'],
            ),
            row=1, col=1
        )

        # 50-day Moving Average
        if 'MA_50' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MA_50'],
                    name='50-day MA',
                    line=dict(color=COLORS['primary'], width=1.5),
                ),
                row=1, col=1
            )

        # 200-day Moving Average
        if 'MA_200' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MA_200'],
                    name='200-day MA',
                    line=dict(color=COLORS['secondary'], width=1.5),
                ),
                row=1, col=1
            )

        # Volume bars
        colors = [COLORS['positive'] if df['Close'].iloc[i] >= df['Open'].iloc[i]
                  else COLORS['negative'] for i in range(len(df))]

        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7,
            ),
            row=2, col=1
        )

        # Update layout
        fig.update_layout(
            title=dict(
                text=f'{self.ticker} Price Chart ({years} Year)',
                font=dict(size=20)
            ),
            xaxis_rangeslider_visible=False,
            height=700,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            template='plotly_white',
        )

        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

        return fig

    def create_financial_trends_chart(self, growth_data: Dict[str, Any]) -> go.Figure:
        """
        Create multi-panel chart showing Revenue, Net Income, and FCF trends.

        Args:
            growth_data: Growth analysis data with historical values

        Returns:
            Plotly Figure object
        """
        # Extract historical data
        revenue_hist = growth_data.get("revenue_history", {"years": [], "values": []})
        ni_hist = growth_data.get("net_income_history", {"years": [], "values": []})
        fcf_hist = growth_data.get("fcf_history", {"years": [], "values": []})

        # Create subplots
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Revenue', 'Net Income', 'Free Cash Flow'),
            horizontal_spacing=0.1
        )

        # Revenue
        if revenue_hist["values"]:
            values = [v / 1e9 if v else 0 for v in revenue_hist["values"]]  # Convert to billions
            fig.add_trace(
                go.Bar(
                    x=revenue_hist["years"],
                    y=values,
                    name='Revenue',
                    marker_color=COLORS['primary'],
                    text=[f'${v:.1f}B' for v in values],
                    textposition='outside',
                ),
                row=1, col=1
            )

        # Net Income
        if ni_hist["values"]:
            values = [v / 1e9 if v else 0 for v in ni_hist["values"]]
            colors = [COLORS['positive'] if v >= 0 else COLORS['negative'] for v in values]
            fig.add_trace(
                go.Bar(
                    x=ni_hist["years"],
                    y=values,
                    name='Net Income',
                    marker_color=colors,
                    text=[f'${v:.1f}B' for v in values],
                    textposition='outside',
                ),
                row=1, col=2
            )

        # Free Cash Flow
        if fcf_hist["values"]:
            values = [v / 1e9 if v else 0 for v in fcf_hist["values"]]
            colors = [COLORS['positive'] if v >= 0 else COLORS['negative'] for v in values]
            fig.add_trace(
                go.Bar(
                    x=fcf_hist["years"],
                    y=values,
                    name='Free Cash Flow',
                    marker_color=colors,
                    text=[f'${v:.1f}B' for v in values],
                    textposition='outside',
                ),
                row=1, col=3
            )

        # Update layout
        fig.update_layout(
            title=dict(
                text=f'{self.ticker} Financial Trends ($ Billions)',
                font=dict(size=20)
            ),
            height=450,
            showlegend=False,
            template='plotly_white',
        )

        fig.update_yaxes(title_text="$ Billions", row=1, col=1)

        return fig

    def create_margin_analysis_chart(self, profitability: Dict[str, Any]) -> go.Figure:
        """
        Create line chart showing margin trends over time.

        Args:
            profitability: Profitability analysis data

        Returns:
            Plotly Figure object
        """
        trends = profitability.get("margin_trends", {})

        if not trends.get("years"):
            return None

        fig = go.Figure()

        # Gross Margin
        if trends.get("gross_margin"):
            values = [v * 100 if v else None for v in trends["gross_margin"]]
            fig.add_trace(
                go.Scatter(
                    x=trends["years"],
                    y=values,
                    name='Gross Margin',
                    mode='lines+markers',
                    line=dict(color=COLORS['primary'], width=3),
                    marker=dict(size=10),
                )
            )

        # Operating Margin
        if trends.get("operating_margin"):
            values = [v * 100 if v else None for v in trends["operating_margin"]]
            fig.add_trace(
                go.Scatter(
                    x=trends["years"],
                    y=values,
                    name='Operating Margin',
                    mode='lines+markers',
                    line=dict(color=COLORS['secondary'], width=3),
                    marker=dict(size=10),
                )
            )

        # Net Margin
        if trends.get("net_margin"):
            values = [v * 100 if v else None for v in trends["net_margin"]]
            fig.add_trace(
                go.Scatter(
                    x=trends["years"],
                    y=values,
                    name='Net Margin',
                    mode='lines+markers',
                    line=dict(color=COLORS['positive'], width=3),
                    marker=dict(size=10),
                )
            )

        fig.update_layout(
            title=dict(
                text=f'{self.ticker} Margin Analysis',
                font=dict(size=20)
            ),
            xaxis_title='Year',
            yaxis_title='Margin (%)',
            height=450,
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
        )

        return fig

    def create_peer_valuation_chart(self, comparison_df: pd.DataFrame) -> go.Figure:
        """
        Create bar chart comparing valuation metrics across peers.

        Args:
            comparison_df: DataFrame with peer comparison data

        Returns:
            Plotly Figure object
        """
        metrics = ['P/E (TTM)', 'EV/EBITDA', 'P/S', 'P/B']
        available_metrics = [m for m in metrics if m in comparison_df.index]

        if not available_metrics:
            return None

        # Get companies (columns)
        companies = [c for c in comparison_df.columns if c != 'Peer Avg']

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=available_metrics[:4],
            horizontal_spacing=0.15,
            vertical_spacing=0.2
        )

        for i, metric in enumerate(available_metrics[:4]):
            row = i // 2 + 1
            col = i % 2 + 1

            values = []
            for company in companies:
                val = comparison_df.loc[metric, company]
                if pd.notna(val) and isinstance(val, (int, float)):
                    values.append(val)
                else:
                    values.append(0)

            # Color the target company differently
            colors = [COLORS['primary'] if c == self.ticker else COLORS['neutral']
                     for c in companies]

            fig.add_trace(
                go.Bar(
                    x=companies,
                    y=values,
                    name=metric,
                    marker_color=colors,
                    showlegend=False,
                ),
                row=row, col=col
            )

        fig.update_layout(
            title=dict(
                text=f'{self.ticker} vs Peers - Valuation Comparison',
                font=dict(size=20)
            ),
            height=600,
            template='plotly_white',
        )

        return fig

    def create_growth_vs_valuation_scatter(self, comparison_df: pd.DataFrame) -> go.Figure:
        """
        Create scatter plot of growth vs valuation for peer comparison.

        Args:
            comparison_df: DataFrame with peer comparison data

        Returns:
            Plotly Figure object
        """
        if 'Revenue Growth' not in comparison_df.index or 'P/E (TTM)' not in comparison_df.index:
            return None

        companies = [c for c in comparison_df.columns if c != 'Peer Avg']

        growth_values = []
        pe_values = []
        valid_companies = []

        for company in companies:
            growth = comparison_df.loc['Revenue Growth', company]
            pe = comparison_df.loc['P/E (TTM)', company]

            if pd.notna(growth) and pd.notna(pe) and isinstance(growth, (int, float)) and isinstance(pe, (int, float)):
                growth_values.append(growth * 100)  # Convert to percentage
                pe_values.append(pe)
                valid_companies.append(company)

        if len(valid_companies) < 2:
            return None

        # Create colors - highlight the target company
        colors = [COLORS['primary'] if c == self.ticker else COLORS['neutral']
                 for c in valid_companies]
        sizes = [20 if c == self.ticker else 12 for c in valid_companies]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=growth_values,
                y=pe_values,
                mode='markers+text',
                text=valid_companies,
                textposition='top center',
                marker=dict(
                    size=sizes,
                    color=colors,
                    line=dict(width=2, color='white')
                ),
                name='Companies',
            )
        )

        # Add quadrant lines (at median values)
        median_growth = np.median(growth_values)
        median_pe = np.median(pe_values)

        fig.add_hline(y=median_pe, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=median_growth, line_dash="dash", line_color="gray", opacity=0.5)

        # Add quadrant labels
        fig.add_annotation(x=max(growth_values)*0.9, y=max(pe_values)*0.9,
                          text="High Growth\nHigh Valuation", showarrow=False,
                          font=dict(size=10, color="gray"))
        fig.add_annotation(x=min(growth_values)*1.1, y=max(pe_values)*0.9,
                          text="Low Growth\nHigh Valuation", showarrow=False,
                          font=dict(size=10, color="gray"))
        fig.add_annotation(x=max(growth_values)*0.9, y=min(pe_values)*1.1,
                          text="High Growth\nLow Valuation", showarrow=False,
                          font=dict(size=10, color="gray"))
        fig.add_annotation(x=min(growth_values)*1.1, y=min(pe_values)*1.1,
                          text="Low Growth\nLow Valuation", showarrow=False,
                          font=dict(size=10, color="gray"))

        fig.update_layout(
            title=dict(
                text=f'Growth vs Valuation - {self.ticker} vs Peers',
                font=dict(size=20)
            ),
            xaxis_title='Revenue Growth (%)',
            yaxis_title='P/E Ratio',
            height=500,
            template='plotly_white',
        )

        return fig

    def create_sentiment_gauge(self, sentiment_score: float, sentiment_label: str) -> go.Figure:
        """
        Create a gauge chart for overall sentiment.

        Args:
            sentiment_score: Score from 1-10
            sentiment_label: Sentiment label (e.g., "Bullish")

        Returns:
            Plotly Figure object
        """
        # Determine color based on score
        if sentiment_score >= 7:
            color = COLORS['positive']
        elif sentiment_score >= 4:
            color = COLORS['secondary']
        else:
            color = COLORS['negative']

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sentiment_score,
            title={'text': f"{self.ticker} Sentiment Score", 'font': {'size': 20}},
            delta={'reference': 5, 'increasing': {'color': COLORS['positive']},
                   'decreasing': {'color': COLORS['negative']}},
            gauge={
                'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "darkgray"},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 3.5], 'color': '#ffcccc'},
                    {'range': [3.5, 5], 'color': '#ffe0cc'},
                    {'range': [5, 6.5], 'color': '#fff2cc'},
                    {'range': [6.5, 8], 'color': '#d9f2d9'},
                    {'range': [8, 10], 'color': '#b3e6b3'},
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': sentiment_score
                }
            }
        ))

        fig.add_annotation(
            x=0.5, y=0.25,
            text=sentiment_label,
            showarrow=False,
            font=dict(size=24, color=color, family="Arial Black"),
        )

        fig.update_layout(
            height=350,
            template='plotly_white',
        )

        return fig

    def create_recommendation_score_chart(self, scores: Dict[str, Any]) -> go.Figure:
        """
        Create horizontal bar chart for recommendation scoring matrix.

        Args:
            scores: Dictionary with scoring matrix data

        Returns:
            Plotly Figure object
        """
        categories = list(scores.get("categories", {}).keys())
        weights = [scores["categories"][c]["weight"] * 100 for c in categories]
        values = [scores["categories"][c]["score"] for c in categories]
        weighted = [scores["categories"][c]["weighted"] for c in categories]

        # Create figure with dual bars
        fig = go.Figure()

        # Score bars
        fig.add_trace(
            go.Bar(
                y=categories,
                x=values,
                name='Score',
                orientation='h',
                marker_color=COLORS['primary'],
                text=[f'{v:.1f}' for v in values],
                textposition='inside',
            )
        )

        fig.update_layout(
            title=dict(
                text=f'{self.ticker} Investment Score Breakdown',
                font=dict(size=20)
            ),
            xaxis_title='Score (out of 10)',
            yaxis_title='Category',
            height=400,
            template='plotly_white',
            xaxis=dict(range=[0, 10]),
            showlegend=False,
        )

        # Add total score annotation
        total = scores.get("total_score", 0)
        fig.add_annotation(
            x=5, y=-0.3,
            xref="x", yref="paper",
            text=f"Total Score: {total:.1f}/10",
            showarrow=False,
            font=dict(size=18, color=COLORS['primary'], family="Arial Black"),
        )

        return fig

    def save_all_charts(self, analysis: Dict[str, Any], peer_comparison: pd.DataFrame,
                       sentiment: Dict[str, Any], scores: Dict[str, Any],
                       format: str = "png") -> Dict[str, str]:
        """
        Generate and save all charts for the report.

        Args:
            analysis: Financial analysis data
            peer_comparison: Peer comparison DataFrame
            sentiment: Sentiment analysis data
            scores: Scoring matrix data
            format: Output format (png, html, svg)

        Returns:
            Dictionary mapping chart names to file paths
        """
        saved_charts = {}

        # 1. Price Chart
        history = analysis.get("historical_prices", pd.DataFrame())
        if not history.empty:
            fig = self.create_price_chart(history)
            if fig:
                path = os.path.join(self.output_dir, f"{self.ticker}_price_chart.{format}")
                if format == "html":
                    fig.write_html(path)
                else:
                    fig.write_image(path, scale=2)
                saved_charts["price_chart"] = path

        # 2. Financial Trends
        growth = analysis.get("growth", {})
        if growth:
            fig = self.create_financial_trends_chart(growth)
            if fig:
                path = os.path.join(self.output_dir, f"{self.ticker}_financial_trends.{format}")
                if format == "html":
                    fig.write_html(path)
                else:
                    fig.write_image(path, scale=2)
                saved_charts["financial_trends"] = path

        # 3. Margin Analysis
        profitability = analysis.get("profitability", {})
        if profitability:
            fig = self.create_margin_analysis_chart(profitability)
            if fig:
                path = os.path.join(self.output_dir, f"{self.ticker}_margin_analysis.{format}")
                if format == "html":
                    fig.write_html(path)
                else:
                    fig.write_image(path, scale=2)
                saved_charts["margin_analysis"] = path

        # 4. Peer Valuation Comparison
        if peer_comparison is not None and not peer_comparison.empty:
            fig = self.create_peer_valuation_chart(peer_comparison)
            if fig:
                path = os.path.join(self.output_dir, f"{self.ticker}_peer_valuation.{format}")
                if format == "html":
                    fig.write_html(path)
                else:
                    fig.write_image(path, scale=2)
                saved_charts["peer_valuation"] = path

            # 5. Growth vs Valuation Scatter
            fig = self.create_growth_vs_valuation_scatter(peer_comparison)
            if fig:
                path = os.path.join(self.output_dir, f"{self.ticker}_growth_vs_valuation.{format}")
                if format == "html":
                    fig.write_html(path)
                else:
                    fig.write_image(path, scale=2)
                saved_charts["growth_vs_valuation"] = path

        # 6. Sentiment Gauge
        if sentiment:
            fig = self.create_sentiment_gauge(
                sentiment.get("overall_sentiment_score", 5),
                sentiment.get("overall_sentiment", "Neutral")
            )
            if fig:
                path = os.path.join(self.output_dir, f"{self.ticker}_sentiment_gauge.{format}")
                if format == "html":
                    fig.write_html(path)
                else:
                    fig.write_image(path, scale=2)
                saved_charts["sentiment_gauge"] = path

        # 7. Recommendation Score
        if scores:
            fig = self.create_recommendation_score_chart(scores)
            if fig:
                path = os.path.join(self.output_dir, f"{self.ticker}_score_breakdown.{format}")
                if format == "html":
                    fig.write_html(path)
                else:
                    fig.write_image(path, scale=2)
                saved_charts["score_breakdown"] = path

        return saved_charts


if __name__ == "__main__":
    # Test the chart generator
    from data_collector import DataCollector
    from financial_analysis import FinancialAnalyzer

    ticker = "NVDA"
    print(f"Testing chart generation for {ticker}")

    collector = DataCollector(ticker)
    data = collector.get_all_data()

    analyzer = FinancialAnalyzer(data)
    analysis = analyzer.get_comprehensive_analysis()

    chart_gen = ChartGenerator(ticker)

    # Test price chart
    print("Creating price chart...")
    fig = chart_gen.create_price_chart(data["historical_prices"])
    if fig:
        fig.write_html("output/charts/test_price_chart.html")
        print("  Saved: output/charts/test_price_chart.html")

    # Test financial trends
    print("Creating financial trends chart...")
    fig = chart_gen.create_financial_trends_chart(analysis["growth"])
    if fig:
        fig.write_html("output/charts/test_financial_trends.html")
        print("  Saved: output/charts/test_financial_trends.html")

    # Test margin analysis
    print("Creating margin analysis chart...")
    fig = chart_gen.create_margin_analysis_chart(analysis["profitability"])
    if fig:
        fig.write_html("output/charts/test_margin_analysis.html")
        print("  Saved: output/charts/test_margin_analysis.html")

    # Test sentiment gauge
    print("Creating sentiment gauge...")
    fig = chart_gen.create_sentiment_gauge(7.5, "Bullish")
    if fig:
        fig.write_html("output/charts/test_sentiment_gauge.html")
        print("  Saved: output/charts/test_sentiment_gauge.html")

    print("\nAll test charts created successfully!")
