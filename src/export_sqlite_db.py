"""
SQLite Relational Database Builder for FNP Sales Analytics
"""

import sys
import sqlite3
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.config import (
    SQLITE_DB_PATH,
    CLEANED_SALES_CSV,
    RAW_CUSTOMERS_CSV,
    RAW_PRODUCTS_CSV,
)
from src.data_pipeline import clean_and_transform


def build_sqlite_database():
    """Build and populate normalized SQLite relational database with indexes and analytical views."""
    # Ensure cleaned data is available
    if not CLEANED_SALES_CSV.exists():
        clean_and_transform()

    df_cleaned = pd.read_csv(CLEANED_SALES_CSV)
    df_customers = pd.read_csv(RAW_CUSTOMERS_CSV)
    df_products = pd.read_csv(RAW_PRODUCTS_CSV)

    # Standardize column naming for dimensions
    df_customers.columns = [
        "customer_id", "customer_name", "customer_city", "contact_number",
        "email", "gender", "address"
    ]
    df_products.columns = [
        "product_id", "product_name", "category", "price_inr",
        "target_occasion", "description"
    ]

    # Select columns for fact table
    fact_cols = [
        "order_id", "customer_id", "product_id", "quantity",
        "order_date", "order_time", "delivery_date", "delivery_time",
        "delivery_location", "occasion", "order_month", "order_hour",
        "delivery_lead_days", "delivery_hour", "unit_price_inr",
        "revenue_inr", "order_day_of_week", "is_weekend",
        "order_quarter", "festive_season"
    ]
    df_fact = df_cleaned[fact_cols]

    # Remove existing DB if present
    if SQLITE_DB_PATH.exists():
        SQLITE_DB_PATH.unlink()

    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Create DDL Tables
    cursor.execute("""
    CREATE TABLE dim_customers (
        customer_id VARCHAR(10) PRIMARY KEY,
        customer_name VARCHAR(100) NOT NULL,
        customer_city VARCHAR(100) NOT NULL,
        contact_number BIGINT,
        email VARCHAR(150),
        gender VARCHAR(10),
        address TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE dim_products (
        product_id INTEGER PRIMARY KEY,
        product_name VARCHAR(100) NOT NULL,
        category VARCHAR(50) NOT NULL,
        price_inr INTEGER NOT NULL,
        target_occasion VARCHAR(50),
        description TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE fact_orders (
        order_id INTEGER PRIMARY KEY,
        customer_id VARCHAR(10) NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        order_date DATE NOT NULL,
        order_time TIME NOT NULL,
        delivery_date DATE NOT NULL,
        delivery_time TIME NOT NULL,
        delivery_location VARCHAR(100) NOT NULL,
        occasion VARCHAR(50) NOT NULL,
        order_month VARCHAR(10) NOT NULL,
        order_hour INTEGER NOT NULL,
        delivery_lead_days INTEGER NOT NULL,
        delivery_hour INTEGER NOT NULL,
        unit_price_inr INTEGER NOT NULL,
        revenue_inr INTEGER NOT NULL,
        order_day_of_week VARCHAR(15) NOT NULL,
        is_weekend INTEGER NOT NULL,
        order_quarter VARCHAR(5) NOT NULL,
        festive_season VARCHAR(50) NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
    );
    """)

    # 2. Insert Data
    df_customers.to_sql("dim_customers", conn, if_exists="append", index=False)
    df_products.to_sql("dim_products", conn, if_exists="append", index=False)
    df_fact.to_sql("fact_orders", conn, if_exists="append", index=False)

    # 3. Create Performance Indexes
    cursor.execute("CREATE INDEX idx_orders_customer ON fact_orders(customer_id);")
    cursor.execute("CREATE INDEX idx_orders_product ON fact_orders(product_id);")
    cursor.execute("CREATE INDEX idx_orders_date ON fact_orders(order_date);")
    cursor.execute("CREATE INDEX idx_orders_occasion ON fact_orders(occasion);")
    cursor.execute("CREATE INDEX idx_orders_month ON fact_orders(order_month);")

    # 4. Create Business Views
    cursor.execute("""
    CREATE VIEW v_executive_kpis AS
    SELECT 
        COUNT(order_id) AS total_orders,
        SUM(revenue_inr) AS total_revenue,
        SUM(quantity) AS total_units_sold,
        ROUND(AVG(revenue_inr), 2) AS average_order_value,
        ROUND(AVG(delivery_lead_days), 2) AS avg_delivery_days,
        COUNT(DISTINCT customer_id) AS total_active_customers,
        COUNT(DISTINCT product_id) AS total_active_skus
    FROM fact_orders;
    """)

    cursor.execute("""
    CREATE VIEW v_category_performance AS
    SELECT 
        p.category,
        COUNT(o.order_id) AS total_orders,
        SUM(o.quantity) AS total_quantity,
        SUM(o.revenue_inr) AS total_revenue,
        ROUND(AVG(o.revenue_inr), 2) AS avg_revenue_per_order,
        ROUND(100.0 * SUM(o.revenue_inr) / (SELECT SUM(revenue_inr) FROM fact_orders), 2) AS revenue_share_pct
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    GROUP BY p.category
    ORDER BY total_revenue DESC;
    """)

    cursor.execute("""
    CREATE VIEW v_occasion_performance AS
    SELECT 
        o.occasion,
        COUNT(o.order_id) AS total_orders,
        SUM(o.revenue_inr) AS total_revenue,
        ROUND(AVG(o.revenue_inr), 2) AS avg_order_value,
        ROUND(100.0 * SUM(o.revenue_inr) / (SELECT SUM(revenue_inr) FROM fact_orders), 2) AS revenue_share_pct
    FROM fact_orders o
    GROUP BY o.occasion
    ORDER BY total_revenue DESC;
    """)

    conn.commit()
    conn.close()

    print(f"Relational SQLite database created successfully at: {SQLITE_DB_PATH}")


if __name__ == "__main__":
    build_sqlite_database()
