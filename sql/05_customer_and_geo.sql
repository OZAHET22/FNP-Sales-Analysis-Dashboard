-- ==============================================================================
-- 05_customer_and_geo.sql
-- Geographic Market Penetration and Customer Segmentation (RFM Analysis)
-- ==============================================================================

-- 1. Top 15 Customer Cities by Order Volume and Spend
SELECT 
    c.customer_city,
    COUNT(o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_id) AS distinct_customers,
    SUM(o.revenue_inr) AS total_revenue_inr,
    ROUND(AVG(o.revenue_inr), 2) AS avg_revenue_per_order_inr,
    ROUND(CAST(SUM(o.revenue_inr) AS REAL) / COUNT(DISTINCT c.customer_id), 2) AS avg_revenue_per_customer_inr
FROM fact_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_city
ORDER BY total_orders DESC
LIMIT 15;

-- 2. Customer RFM Metric Calculation (Recency, Frequency, Monetary)
WITH rfm_base AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.customer_city,
        c.gender,
        JULIANDAY('2023-12-31') - JULIANDAY(MAX(o.order_date)) AS recency_days,
        COUNT(o.order_id) AS frequency_orders,
        SUM(o.revenue_inr) AS monetary_total_spend_inr
    FROM dim_customers c
    JOIN fact_orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name, c.customer_city, c.gender
)
SELECT 
    customer_id,
    customer_name,
    customer_city,
    gender,
    CAST(recency_days AS INT) AS recency_days,
    frequency_orders,
    monetary_total_spend_inr,
    CASE 
        WHEN monetary_total_spend_inr >= 45000 AND frequency_orders >= 12 THEN 'Tier 1 - VIP Champions'
        WHEN monetary_total_spend_inr >= 35000 THEN 'Tier 2 - High Value Loyalists'
        WHEN frequency_orders >= 9 THEN 'Tier 3 - Regular Shoppers'
        ELSE 'Tier 4 - Standard Shoppers'
    END AS customer_segment
FROM rfm_base
ORDER BY monetary_total_spend_inr DESC
LIMIT 20;

-- 3. Top 10 High-Value Spenders (VIP Customers)
SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_city,
    c.gender,
    COUNT(o.order_id) AS lifetime_orders,
    SUM(o.revenue_inr) AS lifetime_spend_inr,
    ROUND(AVG(o.revenue_inr), 2) AS avg_order_value_inr
FROM fact_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_city, c.gender
ORDER BY lifetime_spend_inr DESC
LIMIT 10;
