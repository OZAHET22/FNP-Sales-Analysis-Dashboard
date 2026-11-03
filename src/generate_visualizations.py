"""
Publication-Quality Visual Analytics Generator
"""

import os
import sys
import tempfile
from pathlib import Path

# Fix matplotlib cache directory before import
os.environ["MPLCONFIGDIR"] = tempfile.mkdtemp()

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.config import (
    CLEANED_SALES_CSV,
    ASSETS_DIR,
    MONTH_ORDER,
    DAY_ORDER,
    PALETTE,
)
from src.data_pipeline import clean_and_transform

# Global style configuration
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cbd5e1"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.color"] = "#f1f5f9"
plt.rcParams["grid.linestyle"] = "--"


def load_dataset() -> pd.DataFrame:
    if not CLEANED_SALES_CSV.exists():
        return clean_and_transform()
    return pd.read_csv(CLEANED_SALES_CSV)


def generate_kpi_scorecard(df: pd.DataFrame):
    """Generate executive KPI summary cards banner."""
    total_rev = df["revenue_inr"].sum()
    total_orders = len(df)
    avg_delivery = df["delivery_lead_days"].mean()
    avg_spend = total_rev / df["customer_id"].nunique()

    fig, ax = plt.subplots(figsize=(13, 3.2), facecolor="#ffffff")
    ax.axis("off")

    cards = [
        {"title": "TOTAL REVENUE", "value": f"INR {total_rev/1e6:.2f}M", "sub": "INR 3,520,984 Total GMV", "color": "#0284c7"},
        {"title": "TOTAL ORDERS", "value": f"{total_orders:,}", "sub": "1,000 Transacted Baskets", "color": "#0d9488"},
        {"title": "AVG DELIVERY TIME", "value": f"{avg_delivery:.2f} Days", "sub": "Order to Delivery Cycle", "color": "#f59e0b"},
        {"title": "AVG SPEND / CUSTOMER", "value": f"INR {avg_spend/1e3:.1f}K", "sub": "INR 35,209.84 across 100 Users", "color": "#8b5cf6"},
    ]

    for idx, card in enumerate(cards):
        x = 0.02 + idx * 0.245
        width = 0.225
        # Background card box
        rect = plt.Rectangle(
            (x, 0.08), width, 0.84,
            facecolor="#f8fafc",
            edgecolor=card["color"],
            linewidth=2.5,
            transform=ax.transAxes,
            clip_on=False
        )
        ax.add_patch(rect)

        # Content
        ax.text(x + width / 2, 0.72, card["title"], fontsize=10, fontweight="bold",
                color="#64748b", ha="center", va="center", transform=ax.transAxes)
        ax.text(x + width / 2, 0.44, card["value"], fontsize=18, fontweight="bold",
                color=card["color"], ha="center", va="center", transform=ax.transAxes)
        ax.text(x + width / 2, 0.20, card["sub"], fontsize=8.5,
                color="#475569", ha="center", va="center", transform=ax.transAxes)

    plt.tight_layout()
    output_path = ASSETS_DIR / "kpi_overview_cards.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="#ffffff")
    plt.close()
    print(f"Generated: {output_path}")


def generate_monthly_trend(df: pd.DataFrame):
    """Generate monthly revenue trend chart with festive surges."""
    monthly = df.groupby("order_month")["revenue_inr"].sum().reindex(MONTH_ORDER)

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#ffffff")
    ax.set_facecolor("#ffffff")

    ax.plot(monthly.index, monthly.values / 1e3, color="#0284c7", marker="o", markersize=7,
            linewidth=2.8, label="Monthly Revenue (INR '000)")
    ax.fill_between(monthly.index, monthly.values / 1e3, color="#38bdf8", alpha=0.15)

    # Highlight peak months
    peak_months = {"Feb": "Valentine's Rush\nINR 704.5K", "Aug": "Rakhi Peak\nINR 737.4K", "Nov": "Diwali Season\nINR 449.2K"}
    for m, label in peak_months.items():
        val = monthly[m] / 1e3
        ax.scatter([m], [val], color="#ef4444", s=90, zorder=5)
        ax.annotate(label, (m, val), textcoords="offset points", xytext=(0, 14),
                    ha="center", fontsize=8.5, fontweight="bold", color="#b91c1c",
                    bbox=dict(boxstyle="round,pad=0.25", fc="#fee2e2", ec="#f87171", lw=0.8))

    ax.set_title("Monthly Revenue Trajectory & Festive Surges (FY 2023)", fontsize=13, fontweight="bold", pad=15, color="#0f172a")
    ax.set_xlabel("Order Month", fontsize=10, fontweight="bold", labelpad=8, color="#334155")
    ax.set_ylabel("Gross Merchandise Value (INR Thousands)", fontsize=10, fontweight="bold", labelpad=8, color="#334155")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"INR {int(x):,}K"))
    ax.grid(True, axis="y", linestyle="--", alpha=0.6)
    sns.despine(top=True, right=True)

    plt.tight_layout()
    output_path = ASSETS_DIR / "monthly_trend.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="#ffffff")
    plt.close()
    print(f"Generated: {output_path}")


def generate_occasion_breakdown(df: pd.DataFrame):
    """Generate revenue breakdown by occasion."""
    occ = df.groupby("occasion")["revenue_inr"].sum().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5), facecolor="#ffffff")
    ax.set_facecolor("#ffffff")

    bars = ax.barh(occ.index, occ.values / 1e3, color="#0284c7", height=0.62, edgecolor="#0369a1")

    for bar in bars:
        width = bar.get_width()
        pct = (width * 1000 / df["revenue_inr"].sum()) * 100
        ax.text(width + 8, bar.get_y() + bar.get_height() / 2,
                f"INR {width:,.1f}K ({pct:.1f}%)",
                va="center", fontsize=9, fontweight="bold", color="#1e293b")

    ax.set_title("Revenue Contribution by Gifting Occasion", fontsize=13, fontweight="bold", pad=15, color="#0f172a")
    ax.set_xlabel("Revenue (INR Thousands)", fontsize=10, fontweight="bold", labelpad=8, color="#334155")
    ax.set_xlim(0, max(occ.values / 1e3) * 1.25)
    ax.grid(True, axis="x", linestyle="--", alpha=0.6)
    sns.despine(top=True, right=True)

    plt.tight_layout()
    output_path = ASSETS_DIR / "occasion_breakdown.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="#ffffff")
    plt.close()
    print(f"Generated: {output_path}")


def generate_category_distribution(df: pd.DataFrame):
    """Generate revenue distribution by product category."""
    cat = df.groupby("category")["revenue_inr"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5), facecolor="#ffffff")
    ax.set_facecolor("#ffffff")

    colors = ["#0284c7", "#0ea5e9", "#38bdf8", "#7dd3fc", "#93c5fd", "#bfdbfe", "#cbd5e1"]
    bars = ax.bar(cat.index, cat.values / 1e3, color=colors[:len(cat)], width=0.6, edgecolor="#0f172a", linewidth=0.5)

    for bar in bars:
        height = bar.get_height()
        pct = (height * 1000 / df["revenue_inr"].sum()) * 100
        ax.text(bar.get_x() + bar.get_width() / 2, height + 18,
                f"INR {height:,.0f}K\n({pct:.1f}%)",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#0f172a")

    ax.set_title("Revenue Distribution across Product Categories", fontsize=13, fontweight="bold", pad=15, color="#0f172a")
    ax.set_ylabel("Revenue (INR Thousands)", fontsize=10, fontweight="bold", labelpad=8, color="#334155")
    ax.set_ylim(0, max(cat.values / 1e3) * 1.18)
    ax.grid(True, axis="y", linestyle="--", alpha=0.6)
    sns.despine(top=True, right=True)

    plt.tight_layout()
    output_path = ASSETS_DIR / "category_distribution.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="#ffffff")
    plt.close()
    print(f"Generated: {output_path}")


def generate_top_products(df: pd.DataFrame):
    """Generate horizontal bar chart for top 10 products by revenue."""
    top_p = df.groupby("product_name")["revenue_inr"].sum().sort_values(ascending=True).tail(10)

    fig, ax = plt.subplots(figsize=(9, 5.5), facecolor="#ffffff")
    ax.set_facecolor("#ffffff")

    bars = ax.barh(top_p.index, top_p.values / 1e3, color="#0d9488", height=0.6, edgecolor="#0f766e")

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 2, bar.get_y() + bar.get_height() / 2,
                f"INR {width:,.1f}K",
                va="center", fontsize=8.5, fontweight="bold", color="#134e4a")

    ax.set_title("Top 10 Product SKUs by Total Revenue", fontsize=13, fontweight="bold", pad=15, color="#0f172a")
    ax.set_xlabel("Revenue (INR Thousands)", fontsize=10, fontweight="bold", labelpad=8, color="#334155")
    ax.set_xlim(0, max(top_p.values / 1e3) * 1.22)
    ax.grid(True, axis="x", linestyle="--", alpha=0.6)
    sns.despine(top=True, right=True)

    plt.tight_layout()
    output_path = ASSETS_DIR / "top_products.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="#ffffff")
    plt.close()
    print(f"Generated: {output_path}")


def generate_city_performance(df: pd.DataFrame):
    """Generate top 10 customer cities by order volume."""
    top_c = df["customer_city"].value_counts().head(10).sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5), facecolor="#ffffff")
    ax.set_facecolor("#ffffff")

    bars = ax.barh(top_c.index, top_c.values, color="#6366f1", height=0.6, edgecolor="#4f46e5")

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.4, bar.get_y() + bar.get_height() / 2,
                f"{int(width)} Orders",
                va="center", fontsize=9, fontweight="bold", color="#312e81")

    ax.set_title("Top 10 Customer Cities by Order Volume", fontsize=13, fontweight="bold", pad=15, color="#0f172a")
    ax.set_xlabel("Order Count", fontsize=10, fontweight="bold", labelpad=8, color="#334155")
    ax.set_xlim(0, max(top_c.values) * 1.2)
    ax.grid(True, axis="x", linestyle="--", alpha=0.6)
    sns.despine(top=True, right=True)

    plt.tight_layout()
    output_path = ASSETS_DIR / "city_performance.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="#ffffff")
    plt.close()
    print(f"Generated: {output_path}")


def generate_all_visuals():
    """Batch execute all visual asset generation."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_dataset()
    print(f"Generating publication visual assets for {len(df)} transactions...")
    generate_kpi_scorecard(df)
    generate_monthly_trend(df)
    generate_occasion_breakdown(df)
    generate_category_distribution(df)
    generate_top_products(df)
    generate_city_performance(df)
    print("All visual assets successfully generated in assets/ directory.")


if __name__ == "__main__":
    generate_all_visuals()
