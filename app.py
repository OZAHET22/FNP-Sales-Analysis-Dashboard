"""
Streamlit Web Application: FNP Sales Analytics & Business Intelligence Dashboard
Run with: streamlit run app.py
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set Page Config
st.set_page_config(
    page_title="FNP Sales Analysis Dashboard",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.8rem;
        color: #0284c7;
        font-weight: 700;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    csv_path = Path("data/processed/fnp_sales_cleaned.csv")
    if not csv_path.exists():
        from src.data_pipeline import clean_and_transform
        return clean_and_transform()
    df = pd.read_csv(csv_path)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["delivery_date"] = pd.to_datetime(df["delivery_date"])
    return df


df = load_data()

# Sidebar Filters
st.sidebar.image("https://img.icons8.com/color/96/shop--v1.png", width=64)
st.sidebar.title("Dashboard Slicers")

# Date Filter
min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()
date_range = st.sidebar.date_input("Order Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Occasion Filter
occasions = ["All"] + sorted(df["occasion"].unique().tolist())
selected_occasion = st.sidebar.selectbox("Filter Occasion", occasions)

# Category Filter
categories = ["All"] + sorted(df["category"].unique().tolist())
selected_category = st.sidebar.selectbox("Filter Category", categories)

# Gender Filter
genders = ["All"] + sorted(df["gender"].unique().tolist())
selected_gender = st.sidebar.selectbox("Filter Customer Gender", genders)

# Apply Filters
filtered_df = df.copy()

if len(date_range) == 2:
    start_d, end_d = date_range
    filtered_df = filtered_df[
        (filtered_df["order_date"].dt.date >= start_d) &
        (filtered_df["order_date"].dt.date <= end_d)
    ]

if selected_occasion != "All":
    filtered_df = filtered_df[filtered_df["occasion"] == selected_occasion]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

if selected_gender != "All":
    filtered_df = filtered_df[filtered_df["gender"] == selected_gender]

# Main Header
st.title("🌸 Ferns N Petals (FNP) — Sales Analysis Dashboard")
st.markdown("*Executive Business Intelligence & Gifting Performance Scorecard (FY 2023)*")

# Top KPI Scorecards
k1, k2, k3, k4 = st.columns(4)

total_revenue = filtered_df["revenue_inr"].sum()
total_orders = len(filtered_df)
avg_delivery = filtered_df["delivery_lead_days"].mean() if total_orders > 0 else 0
avg_rev = filtered_df["revenue_inr"].mean() if total_orders > 0 else 0

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Revenue</div>
        <div class="metric-value">₹{total_revenue:,.0f}</div>
        <div class="metric-sub">₹{total_revenue/1e6:.2f}M GMV</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Orders</div>
        <div class="metric-value">{total_orders:,}</div>
        <div class="metric-sub">Transacted Baskets</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Delivery Time</div>
        <div class="metric-value">{avg_delivery:.2f} d</div>
        <div class="metric-sub">Order to Delivery Lead</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Order Value (AOV)</div>
        <div class="metric-value">₹{avg_rev:,.0f}</div>
        <div class="metric-sub">Mean Basket Spend</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Charts Row 1
c1, c2 = st.columns([3, 2])

month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
monthly_rev = filtered_df.groupby("order_month")["revenue_inr"].sum().reindex(month_order).fillna(0).reset_index()

with c1:
    fig_monthly = px.line(
        monthly_rev,
        x="order_month",
        y="revenue_inr",
        title="<b>Monthly Gross Revenue Trajectory (Festive Peaks)</b>",
        markers=True,
        labels={"order_month": "Month", "revenue_inr": "Gross Revenue (₹)"},
        color_discrete_sequence=["#0284c7"]
    )
    fig_monthly.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_monthly, use_container_width=True)

with c2:
    occ_rev = filtered_df.groupby("occasion")["revenue_inr"].sum().sort_values(ascending=True).reset_index()
    fig_occ = px.bar(
        occ_rev,
        x="revenue_inr",
        y="occasion",
        orientation="h",
        title="<b>Revenue by Gifting Occasion</b>",
        labels={"revenue_inr": "Revenue (₹)", "occasion": "Occasion"},
        color_discrete_sequence=["#0ea5e9"]
    )
    fig_occ.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_occ, use_container_width=True)

# Charts Row 2
c3, c4 = st.columns([3, 2])

with c3:
    cat_rev = filtered_df.groupby("category")["revenue_inr"].sum().sort_values(ascending=False).reset_index()
    fig_cat = px.bar(
        cat_rev,
        x="category",
        y="revenue_inr",
        title="<b>Revenue by Product Category</b>",
        labels={"category": "Category", "revenue_inr": "Revenue (₹)"},
        color="revenue_inr",
        color_continuous_scale="Blues"
    )
    fig_cat.update_layout(template="plotly_white", coloraxis_showscale=False, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_cat, use_container_width=True)

with c4:
    gender_rev = filtered_df.groupby("gender")["revenue_inr"].sum().reset_index()
    fig_gender = px.pie(
        gender_rev,
        names="gender",
        values="revenue_inr",
        hole=0.55,
        title="<b>Revenue Share by Customer Gender</b>",
        color_discrete_sequence=["#0284c7", "#38bdf8"]
    )
    fig_gender.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gender, use_container_width=True)

# Charts Row 3
c5, c6 = st.columns([1, 1])

with c5:
    top_p = filtered_df.groupby("product_name")["revenue_inr"].sum().nlargest(10).sort_values(ascending=True).reset_index()
    fig_p = px.bar(
        top_p,
        x="revenue_inr",
        y="product_name",
        orientation="h",
        title="<b>Top 10 Product SKUs by Total Revenue</b>",
        labels={"revenue_inr": "Revenue (₹)", "product_name": "Product SKU"},
        color_discrete_sequence=["#0d9488"]
    )
    fig_p.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_p, use_container_width=True)

with c6:
    top_cities = filtered_df["customer_city"].value_counts().head(10).sort_values(ascending=True).reset_index()
    top_cities.columns = ["city", "orders"]
    fig_cities = px.bar(
        top_cities,
        x="orders",
        y="city",
        orientation="h",
        title="<b>Top 10 Customer Cities by Order Volume</b>",
        labels={"orders": "Confirmed Orders", "city": "City"},
        color_discrete_sequence=["#6366f1"]
    )
    fig_cities.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_cities, use_container_width=True)

# Tabular Data Explorer
with st.expander("🔍 Filtered Transaction Explorer & Data Download"):
    st.dataframe(filtered_df[[
        "order_id", "order_date", "customer_name", "customer_city",
        "gender", "product_name", "category", "quantity", "unit_price_inr",
        "revenue_inr", "occasion", "delivery_lead_days"
    ]].head(100), use_container_width=True)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Dataset as CSV",
        data=csv_data,
        file_name="fnp_sales_filtered.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("**Author:** Het Oza | Professional Data Analyst & Analytics Engineer | [GitHub](https://github.com/OZAHET22)")
