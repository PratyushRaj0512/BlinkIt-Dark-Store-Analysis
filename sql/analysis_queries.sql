-- ============================================================
-- BLINKIT LUCKNOW DARK STORE ANALYTICS -- CORE SQL QUERIES
-- Database: blinkit_lucknow.db (SQLite)
-- ============================================================

-- 1. TOTAL LOST REVENUE BY STORE
SELECT
    s.store_name,
    s.zone,
    ROUND(SUM(o.lost_revenue), 0)      AS total_lost_revenue,
    ROUND(SUM(o.revenue), 0)           AS total_realized_revenue,
    ROUND(SUM(o.lost_revenue) * 100.0 / (SUM(o.revenue) + SUM(o.lost_revenue)), 2) AS pct_revenue_leaked
FROM orders o
JOIN stores s ON o.store_id = s.store_id
GROUP BY s.store_name, s.zone
ORDER BY total_lost_revenue DESC;

-- 2. STOCKOUT RATE BY SKU x STORE
SELECT
    s.store_name,
    p.sku_name,
    p.category,
    COUNT(*)                                            AS demand_events,
    SUM(o.stockout_flag)                                AS stockout_events,
    ROUND(SUM(o.stockout_flag) * 100.0 / COUNT(*), 2)   AS stockout_rate_pct
FROM orders o
JOIN stores s   ON o.store_id = s.store_id
JOIN products p ON o.sku_id = p.sku_id
GROUP BY s.store_name, p.sku_name, p.category
HAVING stockout_rate_pct > 15
ORDER BY stockout_rate_pct DESC
LIMIT 20;

-- 3. HOURLY DEMAND CURVE
SELECT
    CAST(strftime('%H', timestamp) AS INTEGER) AS hour_of_day,
    SUM(demand_qty)                            AS total_demand,
    SUM(lost_qty)                              AS total_lost_units,
    ROUND(SUM(lost_qty) * 100.0 / SUM(demand_qty), 2) AS lost_pct
FROM orders
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- 4. WEEKEND VS WEEKDAY DEMAND UPLIFT
SELECT
    CASE WHEN strftime('%w', timestamp) IN ('0','6') THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    ROUND(AVG(demand_qty), 2)  AS avg_demand_per_event,
    SUM(demand_qty)            AS total_demand
FROM orders
GROUP BY day_type;

-- 5. CATEGORY-LEVEL REVENUE CONTRIBUTION
SELECT
    p.category,
    ROUND(SUM(o.revenue), 0)        AS revenue,
    ROUND(SUM(o.lost_revenue), 0)   AS lost_revenue,
    ROUND(SUM(o.revenue) * 100.0 / (SELECT SUM(revenue) FROM orders), 2) AS pct_of_total_revenue
FROM orders o
JOIN products p ON o.sku_id = p.sku_id
GROUP BY p.category
ORDER BY revenue DESC;

-- 6. WINDOW FUNCTION: 7-DAY ROLLING AVERAGE DEMAND PER STORE
WITH daily_demand AS (
    SELECT store_id, DATE(timestamp) AS order_date, SUM(demand_qty) AS daily_demand
    FROM orders
    GROUP BY store_id, order_date
)
SELECT
    store_id, order_date, daily_demand,
    ROUND(AVG(daily_demand) OVER (
        PARTITION BY store_id ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 1) AS rolling_7day_avg_demand
FROM daily_demand
ORDER BY store_id, order_date;

-- 7. RANK STORES BY STOCKOUT SEVERITY
SELECT
    store_name, stockout_rate_pct,
    RANK() OVER (ORDER BY stockout_rate_pct DESC) AS stockout_rank
FROM (
    SELECT s.store_name, ROUND(SUM(o.stockout_flag) * 100.0 / COUNT(*), 2) AS stockout_rate_pct
    FROM orders o JOIN stores s ON o.store_id = s.store_id
    GROUP BY s.store_name
) t;

-- 8. OVER-STOCKED vs UNDER-STOCKED SKUs
SELECT
    p.sku_name,
    ROUND(AVG(i.opening_stock), 1) AS avg_opening_stock,
    ROUND(AVG(o.demand_qty) * 24, 1) AS est_avg_daily_demand,
    ROUND(AVG(i.opening_stock) / NULLIF(AVG(o.demand_qty) * 24, 0), 2) AS stock_to_demand_ratio
FROM inventory_snapshot i
JOIN products p ON i.sku_id = p.sku_id
JOIN orders o ON o.sku_id = i.sku_id AND o.store_id = i.store_id
GROUP BY p.sku_name
ORDER BY stock_to_demand_ratio DESC;