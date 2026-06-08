-- ============================================================
--  Retail Pharmacy Sales & Inventory Intelligence System
--  Advanced Analytics Queries
--  Techniques: CTEs, Window Functions, CASE WHEN, Subqueries
-- ============================================================


-- ── Q1: Top 10 Revenue-Generating Medicines ─────────────────
SELECT
    medicine_name,
    category,
    COUNT(invoice_id)           AS total_orders,
    SUM(quantity_sold)          AS total_units,
    ROUND(SUM(total_amount), 0) AS total_revenue
FROM sales
GROUP BY medicine_name, category
ORDER BY total_revenue DESC
LIMIT 10;


-- ── Q2: Branch Performance Scorecard ────────────────────────
SELECT
    b.branch_name,
    b.city,
    b.manager,
    COUNT(DISTINCT s.invoice_id)  AS total_transactions,
    COUNT(DISTINCT s.customer_id) AS unique_customers,
    ROUND(SUM(s.total_amount), 0) AS total_revenue,
    ROUND(AVG(s.total_amount), 0) AS avg_order_value,
    CASE
        WHEN SUM(s.total_amount) >= 4500000 THEN 'High Performer'
        WHEN SUM(s.total_amount) >= 3500000 THEN 'Mid Performer'
        ELSE                                     'Needs Attention'
    END AS performance_tier
FROM sales s
JOIN branches b ON s.branch_id = b.branch_id
GROUP BY b.branch_name, b.city, b.manager
ORDER BY total_revenue DESC;


-- ── Q3: Month-over-Month Revenue Growth (CTE + LAG) ─────────
WITH monthly_revenue AS (
    SELECT
        sales_month,
        ROUND(SUM(total_amount), 0) AS revenue
    FROM sales
    GROUP BY sales_month
),
with_growth AS (
    SELECT
        sales_month,
        revenue,
        LAG(revenue) OVER (ORDER BY sales_month) AS prev_month_revenue
    FROM monthly_revenue
)
SELECT
    sales_month,
    revenue,
    prev_month_revenue,
    CASE
        WHEN prev_month_revenue IS NULL THEN 'First Month'
        ELSE ROUND(
            (revenue - prev_month_revenue) * 100.0 / prev_month_revenue,
        1) || '%'
    END AS mom_growth
FROM with_growth
ORDER BY sales_month;


-- ── Q4: Top 3 Medicines per Category (Window Function) ───────
WITH medicine_revenue AS (
    SELECT
        medicine_name,
        category,
        ROUND(SUM(total_amount), 0) AS revenue
    FROM sales
    GROUP BY medicine_name, category
),
ranked AS (
    SELECT
        category,
        medicine_name,
        revenue,
        RANK() OVER (
            PARTITION BY category
            ORDER BY revenue DESC
        ) AS rank_in_category,
        ROUND(
            revenue * 100.0 / SUM(revenue) OVER (PARTITION BY category),
        1) AS pct_of_category
    FROM medicine_revenue
)
SELECT *
FROM ranked
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;


-- ── Q5: Customer RFM Scoring ─────────────────────────────────
WITH customer_stats AS (
    SELECT
        customer_id,
        COUNT(invoice_id)           AS frequency,
        ROUND(SUM(total_amount), 0) AS monetary,
        MAX(sales_date)             AS last_purchase
    FROM sales
    GROUP BY customer_id
)
SELECT
    customer_id,
    frequency,
    monetary,
    last_purchase,
    CASE
        WHEN frequency >= 25 AND monetary >= 15000 THEN 'Champion'
        WHEN frequency >= 20 AND monetary >= 10000 THEN 'Loyal'
        WHEN frequency >= 15                       THEN 'Regular'
        WHEN monetary  >= 10000                    THEN 'High Value'
        ELSE                                            'Occasional'
    END AS customer_segment
FROM customer_stats
ORDER BY monetary DESC
LIMIT 20;


-- ── Q6: Inventory Expiry Risk Analysis ───────────────────────
SELECT
    p.medicine_name,
    p.category,
    b.branch_name,
    i.batch_number,
    i.stock_quantity,
    i.expiry_date,
    i.stock_value,
    CASE
        WHEN julianday(i.expiry_date) - julianday('now') <= 30
            THEN 'URGENT — expires in 30 days'
        WHEN julianday(i.expiry_date) - julianday('now') <= 60
            THEN 'WARNING — expires in 60 days'
        WHEN julianday(i.expiry_date) - julianday('now') <= 90
            THEN 'MONITOR — expires in 90 days'
    END AS expiry_risk
FROM inventory i
JOIN products p ON i.product_id = p.product_id
JOIN branches b ON i.branch_id  = b.branch_id
WHERE julianday(i.expiry_date) - julianday('now') BETWEEN 1 AND 90
ORDER BY i.expiry_date ASC;


-- ── Q7: Above-Average Medicines (Subquery) ───────────────────
SELECT
    medicine_name,
    category,
    ROUND(SUM(total_amount), 0) AS total_revenue
FROM sales
GROUP BY medicine_name, category
HAVING SUM(total_amount) > (
    SELECT AVG(medicine_revenue)
    FROM (
        SELECT SUM(total_amount) AS medicine_revenue
        FROM sales
        GROUP BY medicine_name
    )
)
ORDER BY total_revenue DESC;
