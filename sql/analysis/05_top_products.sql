-- 05_top_products.sql
-- Top 3 products in each category for 2025 (window function ranking).
WITH product_sales AS (
    SELECT category, product_name,
           SUM(CASE WHEN returned = 0 THEN quantity ELSE 0 END) AS units,
           ROUND(SUM(net_sales), 2)                             AS net_sales,
           ROUND(SUM(gross_profit), 2)                          AS gross_profit
    FROM v_sales_lines
    WHERE year = 2025
    GROUP BY category, product_name
),
ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY net_sales DESC) AS rank_in_category
    FROM product_sales
)
SELECT category, rank_in_category, product_name, units, net_sales, gross_profit
FROM ranked
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;
