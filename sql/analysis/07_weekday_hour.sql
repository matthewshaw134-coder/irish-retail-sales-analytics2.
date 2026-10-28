-- 07_weekday_hour.sql
-- In-store footfall heatmap: average orders per day by weekday and hour (2025).
WITH by_hour AS (
    SELECT c.weekday,
           CAST(strftime('%w', o.order_date) AS INTEGER)            AS dow,   -- 0 = Sunday
           CAST(strftime('%H', o.order_datetime) AS INTEGER)        AS hour,
           COUNT(*)                                                 AS orders
    FROM orders o
    JOIN calendar c ON c.date = o.order_date
    WHERE o.channel = 'In-store' AND c.year = 2025
    GROUP BY c.weekday, dow, hour
),
days AS (
    SELECT weekday, COUNT(*) AS n_days
    FROM calendar WHERE year = 2025 GROUP BY weekday
)
SELECT b.weekday, b.dow, b.hour,
       ROUND(1.0 * b.orders / d.n_days, 1) AS avg_orders_per_day
FROM by_hour b
JOIN days d ON d.weekday = b.weekday
ORDER BY (b.dow + 6) % 7, b.hour;     -- Monday first
