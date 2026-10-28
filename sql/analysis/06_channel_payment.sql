-- 06_channel_payment.sql
-- How customers pay, split by channel, 2025.
SELECT
    channel,
    payment_method,
    COUNT(*)                                                        AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY channel), 1) AS share_of_channel_pct
FROM orders o
WHERE substr(order_date, 1, 4) = '2025'
GROUP BY channel, payment_method
ORDER BY channel, orders DESC;
