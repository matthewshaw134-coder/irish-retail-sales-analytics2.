-- 09_peak_trading.sql
-- Key Irish retail trading periods compared across both years.
-- Black Friday: 29 Nov 2024 / 28 Nov 2025 (Fri-Mon incl. Cyber Monday).
WITH periods AS (
    SELECT order_date, year, net_sales, order_id,
        CASE
            WHEN order_date BETWEEN '2024-11-29' AND '2024-12-02'
              OR order_date BETWEEN '2025-11-28' AND '2025-12-01'
                 THEN 'Black Friday weekend'
            WHEN month = 12 AND CAST(substr(order_date, 9, 2) AS INT) BETWEEN 15 AND 24
                 THEN 'Christmas final 10 days'
            WHEN month = 3 AND CAST(substr(order_date, 9, 2) AS INT) BETWEEN 15 AND 18
                 THEN 'St Patrick''s weekend'
            WHEN month = 8
                 THEN 'Back to school (August)'
        END AS period
    FROM v_sales_lines
),
baseline AS (   -- average daily sales across the whole year, for comparison
    SELECT year, SUM(net_sales) / COUNT(DISTINCT order_date) AS avg_day
    FROM v_sales_lines GROUP BY year
)
SELECT p.period, p.year,
       COUNT(DISTINCT p.order_date)                                 AS trading_days,
       ROUND(SUM(p.net_sales), 2)                                   AS net_sales,
       ROUND(SUM(p.net_sales) / COUNT(DISTINCT p.order_date), 2)    AS sales_per_day,
       ROUND(SUM(p.net_sales) / COUNT(DISTINCT p.order_date) / b.avg_day, 2) AS x_normal_day
FROM periods p
JOIN baseline b ON b.year = p.year
WHERE p.period IS NOT NULL
GROUP BY p.period, p.year
ORDER BY x_normal_day DESC, p.year;
