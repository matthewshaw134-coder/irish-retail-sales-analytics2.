-- 08_customer_rfm.sql
-- RFM (Recency, Frequency, Monetary) segmentation of loyalty customers,
-- scored 1-5 with NTILE and grouped into named segments.
WITH cust AS (
    SELECT customer_id,
           JULIANDAY('2025-12-31') - JULIANDAY(MAX(order_date)) AS recency_days,
           COUNT(DISTINCT order_id)                             AS frequency,
           SUM(net_sales)                                       AS monetary
    FROM v_sales_lines
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
scored AS (
    SELECT *,
           NTILE(5) OVER (ORDER BY recency_days DESC) AS r,   -- recent = 5
           NTILE(5) OVER (ORDER BY frequency)        AS f,
           NTILE(5) OVER (ORDER BY monetary)         AS m
    FROM cust
),
segmented AS (
    SELECT *,
           CASE
               WHEN r >= 4 AND f >= 4 AND m >= 4 THEN 'Champions'
               WHEN r >= 3 AND f >= 3            THEN 'Loyal'
               WHEN r >= 4 AND f <= 2            THEN 'New / Promising'
               WHEN r <= 2 AND f >= 3            THEN 'At Risk'
               WHEN r <= 2 AND f <= 2            THEN 'Lapsed'
               ELSE 'Needs Attention'
           END AS segment
    FROM scored
)
SELECT segment,
       COUNT(*)                                             AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)   AS pct_customers,
       ROUND(SUM(monetary), 2)                              AS total_sales,
       ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 1) AS pct_sales,
       ROUND(AVG(frequency), 1)                             AS avg_orders,
       ROUND(AVG(monetary), 2)                              AS avg_spend,
       ROUND(AVG(recency_days), 0)                          AS avg_days_since_last_order
FROM segmented
GROUP BY segment
ORDER BY total_sales DESC;
