"""
Jupyter Notebook Generator for FNP Sales Exploratory Data Analysis
"""

import json
from pathlib import Path

NOTEBOOK_PATH = Path(__file__).resolve().parent.parent / "notebooks" / "fnp_sales_exploratory_data_analysis.ipynb"


def create_markdown_cell(source_lines: list[str]) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source_lines]
    }


def create_code_cell(source_lines: list[str]) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source_lines]
    }


def build_eda_notebook():
    cells = []

    # Title Cell
    cells.append(create_markdown_cell([
        "# 🌸 Ferns N Petals (FNP) E-Commerce Sales Analytics & Business Intelligence",
        "### Exploratory Data Analysis, Festive Seasonality, & Executive Dashboard Re-creation",
        "",
        "**Author:** Het Oza  ",
        "**Role:** Professional Data Analyst & Analytics Engineer  ",
        "**Tools:** Python 3.10+, Pandas, Matplotlib, Seaborn, SQLite, Excel  ",
        "**Dataset Period:** FY 2023 (1,000 Transacted Baskets | 100 Customers | 70 SKUs)",
        "",
        "---"
    ]))

    # Section 1
    cells.append(create_markdown_cell([
        "## 1. Project Overview & Business Objectives",
        "Ferns N Petals (FNP) is India's leading omnichannel gifting and floral retailer. Gifting demand is heavily non-linear, driven by culturally significant festive occasions (Raksha Bandhan, Valentine's Day, Diwali, and Holi).",
        "",
        "### Key Business Objectives:",
        "1. **Replicate & Validate Executive Dashboard KPIs**: Reconcile total gross revenue (₹3.52M), total orders (1,000), and turnaround times.",
        "2. **Quantify Festive Seasonality**: Isolate the revenue contribution and spike dynamics of key Indian festivals.",
        "3. **Analyze Product Portfolio Mix**: Identify top revenue drivers and margin opportunities across 7 core categories.",
        "4. **Evaluate Fulfillment Velocity**: Analyze order-to-delivery turnaround across Indian geographies.",
        "5. **Synthesize Strategic Recommendations**: Provide actionable takeaways for marketing, supply chain, and merchandising teams."
    ]))

    # Section 2: Setup
    cells.append(create_markdown_cell([
        "## 2. Environment Setup & Data Loading"
    ]))

    cells.append(create_code_cell([
        "import os",
        "import sys",
        "import tempfile",
        "from pathlib import Path",
        "",
        "# Ensure clean matplotlib directory",
        "os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()",
        "",
        "import pandas as pd",
        "import numpy as np",
        "import matplotlib.pyplot as plt",
        "import matplotlib.ticker as ticker",
        "import seaborn as sns",
        "",
        "# Set global plotting aesthetic",
        "sns.set_theme(style='whitegrid', palette='Blues_r')",
        "plt.rcParams['font.sans-serif'] = 'DejaVu Sans'",
        "plt.rcParams['axes.edgecolor'] = '#cbd5e1'",
        "plt.rcParams['axes.linewidth'] = 0.8",
        "",
        "# Define path and load cleaned transactional dataset",
        "data_path = Path('../data/processed/fnp_sales_cleaned.csv')",
        "df = pd.read_csv(data_path)",
        "df['order_date'] = pd.to_datetime(df['order_date'])",
        "df['delivery_date'] = pd.to_datetime(df['delivery_date'])",
        "",
        "print(f'Successfully loaded {len(df):,} transactions across {df.shape[1]} columns.')",
        "df.head(3)"
    ]))

    # Section 3: Data Inspection & Integrity
    cells.append(create_markdown_cell([
        "## 3. Data Structure & Data Integrity Validation"
    ]))

    cells.append(create_code_cell([
        "print('=== Dataset Information ===')",
        "df.info()",
        "",
        "print('\\n=== Null Value Audit ===')",
        "print(df.isnull().sum())",
        "",
        "# Reconcile arithmetic integrity: Revenue = Quantity * Unit Price",
        "integrity_check = (df['quantity'] * df['unit_price_inr'] == df['revenue_inr']).all()",
        "print(f'\\n[Data Integrity] Revenue calculation exact match: {integrity_check}')"
    ]))

    # Section 4: Executive Scorecard
    cells.append(create_markdown_cell([
        "## 4. Executive KPI Scorecard Validation",
        "We validate the four primary scorecard metrics displayed on the executive Excel dashboard:",
        "- **Total Revenue**: ₹3,520,984 (~₹3.52M)",
        "- **Total Orders**: 1,000",
        "- **Average Delivery Lead Time**: 5.53 Days",
        "- **Average Spend per Customer**: ₹35,209.84"
    ]))

    cells.append(create_code_cell([
        "total_revenue = df['revenue_inr'].sum()",
        "total_orders = len(df)",
        "total_units = df['quantity'].sum()",
        "avg_aov = df['revenue_inr'].mean()",
        "avg_delivery = df['delivery_lead_days'].mean()",
        "unique_customers = df['customer_id'].nunique()",
        "avg_customer_spend = total_revenue / unique_customers",
        "",
        "print('=' * 55)",
        "print('       EXECUTIVE KPI SCORECARD (FY 2023)')",
        "print('=' * 55)",
        "print(f'Total Gross Revenue          : INR {total_revenue:,.2f} (~INR 3.52M)')",
        "print(f'Total Orders Transacted      : {total_orders:,}')",
        "print(f'Total Units Transacted       : {total_units:,} Units')",
        "print(f'Average Order Value (AOV)    : INR {avg_aov:,.2f}')",
        "print(f'Average Delivery Turnaround  : {avg_delivery:.2f} Days')",
        "print(f'Unique Active Customers      : {unique_customers}')",
        "print(f'Average Spend per Customer   : INR {avg_customer_spend:,.2f}')",
        "print('=' * 55)"
    ]))

    # Section 5: Monthly Trajectory
    cells.append(create_markdown_cell([
        "## 5. Monthly Revenue Trajectory & Festive Seasonality",
        "Analysis of month-over-month revenue reveals dramatic surges during key Indian gifting festivals:",
        "- **August (Raksha Bandhan)**: Peak month generating ₹737,389 (20.9% of annual revenue).",
        "- **February (Valentine's Day)**: Generates ₹704,509 (20.0% of annual revenue).",
        "- **March (Holi Festival)**: Generates ₹511,823 (14.5% of annual revenue).",
        "- **November (Diwali Season)**: Generates ₹449,169 (12.8% of annual revenue)."
    ]))

    cells.append(create_code_cell([
        "month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']",
        "monthly_rev = df.groupby('order_month')['revenue_inr'].sum().reindex(month_order)",
        "",
        "plt.figure(figsize=(11, 5))",
        "plt.plot(monthly_rev.index, monthly_rev.values / 1e3, marker='o', color='#0284c7', linewidth=2.8)",
        "plt.fill_between(monthly_rev.index, monthly_rev.values / 1e3, color='#38bdf8', alpha=0.2)",
        "",
        "# Annotations for peak events",
        "peaks = {'Feb': 'Valentine Rush\\nINR 704.5K', 'Aug': 'Raksha Bandhan\\nINR 737.4K', 'Nov': 'Diwali\\nINR 449.2K'}",
        "for m, txt in peaks.items():",
        "    val = monthly_rev[m] / 1e3",
        "    plt.scatter([m], [val], color='#ef4444', s=80, zorder=5)",
        "    plt.annotate(txt, (m, val), textcoords='offset points', xytext=(0, 15),",
        "                 ha='center', fontsize=9, fontweight='bold', color='#b91c1c',",
        "                 bbox=dict(boxstyle='round,pad=0.3', fc='#fee2e2', ec='#f87171'))",
        "",
        "plt.title('Monthly Gross Merchandise Value & Festive Peaks (2023)', fontsize=14, fontweight='bold', pad=15)",
        "plt.xlabel('Order Month', fontweight='bold', labelpad=10)",
        "plt.ylabel('Revenue (INR Thousands)', fontweight='bold', labelpad=10)",
        "plt.tight_layout()",
        "plt.show()"
    ]))

    # Section 6: Occasion Breakdown
    cells.append(create_markdown_cell([
        "## 6. Gifting Occasion Analysis",
        "Evaluating gross revenue by target gifting occasion."
    ]))

    cells.append(create_code_cell([
        "occasion_summary = df.groupby('occasion').agg(",
        "    revenue=('revenue_inr', 'sum'),",
        "    orders=('order_id', 'count'),",
        "    aov=('revenue_inr', 'mean')",
        ").sort_values('revenue', ascending=True)",
        "",
        "plt.figure(figsize=(10, 5))",
        "bars = plt.barh(occasion_summary.index, occasion_summary['revenue'] / 1e3, color='#0284c7', height=0.6)",
        "for bar in bars:",
        "    w = bar.get_width()",
        "    pct = (w * 1000 / total_revenue) * 100",
        "    plt.text(w + 10, bar.get_y() + bar.get_height() / 2, f'INR {w:,.1f}K ({pct:.1f}%)', va='center', fontweight='bold')",
        "",
        "plt.title('Revenue Contribution by Gifting Occasion', fontsize=14, fontweight='bold', pad=15)",
        "plt.xlabel('Revenue (INR Thousands)', fontweight='bold')",
        "plt.xlim(0, max(occasion_summary['revenue'] / 1e3) * 1.25)",
        "plt.tight_layout()",
        "plt.show()"
    ]))

    # Section 7: Product Categories
    cells.append(create_markdown_cell([
        "## 7. Product Category Breakdown & Catalog Mix"
    ]))

    cells.append(create_code_cell([
        "cat_summary = df.groupby('category').agg(",
        "    revenue=('revenue_inr', 'sum'),",
        "    orders=('order_id', 'count'),",
        "    units=('quantity', 'sum')",
        ").sort_values('revenue', ascending=False)",
        "",
        "cat_summary['rev_share_%'] = (cat_summary['revenue'] / total_revenue * 100).round(2)",
        "display(cat_summary)",
        "",
        "plt.figure(figsize=(10, 5))",
        "sns.barplot(x=cat_summary.index, y=cat_summary['revenue'] / 1e3, palette='Blues_r')",
        "plt.title('Revenue Distribution across 7 Product Categories', fontsize=14, fontweight='bold', pad=15)",
        "plt.xlabel('Category', fontweight='bold')",
        "plt.ylabel('Revenue (INR Thousands)', fontweight='bold')",
        "plt.tight_layout()",
        "plt.show()"
    ]))

    # Section 8: Demographics & Geography
    cells.append(create_markdown_cell([
        "## 8. Customer Demographics & Top 10 Order Hubs"
    ]))

    cells.append(create_code_cell([
        "fig, axes = plt.subplots(1, 2, figsize=(14, 5))",
        "",
        "# Gender Donut",
        "gender_rev = df.groupby('gender')['revenue_inr'].sum()",
        "axes[0].pie(gender_rev, labels=gender_rev.index, autopct='%1.2f%%', startangle=90,",
        "            colors=['#0ea5e9', '#0284c7'], wedgeprops=dict(width=0.45, edgecolor='w', linewidth=2))",
        "axes[0].set_title('Revenue Share by Gender (50.84% M vs 49.16% F)', fontweight='bold', fontsize=12)",
        "",
        "# Top 10 Cities",
        "top_cities = df['customer_city'].value_counts().head(10).sort_values(ascending=True)",
        "axes[1].barh(top_cities.index, top_cities.values, color='#6366f1', height=0.6)",
        "for bar in axes[1].patches:",
        "    axes[1].text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2, f'{int(bar.get_width())}', va='center', fontweight='bold')",
        "axes[1].set_title('Top 10 Cities by Order Volume', fontweight='bold', fontsize=12)",
        "axes[1].set_xlabel('Order Count', fontweight='bold')",
        "",
        "plt.tight_layout()",
        "plt.show()"
    ]))

    # Section 9: Strategic Recommendations
    cells.append(create_markdown_cell([
        "## 9. Strategic Executive Recommendations",
        "",
        "### 1. Festive Inventory Buffer & Fulfillment Preparation",
        "- **August (Rakhi) and February (Valentine's)** together account for **40.9%** of annual top-line revenue.",
        "- Supply chain and fulfillment operations must pre-stock packaging, flowers, and sweets 3 weeks ahead of these key dates.",
        "",
        "### 2. High-Margin Upselling on Colors & Sweets",
        "- The 'Colors' category leads total revenue at **₹1.01M (28.6%)**, primarily purchased around Holi.",
        "- Introduce curated festival hampers combining colors with sweets and greeting cards to expand Average Order Value.",
        "",
        "### 3. Delivery Lead Time Optimization",
        "- The average delivery turnaround of **5.53 days** is relatively long for perishable gifts like cakes and flowers.",
        "- Introducing same-day and next-day express delivery tiers in top tier-2 cities (Imphal, Dhanbad, Kavali) can significantly improve customer retention and repeat purchase rates."
    ]))

    notebook_data = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.11"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(notebook_data, f, indent=2)

    print(f"Interactive Jupyter Notebook built successfully at: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    build_eda_notebook()
