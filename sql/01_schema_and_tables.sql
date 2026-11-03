-- ==============================================================================
-- 01_schema_and_tables.sql
-- FNP E-Commerce Sales Analytics: DDL Schema, Relational Tables, & Indexes
-- ==============================================================================

-- 1. Dimension: Customers
DROP TABLE IF EXISTS dim_customers;
CREATE TABLE dim_customers (
    customer_id         VARCHAR(10) PRIMARY KEY,
    customer_name       VARCHAR(100) NOT NULL,
    customer_city       VARCHAR(100) NOT NULL,
    contact_number      BIGINT,
    email               VARCHAR(150),
    gender              VARCHAR(10) CHECK (gender IN ('Male', 'Female')),
    address             TEXT
);

-- 2. Dimension: Products
DROP TABLE IF EXISTS dim_products;
CREATE TABLE dim_products (
    product_id          INTEGER PRIMARY KEY,
    product_name        VARCHAR(100) NOT NULL,
    category            VARCHAR(50) NOT NULL,
    price_inr           INTEGER NOT NULL CHECK (price_inr > 0),
    target_occasion     VARCHAR(50),
    description         TEXT
);

-- 3. Fact: Orders
DROP TABLE IF EXISTS fact_orders;
CREATE TABLE fact_orders (
    order_id            INTEGER PRIMARY KEY,
    customer_id         VARCHAR(10) NOT NULL,
    product_id          INTEGER NOT NULL,
    quantity            INTEGER NOT NULL CHECK (quantity > 0),
    order_date          DATE NOT NULL,
    order_time          TIME NOT NULL,
    delivery_date       DATE NOT NULL,
    delivery_time       TIME NOT NULL,
    delivery_location   VARCHAR(100) NOT NULL,
    occasion            VARCHAR(50) NOT NULL,
    order_month         VARCHAR(10) NOT NULL,
    order_hour          INTEGER NOT NULL CHECK (order_hour BETWEEN 0 AND 23),
    delivery_lead_days  INTEGER NOT NULL CHECK (delivery_lead_days >= 0),
    delivery_hour       INTEGER NOT NULL CHECK (delivery_hour BETWEEN 0 AND 23),
    unit_price_inr      INTEGER NOT NULL CHECK (unit_price_inr > 0),
    revenue_inr         INTEGER NOT NULL CHECK (revenue_inr > 0),
    order_day_of_week   VARCHAR(15) NOT NULL,
    is_weekend          INTEGER NOT NULL CHECK (is_weekend IN (0, 1)),
    order_quarter       VARCHAR(5) NOT NULL,
    festive_season      VARCHAR(50) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id)
);

-- 4. Performance Indexes
CREATE INDEX idx_orders_customer ON fact_orders(customer_id);
CREATE INDEX idx_orders_product ON fact_orders(product_id);
CREATE INDEX idx_orders_date ON fact_orders(order_date);
CREATE INDEX idx_orders_occasion ON fact_orders(occasion);
CREATE INDEX idx_orders_month ON fact_orders(order_month);
CREATE INDEX idx_orders_quarter ON fact_orders(order_quarter);
