"""
FNP Sales Data Cleaning, Ingestion, and Transformation Pipeline
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.config import (
    RAW_CUSTOMERS_CSV,
    RAW_ORDERS_CSV,
    RAW_PRODUCTS_CSV,
    EXCEL_WORKBOOK,
    CLEANED_SALES_CSV,
    PROCESSED_DATA_DIR,
)


def load_raw_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load raw customers, orders, and products data from CSV or Excel fallback."""
    if RAW_CUSTOMERS_CSV.exists() and RAW_ORDERS_CSV.exists() and RAW_PRODUCTS_CSV.exists():
        customers = pd.read_csv(RAW_CUSTOMERS_CSV)
        orders = pd.read_csv(RAW_ORDERS_CSV)
        products = pd.read_csv(RAW_PRODUCTS_CSV)
    else:
        xls = pd.ExcelFile(EXCEL_WORKBOOK)
        customers = pd.read_excel(xls, "Customers")
        orders = pd.read_excel(xls, "Orders")
        products = pd.read_excel(xls, "Products")
    return customers, orders, products


def clean_and_transform() -> pd.DataFrame:
    """Execute complete data transformation and feature engineering pipeline."""
    customers, orders, products = load_raw_data()

    # 1. Clean Customers
    customers_clean = customers.copy()
    customers_clean.rename(columns={
        "Customer_ID": "customer_id",
        "Name": "customer_name",
        "City": "customer_city",
        "Contact_Number": "contact_number",
        "Email": "email",
        "Gender": "gender",
        "Address": "address"
    }, inplace=True)
    customers_clean["customer_id"] = customers_clean["customer_id"].astype(str).str.strip()
    customers_clean["customer_name"] = customers_clean["customer_name"].astype(str).str.strip()
    customers_clean["customer_city"] = customers_clean["customer_city"].astype(str).str.strip()
    customers_clean["gender"] = customers_clean["gender"].astype(str).str.strip().str.capitalize()

    # 2. Clean Products
    products_clean = products.copy()
    products_clean.rename(columns={
        "Product_ID": "product_id",
        "Product_Name": "product_name",
        "Category": "category",
        "Price (INR)": "catalog_price_inr",
        "Occasion": "product_target_occasion",
        "Description": "product_description"
    }, inplace=True)
    products_clean["product_id"] = products_clean["product_id"].astype(int)
    products_clean["product_name"] = products_clean["product_name"].astype(str).str.strip()
    products_clean["category"] = products_clean["category"].astype(str).str.strip()

    # 3. Clean Orders
    orders_clean = orders.copy()
    orders_clean.rename(columns={
        "Order_ID": "order_id",
        "Customer_ID": "customer_id",
        "Product_ID": "product_id",
        "Quantity": "quantity",
        "Order_Date": "order_date",
        "Order_Time": "order_time",
        "Delivery_Date": "delivery_date",
        "Delivery_Time": "delivery_time",
        "Location": "delivery_location",
        "Occasion": "occasion",
        "Order_Month_Name": "order_month",
        "Order_Hour": "order_hour",
        "diff_order_delivery": "delivery_lead_days",
        "delivery_Hour": "delivery_hour",
        "Products.Price (INR)": "unit_price_inr",
        "Revenue": "revenue_inr",
        "Week days": "order_day_of_week"
    }, inplace=True)

    orders_clean["customer_id"] = orders_clean["customer_id"].astype(str).str.strip()
    orders_clean["product_id"] = orders_clean["product_id"].astype(int)
    orders_clean["order_date"] = pd.to_datetime(orders_clean["order_date"])
    orders_clean["delivery_date"] = pd.to_datetime(orders_clean["delivery_date"])
    orders_clean["order_time"] = orders_clean["order_time"].astype(str)
    orders_clean["delivery_time"] = orders_clean["delivery_time"].astype(str)
    orders_clean["delivery_location"] = orders_clean["delivery_location"].astype(str).str.strip()
    orders_clean["occasion"] = orders_clean["occasion"].astype(str).str.strip()
    orders_clean["order_day_of_week"] = orders_clean["order_day_of_week"].astype(str).str.strip()

    # 4. Feature Engineering
    orders_clean["order_year"] = orders_clean["order_date"].dt.year
    orders_clean["order_quarter"] = "Q" + orders_clean["order_date"].dt.quarter.astype(str)
    orders_clean["order_month_num"] = orders_clean["order_date"].dt.month
    orders_clean["is_weekend"] = orders_clean["order_day_of_week"].isin(["Saturday", "Sunday"]).astype(int)

    # Basket Size Categorization
    orders_clean["basket_tier"] = pd.cut(
        orders_clean["quantity"],
        bins=[0, 1, 3, 5],
        labels=["Single (1)", "Standard (2-3)", "Bulk (4-5)"]
    )

    # Delivery Performance Tier
    orders_clean["delivery_tier"] = pd.cut(
        orders_clean["delivery_lead_days"],
        bins=[-1, 2, 5, 10],
        labels=["Express (<=2d)", "Standard (3-5d)", "Extended (6-10d)"]
    )

    # Festive Surge Season Tagging
    def tag_festive_season(row):
        month = row["order_month_num"]
        occasion = row["occasion"]
        if occasion == "Valentine's Day" or month == 2:
            return "Valentine Rush (Feb)"
        elif occasion == "Holi" or month == 3:
            return "Holi Festival (Mar)"
        elif occasion == "Raksha Bandhan" or month == 8:
            return "Raksha Bandhan Surge (Aug)"
        elif occasion == "Diwali" or month in [10, 11]:
            return "Diwali & Festive Season (Q4)"
        return "Regular Gifting"

    orders_clean["festive_season"] = orders_clean.apply(tag_festive_season, axis=1)

    # 5. Enrich Orders with Customer and Product Metadata
    enriched_df = orders_clean.merge(
        customers_clean[["customer_id", "customer_name", "customer_city", "gender", "email"]],
        on="customer_id",
        how="left"
    ).merge(
        products_clean[["product_id", "product_name", "category", "product_description"]],
        on="product_id",
        how="left"
    )

    # 6. Integrity Validations
    assert len(enriched_df) == 1000, f"Expected 1000 orders, got {len(enriched_df)}"
    revenue_check = (enriched_df["quantity"] * enriched_df["unit_price_inr"] == enriched_df["revenue_inr"]).all()
    assert revenue_check, "Revenue does not equal quantity * unit_price_inr!"
    assert enriched_df["revenue_inr"].sum() == 3520984, f"Revenue mismatch: {enriched_df['revenue_inr'].sum()}"
    assert enriched_df.isnull().sum().sum() == 0, "Found unexpected null values in enriched dataset!"

    # 7. Persist Cleaned Dataset
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    enriched_df.to_csv(CLEANED_SALES_CSV, index=False)
    print(f"Data pipeline executed successfully: {len(enriched_df)} rows saved to {CLEANED_SALES_CSV}")
    return enriched_df


if __name__ == "__main__":
    df = clean_and_transform()
    print("Pipeline validation passed with 100% data integrity.")
