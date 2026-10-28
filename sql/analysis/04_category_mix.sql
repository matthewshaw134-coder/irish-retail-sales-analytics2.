-- 04_category_mix.sql
-- Category performance in 2025: sales, margin, discounting and returns.
SELECT
    category,
    ROUND(SUM(net_sales), 2)                                        AS net_sales,
    ROUND(100.0 * SUM(net_sales) / SUM(SUM(net_sales)) OVER (), 1)  AS share_pct,
    ROUND(100.0 * SUM(gross_profit) / SUM(net_sales), 1)            AS gross_margin_pct,
    ROUND(100.0 * SUM(CASE WHEN discount_pct > 0 THEN sales_ex_vat ELSE 0 END)
          / SUM(sales_ex_vat), 1)                                   AS pct_sold_on_promo,
    ROUND(100.0 * SUM(CASE WHEN returned = 1 THEN sales_ex_vat ELSE 0 END)
          / SUM(sales_ex_vat), 1)                                   AS return_rate_pct
FROM v_sales_lines
WHERE year = 2025
GROUP BY category
ORDER BY net_sales DESC;
