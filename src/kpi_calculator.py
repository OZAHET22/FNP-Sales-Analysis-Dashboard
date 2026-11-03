"""
Automated Executive KPI Calculator and Metrics Engine
"""

import sys
import json
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.config import (
    CLEANED_SALES_CSV,
    KPI_SUMMARY_JSON,
    CATEGORY_KPI_CSV,
    MONTH_ORDER,
    DAY_ORDER,
)
from src.data_pipeline import clean_and_transform


def calculate_kpis(df: pd.DataFrame = None) -> dict:
    """Calculate all executive KPI metrics, category breakdowns, and dimensions."""
    if df is None:
        if not CLEANED_SALES_CSV.exists():
            df = clean_and_transform()
        else:
            df = pd.read_csv(CLEANED_SALES_CSV)

    # 1. High-Level Executive Metrics
    total_revenue = int(df["revenue_inr"].sum())
    total_orders = int(len(df))
    total_quantity = int(df["quantity"].sum())
    avg_order_value = round(float(df["revenue_inr"].mean()), 2)
    avg_delivery_days = round(float(df["delivery_lead_days"].mean()), 2)
    unique_customers = int(df["customer_id"].nunique())
    unique_products = int(df["product_id"].nunique())
    avg_customer_spend = round(total_revenue / unique_customers, 2)
    avg_orders_per_customer = round(total_orders / unique_customers, 2)

    # Gender Split
    gender_grouped = df.groupby("gender")["revenue_inr"].sum()
    gender_share = {
        gender: {
            "revenue": int(rev),
            "share_percentage": round(float(rev / total_revenue * 100), 2)
        }
        for gender, rev in gender_grouped.items()
    }

    # 2. Monthly Trend
    monthly_df = df.groupby("order_month").agg(
        revenue=("revenue_inr", "sum"),
        orders=("order_id", "count"),
        units=("quantity", "sum")
    ).reindex(MONTH_ORDER)

    monthly_summary = {
        month: {
            "revenue": int(monthly_df.loc[month, "revenue"]),
            "orders": int(monthly_df.loc[month, "orders"]),
            "units": int(monthly_df.loc[month, "units"])
        }
        for month in MONTH_ORDER if month in monthly_df.index
    }

    # 3. Occasion Breakdown
    occasion_df = df.groupby("occasion").agg(
        revenue=("revenue_inr", "sum"),
        orders=("order_id", "count"),
        avg_order_value=("revenue_inr", "mean")
    ).sort_values("revenue", ascending=False)

    occasion_summary = {
        occ: {
            "revenue": int(row["revenue"]),
            "orders": int(row["orders"]),
            "avg_order_value": round(float(row["avg_order_value"]), 2),
            "revenue_share": round(float(row["revenue"] / total_revenue * 100), 2)
        }
        for occ, row in occasion_df.iterrows()
    }

    # 4. Category Breakdown
    category_df = df.groupby("category").agg(
        revenue=("revenue_inr", "sum"),
        orders=("order_id", "count"),
        units_sold=("quantity", "sum"),
        avg_unit_price=("unit_price_inr", "mean")
    ).sort_values("revenue", ascending=False)

    category_summary = {
        cat: {
            "revenue": int(row["revenue"]),
            "orders": int(row["orders"]),
            "units_sold": int(row["units_sold"]),
            "avg_unit_price": round(float(row["avg_unit_price"]), 2),
            "revenue_share": round(float(row["revenue"] / total_revenue * 100), 2)
        }
        for cat, row in category_df.iterrows()
    }

    # Export Category CSV for reporting
    category_df_export = category_df.reset_index()
    category_df_export["revenue_share_pct"] = (category_df_export["revenue"] / total_revenue * 100).round(2)
    category_df_export.to_csv(CATEGORY_KPI_CSV, index=False)

    # 5. Day of Week Trend
    dow_df = df.groupby("order_day_of_week")["revenue_inr"].agg(["sum", "count"]).reindex(DAY_ORDER)
    dow_summary = {
        day: {
            "revenue": int(dow_df.loc[day, "sum"]),
            "orders": int(dow_df.loc[day, "count"])
        }
        for day in DAY_ORDER if day in dow_df.index
    }

    # 6. Hourly Order & Revenue Trend
    hourly_df = df.groupby("order_hour")["revenue_inr"].agg(["sum", "count"]).sort_index()
    hourly_summary = {
        int(hour): {
            "revenue": int(row["sum"]),
            "orders": int(row["count"])
        }
        for hour, row in hourly_df.iterrows()
    }

    # 7. Top 10 Products by Revenue
    top_products_df = df.groupby(["product_id", "product_name", "category"]).agg(
        revenue=("revenue_inr", "sum"),
        orders=("order_id", "count"),
        units=("quantity", "sum")
    ).sort_values("revenue", ascending=False).head(10).reset_index()

    top_products = [
        {
            "product_id": int(row["product_id"]),
            "product_name": str(row["product_name"]),
            "category": str(row["category"]),
            "revenue": int(row["revenue"]),
            "orders": int(row["orders"]),
            "units": int(row["units"])
        }
        for _, row in top_products_df.iterrows()
    ]

    # 8. Top 10 Customer Cities by Orders
    top_cities_df = df["customer_city"].value_counts().head(10).reset_index()
    top_cities_df.columns = ["city", "orders"]
    top_cities = [
        {"city": str(row["city"]), "orders": int(row["orders"])}
        for _, row in top_cities_df.iterrows()
    ]

    # Combine all into master KPI payload
    kpis = {
        "metadata": {
            "project_name": "FNP E-Commerce Sales Analytics",
            "currency": "INR (₹)",
            "reporting_period": "FY 2023 (Jan 2023 - Dec 2023)"
        },
        "executive_summary": {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_units_sold": total_quantity,
            "average_order_value": avg_order_value,
            "average_delivery_days": avg_delivery_days,
            "unique_customers": unique_customers,
            "unique_products": unique_products,
            "average_spend_per_customer": avg_customer_spend,
            "average_orders_per_customer": avg_orders_per_customer,
            "gender_distribution": gender_share
        },
        "monthly_trends": monthly_summary,
        "occasion_breakdown": occasion_summary,
        "category_breakdown": category_summary,
        "day_of_week_trends": dow_summary,
        "hourly_trends": hourly_summary,
        "top_10_products": top_products,
        "top_10_cities": top_cities
    }

    # Persist JSON
    with open(KPI_SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(kpis, f, indent=2)

    return kpis


def print_executive_scorecard(kpis: dict):
    """Format and print an executive summary scorecard to console."""
    es = kpis["executive_summary"]
    print("\n" + "=" * 65)
    print("        FNP SALES ANALYTICS - EXECUTIVE SCORECARD (2023)")
    print("=" * 65)
    print(f"  Total Gross Merchandise Value (Revenue) : INR {es['total_revenue']:,} (~INR 3.52M)")
    print(f"  Total Confirmed Orders                  : {es['total_orders']:,} Orders")
    print(f"  Total Product Units Transacted          : {es['total_units_sold']:,} Units")
    print(f"  Average Order Value (AOV)               : INR {es['average_order_value']:,.2f}")
    print(f"  Average Order-to-Delivery Turnaround    : {es['average_delivery_days']} Days")
    print(f"  Active Customer Base                    : {es['unique_customers']} Customers")
    print(f"  Average Revenue Per Customer            : INR {es['average_spend_per_customer']:,.2f}")
    print(f"  Male Revenue Contribution               : {es['gender_distribution']['Male']['share_percentage']}%")
    print(f"  Female Revenue Contribution             : {es['gender_distribution']['Female']['share_percentage']}%")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    kpis = calculate_kpis()
    print_executive_scorecard(kpis)
    print(f"KPI summary exported to {KPI_SUMMARY_JSON}")
