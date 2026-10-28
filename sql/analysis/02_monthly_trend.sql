-- 02_monthly_trend.sql
-- Monthly net sales with the same month last year and YoY growth.
WITH monthly AS (
    SELECT year, month, month_name,
           ROUND(SUM(net_sales), 2)   AS net_sales,
           COUNT(DISTINCT order_id)   AS orders
    FROM v_sales_lines
    GROUP BY year, month, month_name
)
SELECT
    m.year, m.month, m.month_name,
    m.net_sales,
    m.orders,
    ly.net_sales                                                   AS net_sales_last_year,
    ROUND(100.0 * (m.net_sales - ly.net_sales) / ly.net_sales, 1)  AS yoy_pct,
    ROUND(SUM(m.net_sales) OVER (PARTITION BY m.year ORDER BY m.month), 2) AS ytd_net_sales
FROM monthly m
LEFT JOIN monthly ly
       ON ly.year = m.year - 1 AND ly.month = m.month
ORDER BY m.year, m.month;
