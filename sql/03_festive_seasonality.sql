-- ==============================================================================
-- 03_festive_seasonality.sql
-- Gifting Occasions, Festive Peaks, and Month-over-Month Growth Analysis
-- ==============================================================================

-- 1. Revenue Contribution by Gifting Occasion
SELECT 
    occasion,
    COUNT(order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    SUM(revenue_inr) AS total_revenue_inr,
    ROUND(AVG(revenue_inr), 2) AS avg_order_value_inr,
    ROUND(100.0 * SUM(revenue_inr) / (SELECT SUM(revenue_inr) FROM fact_orders), 2) AS revenue_share_pct
FROM fact_orders
GROUP BY occasion
ORDER BY total_revenue_inr DESC;

-- 2. Monthly Revenue Trajectory with Month-over-Month (MoM) Growth Rates
WITH monthly_metrics AS (
    SELECT 
        strftime('%m', order_date) AS month_num,
        order_month,
        COUNT(order_id) AS order_count,
        SUM(revenue_inr) AS total_revenue_inr,
        ROUND(AVG(revenue_inr), 2) AS avg_order_value_inr
    FROM fact_orders
    GROUP BY strftime('%m', order_date), order_month
)
SELECT 
    month_num,
    order_month,
    order_count,
    total_revenue_inr,
    avg_order_value_inr,
    LAG(total_revenue_inr, 1) OVER (ORDER BY month_num) AS prev_month_revenue_inr,
    ROUND(
        100.0 * (total_revenue_inr - LAG(total_revenue_inr, 1) OVER (ORDER BY month_num)) / 
        LAG(total_revenue_inr, 1) OVER (ORDER BY month_num), 2
    ) AS mom_growth_pct
FROM monthly_metrics
ORDER BY month_num;

-- 3. Festive Surge vs Regular Season Performance Breakdown
SELECT 
    festive_season,
    COUNT(order_id) AS order_count,
    SUM(revenue_inr) AS total_revenue_inr,
    ROUND(AVG(revenue_inr), 2) AS avg_order_value_inr,
    ROUND(100.0 * SUM(revenue_inr) / (SELECT SUM(revenue_inr) FROM fact_orders), 2) AS revenue_share_pct
FROM fact_orders
GROUP BY festive_season
ORDER BY total_revenue_inr DESC;
