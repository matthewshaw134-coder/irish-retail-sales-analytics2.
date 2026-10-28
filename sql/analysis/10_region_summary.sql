-- 10_region_summary.sql
-- Sales by region and year, with each region's growth.
SELECT region,
       ROUND(SUM(CASE WHEN year = 2024 THEN net_sales END), 2) AS sales_2024,
       ROUND(SUM(CASE WHEN year = 2025 THEN net_sales END), 2) AS sales_2025,
       ROUND(100.0 * (SUM(CASE WHEN year = 2025 THEN net_sales END)
                    - SUM(CASE WHEN year = 2024 THEN net_sales END))
                    / SUM(CASE WHEN year = 2024 THEN net_sales END), 1) AS yoy_pct,
       COUNT(DISTINCT store_id) AS stores
FROM v_sales_lines
GROUP BY region
ORDER BY sales_2025 DESC;
