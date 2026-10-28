-- 01_kpi_summary.sql
-- Headline KPIs per year with year-on-year change (window function LAG).
WITH yearly AS (
    SELECT
        year,
        ROUND(SUM(net_sales), 2)                                   AS net_sales,
        ROUND(SUM(gross_profit), 2)                                AS gross_profit,
        COUNT(DISTINCT order_id)                                   AS orders,
        SUM(CASE WHEN returned = 0 THEN quantity ELSE 0 END)       AS units_sold,
        ROUND(SUM(CASE WHEN returned = 1 THEN sales_ex_vat ELSE 0 END), 2) AS returns_value,
        ROUND(SUM(sales_ex_vat), 2)                                AS sales_before_returns
    FROM v_sales_lines
    GROUP BY year
)
SELECT
    year,
    net_sales,
    gross_profit,
    ROUND(100.0 * gross_profit / net_sales, 1)                     AS gross_margin_pct,
    orders,
    ROUND(net_sales / orders, 2)                                   AS avg_order_value,
    units_sold,
    ROUND(100.0 * returns_value / sales_before_returns, 1)         AS return_rate_pct,
    ROUND(100.0 * (net_sales - LAG(net_sales) OVER (ORDER BY year))
          / LAG(net_sales) OVER (ORDER BY year), 1)                AS net_sales_yoy_pct,
    ROUND(100.0 * (orders - LAG(orders) OVER (ORDER BY year))
          / LAG(orders) OVER (ORDER BY year), 1)                   AS orders_yoy_pct
FROM yearly
ORDER BY year;
