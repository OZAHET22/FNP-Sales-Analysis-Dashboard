-- ==============================================================================
-- 04_product_and_category.sql
-- Product Category Mix, Top Revenue Drivers, and Pareto (80/20) Analysis
-- ==============================================================================

-- 1. Product Category Performance
SELECT 
    p.category,
    COUNT(o.order_id) AS order_count,
    SUM(o.quantity) AS total_units_sold,
    SUM(o.revenue_inr) AS total_revenue_inr,
    ROUND(AVG(o.revenue_inr), 2) AS avg_order_value_inr,
    ROUND(100.0 * SUM(o.revenue_inr) / (SELECT SUM(revenue_inr) FROM fact_orders), 2) AS revenue_share_pct
FROM fact_orders o
JOIN dim_products p ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue_inr DESC;

-- 2. Top 10 Best-Selling Product SKUs
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.price_inr AS catalog_price,
    COUNT(o.order_id) AS total_orders,
    SUM(o.quantity) AS total_quantity_sold,
    SUM(o.revenue_inr) AS total_revenue_inr,
    ROUND(100.0 * SUM(o.revenue_inr) / (SELECT SUM(revenue_inr) FROM fact_orders), 2) AS revenue_contribution_pct
FROM fact_orders o
JOIN dim_products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.price_inr
ORDER BY total_revenue_inr DESC
LIMIT 10;

-- 3. Pareto Analysis: Cumulative Revenue Contribution by SKU
WITH product_revenue AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        SUM(o.revenue_inr) AS sku_revenue
    FROM fact_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category
),
ranked_skus AS (
    SELECT 
        product_id,
        product_name,
        category,
        sku_revenue,
        ROW_NUMBER() OVER (ORDER BY sku_revenue DESC) AS sku_rank,
        SUM(sku_revenue) OVER (ORDER BY sku_revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_revenue_sum,
        (SELECT SUM(revenue_inr) FROM fact_orders) AS total_catalog_revenue
    FROM product_revenue
)
SELECT 
    sku_rank,
    product_name,
    category,
    sku_revenue,
    running_revenue_sum,
    ROUND(100.0 * running_revenue_sum / total_catalog_revenue, 2) AS cumulative_revenue_pct
FROM ranked_skus
LIMIT 20;
