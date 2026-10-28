-- 11_monthly_category.sql
-- Monthly net sales per category (feeds the dashboard's category filter).
SELECT year, month, category, ROUND(SUM(net_sales), 2) AS net_sales
FROM v_sales_lines
GROUP BY year, month, category
ORDER BY year, month, category;
