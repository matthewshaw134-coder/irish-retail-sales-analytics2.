-- schema.sql
-- Star-style schema for the Clover & Co. retail sales database (SQLite).
-- Fact tables: orders (header) and order_items (lines).
-- Dimension tables: stores, products, customers, calendar.

DROP VIEW  IF EXISTS v_sales_lines;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS calendar;

CREATE TABLE stores (
    store_id     TEXT PRIMARY KEY,
    store_name   TEXT NOT NULL,
    town         TEXT NOT NULL,
    county       TEXT NOT NULL,
    region       TEXT NOT NULL,
    size_factor  REAL,
    opened_date  DATE
);

CREATE TABLE products (
    product_id    TEXT PRIMARY KEY,
    product_name  TEXT NOT NULL,
    category      TEXT NOT NULL,
    unit_price    REAL NOT NULL,   -- shelf price, incl. 23% VAT
    unit_cost     REAL NOT NULL    -- cost price, ex VAT
);

CREATE TABLE customers (
    customer_id   TEXT PRIMARY KEY,
    county        TEXT,
    age_band      TEXT,
    loyalty_tier  TEXT CHECK (loyalty_tier IN ('Bronze','Silver','Gold')),
    signup_date   DATE
);

CREATE TABLE calendar (
    date          DATE PRIMARY KEY,
    year          INTEGER,
    quarter       INTEGER,
    month         INTEGER,
    month_name    TEXT,
    iso_week      INTEGER,
    weekday       TEXT,
    is_weekend    INTEGER,
    is_bank_holiday INTEGER       -- Irish public holidays
);

CREATE TABLE orders (
    order_id        TEXT PRIMARY KEY,
    order_datetime  DATETIME NOT NULL,
    order_date      DATE NOT NULL REFERENCES calendar(date),
    store_id        TEXT NOT NULL REFERENCES stores(store_id),
    customer_id     TEXT REFERENCES customers(customer_id),  -- NULL = non-loyalty
    channel         TEXT NOT NULL,
    payment_method  TEXT NOT NULL
);

CREATE TABLE order_items (
    line_id       INTEGER PRIMARY KEY,
    order_id      TEXT NOT NULL REFERENCES orders(order_id),
    product_id    TEXT NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    unit_price    REAL NOT NULL,
    discount_pct  REAL NOT NULL DEFAULT 0,
    returned      INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_orders_date     ON orders(order_date);
CREATE INDEX idx_orders_store    ON orders(store_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_items_order     ON order_items(order_id);
CREATE INDEX idx_items_product   ON order_items(product_id);

-- One row per order line with all the business measures pre-calculated.
-- Net sales are reported EX VAT (Irish standard rate 23%), after discount,
-- and exclude returned lines.
CREATE VIEW v_sales_lines AS
SELECT
    oi.line_id,
    o.order_id,
    o.order_date,
    c.year, c.quarter, c.month, c.month_name, c.weekday, c.is_weekend,
    o.store_id, s.store_name, s.town, s.region,
    o.channel, o.payment_method, o.customer_id,
    p.product_id, p.product_name, p.category,
    oi.quantity,
    oi.discount_pct,
    oi.returned,
    ROUND(oi.quantity * oi.unit_price * (1 - oi.discount_pct), 2)            AS gross_sales_incl_vat,
    ROUND(oi.quantity * oi.unit_price * (1 - oi.discount_pct) / 1.23, 2)     AS sales_ex_vat,
    CASE WHEN oi.returned = 0
         THEN ROUND(oi.quantity * oi.unit_price * (1 - oi.discount_pct) / 1.23, 2)
         ELSE 0 END                                                          AS net_sales,
    CASE WHEN oi.returned = 0
         THEN ROUND(oi.quantity * (oi.unit_price * (1 - oi.discount_pct) / 1.23 - p.unit_cost), 2)
         ELSE 0 END                                                          AS gross_profit
FROM order_items oi
JOIN orders   o ON o.order_id   = oi.order_id
JOIN products p ON p.product_id = oi.product_id
JOIN stores   s ON s.store_id   = o.store_id
JOIN calendar c ON c.date       = o.order_date;
