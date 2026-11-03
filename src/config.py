"""
Global Project Configuration and Path Constants
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ASSETS_DIR = PROJECT_ROOT / "assets"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
SQL_DIR = PROJECT_ROOT / "sql"

# Raw Data Files
RAW_CUSTOMERS_CSV = RAW_DATA_DIR / "customers.csv"
RAW_ORDERS_CSV = RAW_DATA_DIR / "orders.csv"
RAW_PRODUCTS_CSV = RAW_DATA_DIR / "products.csv"
EXCEL_WORKBOOK = PROJECT_ROOT / "Sales_Dashbaoard_Using_Excel.xlsx"

# Processed Data Files
CLEANED_SALES_CSV = PROCESSED_DATA_DIR / "fnp_sales_cleaned.csv"
SQLITE_DB_PATH = PROCESSED_DATA_DIR / "fnp_sales.db"
KPI_SUMMARY_JSON = PROCESSED_DATA_DIR / "kpi_summary.json"
CATEGORY_KPI_CSV = PROCESSED_DATA_DIR / "category_kpi_summary.csv"

# Color Palette for Visualizations
PALETTE = {
    "primary": "#0284c7",       # Vibrant Sky Blue
    "secondary": "#0ea5e9",     # Ocean Blue
    "accent": "#f59e0b",        # Amber Gold
    "success": "#10b981",       # Emerald Green
    "danger": "#ef4444",        # Coral Red
    "dark": "#0f172a",          # Slate Navy
    "light": "#f8fafc",         # Off-white
    "gray": "#64748b",          # Slate Gray
}

# Ordered Month Names
MONTH_ORDER = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

# Ordered Days of Week
DAY_ORDER = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]
