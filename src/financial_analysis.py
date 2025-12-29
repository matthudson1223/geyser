"""
Financial Analysis Module for Equity Research Report Generator.

This module calculates comprehensive financial ratios and metrics including:
- Valuation ratios
- Profitability metrics
- Growth rates
- Financial health indicators
- Efficiency ratios
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime


class FinancialAnalyzer:
    """Performs comprehensive financial analysis on company data."""

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize FinancialAnalyzer with collected company data.

        Args:
            data: Dictionary containing all collected financial data
        """
        self.data = data
        self.ticker = data.get("ticker", "Unknown")
        self.overview = data.get("overview", {})
        self.stats = data.get("key_statistics", {})
        self.income_annual = data.get("income_statement_annual", pd.DataFrame())
        self.income_quarterly = data.get("income_statement_quarterly", pd.DataFrame())
        self.balance_annual = data.get("balance_sheet_annual", pd.DataFrame())
        self.balance_quarterly = data.get("balance_sheet_quarterly", pd.DataFrame())
        self.cashflow_annual = data.get("cash_flow_annual", pd.DataFrame())
        self.cashflow_quarterly = data.get("cash_flow_quarterly", pd.DataFrame())
        self.return_metrics = data.get("return_metrics", {})

    def _safe_get(self, df: pd.DataFrame, row: str, col_idx: int = 0) -> Optional[float]:
        """Safely get a value from a DataFrame."""
        try:
            if df.empty or row not in df.index:
                return None
            if col_idx >= len(df.columns):
                return None
            value = df.loc[row].iloc[col_idx]
            return float(value) if pd.notna(value) else None
        except Exception:
            return None

    def _safe_divide(self, numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
        """Safely divide two numbers."""
        if numerator is None or denominator is None or denominator == 0:
            return None
        return numerator / denominator

    def calculate_valuation_ratios(self) -> Dict[str, Any]:
        """
        Calculate valuation ratios.

        Returns:
            Dictionary of valuation metrics
        """
        price = self.overview.get("current_price")
        market_cap = self.overview.get("market_cap")
        enterprise_value = self.overview.get("enterprise_value")

        # Get from yfinance stats first, then calculate if missing
        valuation = {
            "pe_trailing": self.stats.get("pe_trailing"),
            "pe_forward": self.stats.get("pe_forward"),
            "peg_ratio": self.stats.get("peg_ratio"),
            "price_to_book": self.stats.get("price_to_book"),
            "price_to_sales": self.stats.get("price_to_sales"),
            "ev_to_ebitda": self.stats.get("ev_to_ebitda"),
            "ev_to_revenue": self.stats.get("ev_to_revenue"),
        }

        # Calculate P/FCF if we have the data
        fcf = self.stats.get("free_cash_flow")
        if market_cap and fcf and fcf > 0:
            valuation["price_to_fcf"] = market_cap / fcf

        # Get TTM earnings
        eps = self.stats.get("eps_trailing")
        if price and eps and eps > 0 and valuation["pe_trailing"] is None:
            valuation["pe_trailing"] = price / eps

        # Calculate EV/Sales if missing
        revenue = self._safe_get(self.income_annual, "Total Revenue", 0)
        if enterprise_value and revenue and valuation["ev_to_revenue"] is None:
            valuation["ev_to_revenue"] = enterprise_value / revenue

        # Calculate dividend yield
        valuation["dividend_yield"] = self.overview.get("dividend_yield")

        # Earnings yield (inverse of P/E)
        if valuation["pe_trailing"] and valuation["pe_trailing"] > 0:
            valuation["earnings_yield"] = 1 / valuation["pe_trailing"]

        # FCF yield
        if valuation.get("price_to_fcf") and valuation["price_to_fcf"] > 0:
            valuation["fcf_yield"] = 1 / valuation["price_to_fcf"]

        return valuation

    def calculate_profitability_ratios(self) -> Dict[str, Any]:
        """
        Calculate profitability ratios.

        Returns:
            Dictionary of profitability metrics
        """
        profitability = {
            "gross_margin": self.stats.get("gross_margin"),
            "operating_margin": self.stats.get("operating_margin"),
            "net_margin": self.stats.get("profit_margin"),
            "roe": self.stats.get("roe"),
            "roa": self.stats.get("roa"),
        }

        # Calculate ROIC if we have the data
        # ROIC = NOPAT / Invested Capital
        # NOPAT = Operating Income * (1 - Tax Rate)
        # Invested Capital = Total Equity + Total Debt - Cash

        operating_income = self._safe_get(self.income_annual, "Operating Income", 0)
        tax_provision = self._safe_get(self.income_annual, "Tax Provision", 0)
        pretax_income = self._safe_get(self.income_annual, "Pretax Income", 0)

        total_equity = self._safe_get(self.balance_annual, "Stockholders Equity", 0)
        if total_equity is None:
            total_equity = self._safe_get(self.balance_annual, "Total Equity Gross Minority Interest", 0)

        total_debt = self._safe_get(self.balance_annual, "Total Debt", 0)
        cash = self._safe_get(self.balance_annual, "Cash And Cash Equivalents", 0)

        # Calculate effective tax rate
        if tax_provision and pretax_income and pretax_income != 0:
            tax_rate = tax_provision / pretax_income
            tax_rate = max(0, min(tax_rate, 0.5))  # Sanity check
        else:
            tax_rate = 0.21  # Default to US corporate rate

        # Calculate NOPAT and ROIC
        if operating_income:
            nopat = operating_income * (1 - tax_rate)
            profitability["nopat"] = nopat

            # Calculate invested capital
            if total_equity is not None:
                invested_capital = total_equity + (total_debt or 0) - (cash or 0)
                if invested_capital > 0:
                    profitability["roic"] = nopat / invested_capital
                    profitability["invested_capital"] = invested_capital

        # Calculate margin trends over time
        margin_trends = self._calculate_margin_trends()
        profitability["margin_trends"] = margin_trends

        return profitability

    def _calculate_margin_trends(self) -> Dict[str, List]:
        """Calculate margin trends over multiple years."""
        trends = {
            "years": [],
            "gross_margin": [],
            "operating_margin": [],
            "net_margin": [],
        }

        if self.income_annual.empty:
            return trends

        for i, col in enumerate(self.income_annual.columns[:4]):  # Last 4 years
            year = col.year if hasattr(col, 'year') else str(col)[:4]
            trends["years"].append(year)

            revenue = self._safe_get(self.income_annual, "Total Revenue", i)
            gross_profit = self._safe_get(self.income_annual, "Gross Profit", i)
            operating_income = self._safe_get(self.income_annual, "Operating Income", i)
            net_income = self._safe_get(self.income_annual, "Net Income", i)

            trends["gross_margin"].append(self._safe_divide(gross_profit, revenue))
            trends["operating_margin"].append(self._safe_divide(operating_income, revenue))
            trends["net_margin"].append(self._safe_divide(net_income, revenue))

        return trends

    def calculate_growth_rates(self) -> Dict[str, Any]:
        """
        Calculate growth rates for revenue, earnings, and cash flow.

        Returns:
            Dictionary of growth metrics
        """
        growth = {
            "revenue_growth_yoy": self.stats.get("revenue_growth"),
            "earnings_growth_yoy": self.stats.get("earnings_growth"),
            "earnings_growth_quarterly": self.stats.get("earnings_quarterly_growth"),
        }

        # Calculate historical growth rates from financial statements
        if not self.income_annual.empty and len(self.income_annual.columns) >= 2:
            # Revenue growth
            revenue_current = self._safe_get(self.income_annual, "Total Revenue", 0)
            revenue_1y = self._safe_get(self.income_annual, "Total Revenue", 1)
            revenue_3y = self._safe_get(self.income_annual, "Total Revenue", 3) if len(self.income_annual.columns) > 3 else None

            if revenue_current and revenue_1y:
                growth["revenue_growth_1y"] = (revenue_current / revenue_1y) - 1

            if revenue_current and revenue_3y and revenue_3y > 0:
                growth["revenue_cagr_3y"] = (revenue_current / revenue_3y) ** (1/3) - 1

            # EPS growth
            eps_current = self._safe_get(self.income_annual, "Basic EPS", 0)
            if eps_current is None:
                eps_current = self._safe_get(self.income_annual, "Diluted EPS", 0)

            eps_1y = self._safe_get(self.income_annual, "Basic EPS", 1)
            if eps_1y is None:
                eps_1y = self._safe_get(self.income_annual, "Diluted EPS", 1)

            eps_3y = None
            if len(self.income_annual.columns) > 3:
                eps_3y = self._safe_get(self.income_annual, "Basic EPS", 3)
                if eps_3y is None:
                    eps_3y = self._safe_get(self.income_annual, "Diluted EPS", 3)

            if eps_current and eps_1y and eps_1y > 0:
                growth["eps_growth_1y"] = (eps_current / eps_1y) - 1

            if eps_current and eps_3y and eps_3y > 0:
                growth["eps_cagr_3y"] = (eps_current / eps_3y) ** (1/3) - 1

            # Net income growth
            ni_current = self._safe_get(self.income_annual, "Net Income", 0)
            ni_1y = self._safe_get(self.income_annual, "Net Income", 1)

            if ni_current and ni_1y and ni_1y > 0:
                growth["net_income_growth_1y"] = (ni_current / ni_1y) - 1

        # FCF growth
        if not self.cashflow_annual.empty and len(self.cashflow_annual.columns) >= 2:
            fcf_current = self._safe_get(self.cashflow_annual, "Free Cash Flow", 0)
            fcf_1y = self._safe_get(self.cashflow_annual, "Free Cash Flow", 1)

            if fcf_current and fcf_1y and fcf_1y > 0:
                growth["fcf_growth_1y"] = (fcf_current / fcf_1y) - 1

        # Add historical data for trends
        growth["revenue_history"] = self._get_metric_history("Total Revenue", self.income_annual)
        growth["net_income_history"] = self._get_metric_history("Net Income", self.income_annual)
        growth["fcf_history"] = self._get_metric_history("Free Cash Flow", self.cashflow_annual)

        return growth

    def _get_metric_history(self, metric: str, df: pd.DataFrame) -> Dict[str, List]:
        """Get historical values for a metric."""
        history = {"years": [], "values": []}

        if df.empty or metric not in df.index:
            return history

        for i, col in enumerate(df.columns[:5]):  # Last 5 years
            year = col.year if hasattr(col, 'year') else str(col)[:4]
            value = self._safe_get(df, metric, i)
            history["years"].append(year)
            history["values"].append(value)

        # Reverse to show oldest first
        history["years"].reverse()
        history["values"].reverse()

        return history

    def calculate_financial_health(self) -> Dict[str, Any]:
        """
        Calculate financial health and leverage metrics.

        Returns:
            Dictionary of financial health metrics
        """
        health = {
            "current_ratio": self.stats.get("current_ratio"),
            "quick_ratio": self.stats.get("quick_ratio"),
            "debt_to_equity": self.stats.get("debt_to_equity"),
        }

        # Calculate additional metrics from balance sheet
        if not self.balance_annual.empty:
            total_assets = self._safe_get(self.balance_annual, "Total Assets", 0)
            total_liabilities = self._safe_get(self.balance_annual, "Total Liabilities Net Minority Interest", 0)
            total_equity = self._safe_get(self.balance_annual, "Stockholders Equity", 0)
            if total_equity is None:
                total_equity = self._safe_get(self.balance_annual, "Total Equity Gross Minority Interest", 0)
            total_debt = self._safe_get(self.balance_annual, "Total Debt", 0)
            long_term_debt = self._safe_get(self.balance_annual, "Long Term Debt", 0)
            cash = self._safe_get(self.balance_annual, "Cash And Cash Equivalents", 0)
            short_term_investments = self._safe_get(self.balance_annual, "Other Short Term Investments", 0)

            # Net debt
            if total_debt is not None and cash is not None:
                health["net_debt"] = total_debt - cash - (short_term_investments or 0)
                health["cash_position"] = cash + (short_term_investments or 0)

            # Debt ratios
            if total_assets and total_debt:
                health["debt_to_assets"] = total_debt / total_assets

            if total_equity and total_debt:
                health["debt_to_equity_calc"] = total_debt / total_equity

            # Equity ratio
            if total_assets and total_equity:
                health["equity_ratio"] = total_equity / total_assets

        # Interest coverage ratio
        if not self.income_annual.empty:
            operating_income = self._safe_get(self.income_annual, "Operating Income", 0)
            if operating_income is None:
                operating_income = self._safe_get(self.income_annual, "EBIT", 0)
            interest_expense = self._safe_get(self.income_annual, "Interest Expense", 0)

            if operating_income and interest_expense and interest_expense > 0:
                health["interest_coverage"] = operating_income / interest_expense

        # Debt/EBITDA
        if not self.income_annual.empty:
            ebitda = self._safe_get(self.income_annual, "EBITDA", 0)
            if ebitda is None:
                # Calculate EBITDA
                operating_income = self._safe_get(self.income_annual, "Operating Income", 0)
                depreciation = self._safe_get(self.cashflow_annual, "Depreciation And Amortization", 0)
                if operating_income and depreciation:
                    ebitda = operating_income + depreciation

            total_debt = self._safe_get(self.balance_annual, "Total Debt", 0)
            if ebitda and total_debt:
                health["debt_to_ebitda"] = total_debt / ebitda

        # Altman Z-Score (for non-financial companies)
        health["altman_z_score"] = self._calculate_altman_z_score()

        return health

    def _calculate_altman_z_score(self) -> Optional[float]:
        """
        Calculate Altman Z-Score for bankruptcy prediction.

        Z = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
        Where:
        A = Working Capital / Total Assets
        B = Retained Earnings / Total Assets
        C = EBIT / Total Assets
        D = Market Cap / Total Liabilities
        E = Sales / Total Assets
        """
        if self.balance_annual.empty or self.income_annual.empty:
            return None

        total_assets = self._safe_get(self.balance_annual, "Total Assets", 0)
        if not total_assets:
            return None

        current_assets = self._safe_get(self.balance_annual, "Current Assets", 0)
        current_liabilities = self._safe_get(self.balance_annual, "Current Liabilities", 0)
        retained_earnings = self._safe_get(self.balance_annual, "Retained Earnings", 0)
        ebit = self._safe_get(self.income_annual, "Operating Income", 0)
        total_liabilities = self._safe_get(self.balance_annual, "Total Liabilities Net Minority Interest", 0)
        revenue = self._safe_get(self.income_annual, "Total Revenue", 0)
        market_cap = self.overview.get("market_cap")

        # Calculate working capital
        working_capital = (current_assets or 0) - (current_liabilities or 0)

        # Calculate components
        a = working_capital / total_assets if total_assets else 0
        b = (retained_earnings / total_assets) if retained_earnings else 0
        c = (ebit / total_assets) if ebit else 0
        d = (market_cap / total_liabilities) if market_cap and total_liabilities else 0
        e = (revenue / total_assets) if revenue else 0

        z_score = 1.2 * a + 1.4 * b + 3.3 * c + 0.6 * d + 1.0 * e

        return z_score

    def calculate_efficiency_ratios(self) -> Dict[str, Any]:
        """
        Calculate efficiency and turnover ratios.

        Returns:
            Dictionary of efficiency metrics
        """
        efficiency = {}

        if self.balance_annual.empty or self.income_annual.empty:
            return efficiency

        # Get necessary values
        revenue = self._safe_get(self.income_annual, "Total Revenue", 0)
        cogs = self._safe_get(self.income_annual, "Cost Of Revenue", 0)
        total_assets = self._safe_get(self.balance_annual, "Total Assets", 0)
        inventory = self._safe_get(self.balance_annual, "Inventory", 0)
        receivables = self._safe_get(self.balance_annual, "Accounts Receivable", 0)
        if receivables is None:
            receivables = self._safe_get(self.balance_annual, "Net Receivables", 0)
        payables = self._safe_get(self.balance_annual, "Accounts Payable", 0)

        # Asset turnover
        if revenue and total_assets:
            efficiency["asset_turnover"] = revenue / total_assets

        # Inventory turnover
        if cogs and inventory and inventory > 0:
            efficiency["inventory_turnover"] = cogs / inventory
            efficiency["days_inventory"] = 365 / efficiency["inventory_turnover"]

        # Receivables turnover (DSO)
        if revenue and receivables and receivables > 0:
            efficiency["receivables_turnover"] = revenue / receivables
            efficiency["days_sales_outstanding"] = 365 / efficiency["receivables_turnover"]

        # Payables turnover (DPO)
        if cogs and payables and payables > 0:
            efficiency["payables_turnover"] = cogs / payables
            efficiency["days_payables_outstanding"] = 365 / efficiency["payables_turnover"]

        # Cash conversion cycle
        if all(k in efficiency for k in ["days_inventory", "days_sales_outstanding", "days_payables_outstanding"]):
            efficiency["cash_conversion_cycle"] = (
                efficiency["days_inventory"]
                + efficiency["days_sales_outstanding"]
                - efficiency["days_payables_outstanding"]
            )

        return efficiency

    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive financial analysis.

        Returns:
            Dictionary containing all financial analysis results
        """
        analysis = {
            "ticker": self.ticker,
            "company_name": self.overview.get("name"),
            "sector": self.overview.get("sector"),
            "industry": self.overview.get("industry"),
            "market_cap": self.overview.get("market_cap"),
            "current_price": self.overview.get("current_price"),
            "valuation": self.calculate_valuation_ratios(),
            "profitability": self.calculate_profitability_ratios(),
            "growth": self.calculate_growth_rates(),
            "financial_health": self.calculate_financial_health(),
            "efficiency": self.calculate_efficiency_ratios(),
            "return_metrics": self.return_metrics,
            "price_metrics": {
                "fifty_two_week_high": self.overview.get("fifty_two_week_high"),
                "fifty_two_week_low": self.overview.get("fifty_two_week_low"),
                "pct_from_52w_high": self.overview.get("pct_from_52w_high"),
                "pct_from_52w_low": self.overview.get("pct_from_52w_low"),
                "fifty_day_avg": self.overview.get("fifty_day_avg"),
                "two_hundred_day_avg": self.overview.get("two_hundred_day_avg"),
                "beta": self.stats.get("beta"),
            },
        }

        return analysis

    def generate_summary_table(self) -> pd.DataFrame:
        """
        Generate a summary table of key metrics.

        Returns:
            DataFrame with key metrics summary
        """
        analysis = self.get_comprehensive_analysis()

        summary_data = {
            "Metric": [],
            "Value": [],
            "Category": [],
        }

        # Valuation metrics
        val = analysis["valuation"]
        metrics_to_add = [
            ("P/E (Trailing)", val.get("pe_trailing"), "Valuation", ".2f"),
            ("P/E (Forward)", val.get("pe_forward"), "Valuation", ".2f"),
            ("PEG Ratio", val.get("peg_ratio"), "Valuation", ".2f"),
            ("P/B", val.get("price_to_book"), "Valuation", ".2f"),
            ("P/S", val.get("price_to_sales"), "Valuation", ".2f"),
            ("EV/EBITDA", val.get("ev_to_ebitda"), "Valuation", ".2f"),
            ("EV/Revenue", val.get("ev_to_revenue"), "Valuation", ".2f"),
            ("P/FCF", val.get("price_to_fcf"), "Valuation", ".2f"),
        ]

        # Profitability metrics
        prof = analysis["profitability"]
        metrics_to_add.extend([
            ("Gross Margin", prof.get("gross_margin"), "Profitability", ".1%"),
            ("Operating Margin", prof.get("operating_margin"), "Profitability", ".1%"),
            ("Net Margin", prof.get("net_margin"), "Profitability", ".1%"),
            ("ROE", prof.get("roe"), "Profitability", ".1%"),
            ("ROA", prof.get("roa"), "Profitability", ".1%"),
            ("ROIC", prof.get("roic"), "Profitability", ".1%"),
        ])

        # Growth metrics
        growth = analysis["growth"]
        metrics_to_add.extend([
            ("Revenue Growth (YoY)", growth.get("revenue_growth_1y"), "Growth", ".1%"),
            ("Revenue CAGR (3Y)", growth.get("revenue_cagr_3y"), "Growth", ".1%"),
            ("EPS Growth (YoY)", growth.get("eps_growth_1y"), "Growth", ".1%"),
            ("FCF Growth (YoY)", growth.get("fcf_growth_1y"), "Growth", ".1%"),
        ])

        # Financial health metrics
        health = analysis["financial_health"]
        metrics_to_add.extend([
            ("Current Ratio", health.get("current_ratio"), "Financial Health", ".2f"),
            ("Quick Ratio", health.get("quick_ratio"), "Financial Health", ".2f"),
            ("Debt/Equity", health.get("debt_to_equity"), "Financial Health", ".2f"),
            ("Interest Coverage", health.get("interest_coverage"), "Financial Health", ".1f"),
            ("Debt/EBITDA", health.get("debt_to_ebitda"), "Financial Health", ".2f"),
        ])

        # Efficiency metrics
        eff = analysis["efficiency"]
        metrics_to_add.extend([
            ("Asset Turnover", eff.get("asset_turnover"), "Efficiency", ".2f"),
            ("Inventory Turnover", eff.get("inventory_turnover"), "Efficiency", ".1f"),
            ("Days Sales Outstanding", eff.get("days_sales_outstanding"), "Efficiency", ".0f"),
        ])

        for metric_name, value, category, fmt in metrics_to_add:
            if value is not None:
                if "%" in fmt:
                    formatted_value = f"{value:{fmt}}"
                else:
                    formatted_value = f"{value:{fmt}}"
                summary_data["Metric"].append(metric_name)
                summary_data["Value"].append(formatted_value)
                summary_data["Category"].append(category)

        return pd.DataFrame(summary_data)


if __name__ == "__main__":
    # Test the financial analyzer
    from data_collector import DataCollector

    collector = DataCollector("NVDA")
    data = collector.get_all_data()

    analyzer = FinancialAnalyzer(data)
    analysis = analyzer.get_comprehensive_analysis()

    print("\n=== Comprehensive Financial Analysis ===")
    print(f"\nCompany: {analysis['company_name']}")
    print(f"Sector: {analysis['sector']}")
    print(f"Industry: {analysis['industry']}")

    print("\n--- Valuation ---")
    for key, value in analysis["valuation"].items():
        if value is not None and not isinstance(value, (dict, list)):
            print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")

    print("\n--- Profitability ---")
    for key, value in analysis["profitability"].items():
        if value is not None and not isinstance(value, (dict, list)):
            if isinstance(value, float) and abs(value) < 1:
                print(f"  {key}: {value:.1%}")
            elif isinstance(value, float):
                print(f"  {key}: {value:.2f}")

    print("\n--- Growth ---")
    for key, value in analysis["growth"].items():
        if value is not None and not isinstance(value, (dict, list)):
            if isinstance(value, float) and abs(value) < 10:
                print(f"  {key}: {value:.1%}")

    print("\n--- Financial Health ---")
    for key, value in analysis["financial_health"].items():
        if value is not None and not isinstance(value, (dict, list)):
            print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")

    print("\n--- Summary Table ---")
    summary = analyzer.generate_summary_table()
    print(summary.to_string(index=False))
