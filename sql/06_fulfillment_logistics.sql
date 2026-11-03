-- ==============================================================================
-- 06_fulfillment_logistics.sql
-- Logistics Fulfillment, Turnaround Times, and Dispatch Time Windows
-- ==============================================================================

-- 1. Delivery Turnaround Time Distribution
SELECT 
    delivery_lead_days,
    COUNT(order_id) AS order_count,
    ROUND(100.0 * COUNT(order_id) / (SELECT COUNT(*) FROM fact_orders), 2) AS order_share_pct,
    SUM(revenue_inr) AS associated_revenue_inr
FROM fact_orders
GROUP BY delivery_lead_days
ORDER BY delivery_lead_days ASC;

-- 2. Delivery Speed Performance Tiers
SELECT 
    CASE 
        WHEN delivery_lead_days <= 2 THEN 'Express Turnaround (1-2 Days)'
        WHEN delivery_lead_days BETWEEN 3 AND 5 THEN 'Standard Delivery (3-5 Days)'
        ELSE 'Extended Fulfillment (6-10 Days)'
    END AS fulfillment_tier,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(delivery_lead_days), 2) AS avg_turnaround_days,
    SUM(revenue_inr) AS total_revenue_inr,
    ROUND(100.0 * COUNT(order_id) / (SELECT COUNT(*) FROM fact_orders), 2) AS order_percentage
FROM fact_orders
GROUP BY 
    CASE 
        WHEN delivery_lead_days <= 2 THEN 'Express Turnaround (1-2 Days)'
        WHEN delivery_lead_days BETWEEN 3 AND 5 THEN 'Standard Delivery (3-5 Days)'
        ELSE 'Extended Fulfillment (6-10 Days)'
    END
ORDER BY total_orders DESC;

-- 3. Order Placement Velocity by Hour of Day (0 - 23)
SELECT 
    order_hour,
    COUNT(order_id) AS orders_placed,
    SUM(revenue_inr) AS hourly_revenue_inr,
    ROUND(AVG(revenue_inr), 2) AS avg_order_value_inr
FROM fact_orders
GROUP BY order_hour
ORDER BY order_hour ASC;

-- 4. Day of Week Ordering Rhythm
SELECT 
    order_day_of_week,
    COUNT(order_id) AS order_count,
    SUM(revenue_inr) AS day_revenue_inr,
    ROUND(AVG(revenue_inr), 2) AS avg_ticket_size_inr,
    ROUND(100.0 * SUM(revenue_inr) / (SELECT SUM(revenue_inr) FROM fact_orders), 2) AS revenue_share_pct
FROM fact_orders
GROUP BY order_day_of_week
ORDER BY day_revenue_inr DESC;
