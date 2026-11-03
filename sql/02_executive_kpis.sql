-- ==============================================================================
-- 02_executive_kpis.sql
-- High-Level Executive Scorecard and Baseline Business Metrics
-- ==============================================================================

-- 1. Global Executive Scorecard
SELECT 
    COUNT(order_id) AS total_orders,
    SUM(revenue_inr) AS total_revenue_inr,
    SUM(quantity) AS total_units_sold,
    ROUND(AVG(revenue_inr), 2) AS average_order_value_inr,
    ROUND(AVG(delivery_lead_days), 2) AS avg_delivery_turnaround_days,
    COUNT(DISTINCT customer_id) AS total_active_customers,
    COUNT(DISTINCT product_id) AS total_active_skus,
    ROUND(CAST(SUM(revenue_inr) AS REAL) / COUNT(DISTINCT customer_id), 2) AS avg_customer_lifetime_value_inr,
    ROUND(CAST(COUNT(order_id) AS REAL) / COUNT(DISTINCT customer_id), 2) AS avg_orders_per_customer
FROM fact_orders;

-- 2. Gender Demographic Contribution
SELECT 
    c.gender,
    COUNT(o.order_id) AS order_count,
    SUM(o.quantity) AS total_units_sold,
    SUM(o.revenue_inr) AS total_revenue_inr,
    ROUND(AVG(o.revenue_inr), 2) AS avg_basket_size_inr,
    ROUND(100.0 * SUM(o.revenue_inr) / (SELECT SUM(revenue_inr) FROM fact_orders), 2) AS revenue_share_pct
FROM fact_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
GROUP BY c.gender
ORDER BY total_revenue_inr DESC;

-- 3. Weekend vs Weekday Revenue Velocity
SELECT 
    CASE WHEN is_weekend = 1 THEN 'Weekend (Sat-Sun)' ELSE 'Weekday (Mon-Fri)' END AS sales_period,
    COUNT(order_id) AS total_orders,
    SUM(revenue_inr) AS total_revenue_inr,
    ROUND(AVG(revenue_inr), 2) AS avg_order_value_inr,
    ROUND(100.0 * SUM(revenue_inr) / (SELECT SUM(revenue_inr) FROM fact_orders), 2) AS revenue_share_pct
FROM fact_orders
GROUP BY is_weekend
ORDER BY is_weekend DESC;
