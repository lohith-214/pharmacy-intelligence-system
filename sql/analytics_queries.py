"""
Pharmacy Intelligence System
SQL Analytics Queries
Techniques covered:
  - Basic SELECT, GROUP BY, ORDER BY
  - JOIN across multiple tables
  - CASE WHEN for business logic
  - Subqueries
  - CTEs (Common Table Expressions)
  - Window Functions
"""

import sqlite3
import pandas as pd

DB_PATH = "sql/pharmacy.db"

def run_query(sql, description):
    """Helper — runs any SQL and prints the result neatly."""
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql(sql, conn)
    conn.close()

    print("\n" + "=" * 55)
    print(f"  {description}")
    print("=" * 55)
    print(df.to_string(index=False))
    return df

# TECHNIQUE 1: GROUP BY + ORDER BY


run_query("""
    SELECT
        medicine_name,
        category,
        COUNT(invoice_id)            AS total_orders,
        SUM(quantity_sold)           AS total_units,
        ROUND(SUM(total_amount), 0)  AS total_revenue
    FROM sales
    GROUP BY medicine_name, category
    ORDER BY total_revenue DESC
    LIMIT 10
""", "TOP 10 MEDICINES BY REVENUE")


# TECHNIQUE 2: JOIN

run_query("""
    SELECT
        b.branch_name,
        b.city,
        b.manager,
        COUNT(s.invoice_id)            AS total_orders,
        COUNT(DISTINCT s.customer_id)  AS unique_customers,
        ROUND(SUM(s.total_amount), 0)  AS total_revenue,
        ROUND(AVG(s.total_amount), 0)  AS avg_order_value
    FROM sales s
    JOIN branches b ON s.branch_id = b.branch_id
    GROUP BY b.branch_name, b.city, b.manager
    ORDER BY total_revenue DESC
""", "BRANCH PERFORMANCE (JOIN)")

# TECHNIQUE 3: CASE WHEN

run_query("""
    SELECT
        b.branch_name,
        ROUND(SUM(s.total_amount), 0) AS total_revenue,
        CASE
            WHEN SUM(s.total_amount) >= 4500000 THEN 'High Performer'
            WHEN SUM(s.total_amount) >= 3500000 THEN 'Mid Performer'
            ELSE                                     'Needs Attention'
        END AS performance_tier
    FROM sales s
    JOIN branches b ON s.branch_id = b.branch_id
    GROUP BY b.branch_name
    ORDER BY total_revenue DESC
""", "BRANCH PERFORMANCE TIERS (CASE WHEN)")

# TECHNIQUE 4: SUBQUERY

run_query("""
    SELECT
        medicine_name,
        category,
        ROUND(SUM(total_amount), 0) AS total_revenue
    FROM sales
    GROUP BY medicine_name, category
    HAVING SUM(total_amount) > (
        -- This inner query calculates the average medicine revenue
        SELECT AVG(medicine_revenue)
        FROM (
            SELECT SUM(total_amount) AS medicine_revenue
            FROM sales
            GROUP BY medicine_name
        )
    )
    ORDER BY total_revenue DESC
""", "ABOVE-AVERAGE MEDICINES (SUBQUERY)")


# TECHNIQUE 5: CTE (Common Table Expression)

run_query("""
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
    ORDER BY sales_month
""", "MONTH-OVER-MONTH GROWTH (CTE + LAG)")

# TECHNIQUE 6: WINDOW FUNCTIONS

run_query("""
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
    ORDER BY category, rank_in_category

""", "TOP 3 MEDICINES PER CATEGORY (WINDOW FUNCTION)")

# BONUS: INVENTORY ALERT QUERY

run_query("""
    SELECT
        p.medicine_name,
        p.category,
        b.branch_name,
        i.stock_quantity,
        i.reorder_level,
        i.stock_status,
        (i.reorder_level - i.stock_quantity) AS units_needed,
        i.supplier_name
    FROM inventory i
    JOIN products p  ON i.product_id = p.product_id
    JOIN branches b  ON i.branch_id  = b.branch_id
    WHERE i.stock_status IN ('Low Stock', 'Critical', 'Out of Stock')
    ORDER BY i.stock_quantity ASC
""", "INVENTORY ALERT — ITEMS NEEDING REORDER")


print("\n\n All queries complete")