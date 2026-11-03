"""
Automated Test Suite for FNP Sales Analytics Data Pipeline & KPIs
"""

import sys
import sqlite3
from pathlib import Path
import pytest
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.config import (
    CLEANED_SALES_CSV,
    SQLITE_DB_PATH,
    RAW_CUSTOMERS_CSV,
    RAW_ORDERS_CSV,
    RAW_PRODUCTS_CSV,
)
from src.data_pipeline import load_raw_data, clean_and_transform
from src.kpi_calculator import calculate_kpis
from src.export_sqlite_db import build_sqlite_database


@pytest.fixture(scope="session")
def processed_data():
    """Ensure data is processed and return cleaned DataFrame."""
    df = clean_and_transform()
    build_sqlite_database()
    return df


def test_raw_data_loading():
    """Verify raw datasets load with expected record counts."""
    customers, orders, products = load_raw_data()
    assert len(customers) == 100, f"Expected 100 customers, got {len(customers)}"
    assert len(orders) == 1000, f"Expected 1000 orders, got {len(orders)}"
    assert len(products) == 70, f"Expected 70 products, got {len(products)}"


def test_cleaned_data_shape_and_nulls(processed_data):
    """Verify cleaned dataset has exactly 1,000 rows and zero null values."""
    assert len(processed_data) == 1000
    assert processed_data.isnull().sum().sum() == 0


def test_revenue_arithmetic_consistency(processed_data):
    """Verify revenue equals quantity multiplied by unit price for all records."""
    calculated = processed_data["quantity"] * processed_data["unit_price_inr"]
    assert (calculated == processed_data["revenue_inr"]).all()


def test_total_gmv_reconciliation(processed_data):
    """Verify total revenue matches exact Excel dashboard value of INR 3,520,984."""
    total_rev = processed_data["revenue_inr"].sum()
    assert total_rev == 3520984


def test_delivery_lead_calculation(processed_data):
    """Verify delivery lead days calculation matches date difference."""
    order_d = pd.to_datetime(processed_data["order_date"])
    delivery_d = pd.to_datetime(processed_data["delivery_date"])
    expected_days = (delivery_d - order_d).dt.days
    assert (expected_days == processed_data["delivery_lead_days"]).all()


def test_kpi_engine_values(processed_data):
    """Verify KPI calculator returns exact expected executive scorecard metrics."""
    kpis = calculate_kpis(processed_data)
    es = kpis["executive_summary"]
    assert es["total_revenue"] == 3520984
    assert es["total_orders"] == 1000
    assert es["total_units_sold"] == 3045
    assert es["average_order_value"] == 3520.98
    assert es["average_delivery_days"] == 5.53
    assert es["unique_customers"] == 100
    assert es["gender_distribution"]["Male"]["share_percentage"] == 50.84
    assert es["gender_distribution"]["Female"]["share_percentage"] == 49.16


def test_sqlite_database_views():
    """Verify SQLite database schema, tables, and views function correctly."""
    assert SQLITE_DB_PATH.exists(), "SQLite database does not exist"
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cur = conn.cursor()

    # Check table counts
    cur.execute("SELECT COUNT(*) FROM dim_customers;")
    assert cur.fetchone()[0] == 100

    cur.execute("SELECT COUNT(*) FROM dim_products;")
    assert cur.fetchone()[0] == 70

    cur.execute("SELECT COUNT(*) FROM fact_orders;")
    assert cur.fetchone()[0] == 1000

    # Check view execution
    cur.execute("SELECT total_revenue FROM v_executive_kpis;")
    assert cur.fetchone()[0] == 3520984

    conn.close()
