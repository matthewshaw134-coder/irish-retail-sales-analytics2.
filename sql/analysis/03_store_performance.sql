-- 03_store_performance.sql
-- Store league table for 2025 vs 2024: sales, growth, share, rank.
WITH store_year AS (
    SELECT store_id, store_name, town, region, channel, year,
           SUM(net_sales)            AS net_sales,
           SUM(gross_profit)         AS gross_profit,
           COUNT(DISTINCT order_id)  AS orders
    FROM v_sales_lines
    GROUP BY store_id, store_name, town, region, channel, year
),
pivoted AS (
    SELECT store_id, store_name, town, region, channel,
           SUM(CASE WHEN year = 2024 THEN net_sales END)    AS sales_2024,
           SUM(CASE WHEN year = 2025 THEN net_sales END)    AS sales_2025,
           SUM(CASE WHEN year = 2025 THEN gross_profit END) AS gp_2025,
           SUM(CASE WHEN year = 2025 THEN orders END)       AS orders_2025
    FROM store_year
    GROUP BY store_id, store_name, town, region, channel
)
SELECT
    RANK() OVER (ORDER BY sales_2025 DESC)                         AS rank_2025,
    store_id,
    CASE WHEN channel = 'Online' THEN 'Online Store'
         ELSE town || ' – ' || store_name END                     AS store,
    region,
    ROUND(sales_2024, 2)                                           AS sales_2024,
    ROUND(sales_2025, 2)                                           AS sales_2025,
    ROUND(100.0 * (sales_2025 - sales_2024) / sales_2024, 1)       AS yoy_pct,
    ROUND(100.0 * sales_2025 / SUM(sales_2025) OVER (), 1)         AS share_of_sales_pct,
    ROUND(100.0 * gp_2025 / sales_2025, 1)                         AS gross_margin_pct,
    ROUND(sales_2025 / orders_2025, 2)                             AS avg_order_value
FROM pivoted
ORDER BY rank_2025;
