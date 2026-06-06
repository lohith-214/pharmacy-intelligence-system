"""
Pharmacy Intelligence System
Database Setup — loads all 5 CSVs into SQLite
"""

import sqlite3
import pandas as pd
import os

DB_PATH  = "sql/pharmacy.db"
RAW_PATH = "data/raw/"
PROC_PATH = "data/processed/"

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_all_tables():

    conn = get_connection()

    print("=" * 50)
    print("  Loading CSVs into SQLite database")
    print("=" * 50)

    # ── Load each CSV into a database table ────────

    tables = [
        ("branches",  RAW_PATH  + "branches.csv",               None),
        ("products",  RAW_PATH  + "products.csv",                None),
        ("customers", PROC_PATH + "customers_clean.csv",         ["registration_date"]),
        ("sales",     PROC_PATH + "sales_clean.csv",             ["sales_date"]),
        ("inventory", PROC_PATH + "inventory_clean.csv",         ["expiry_date"]),
    ]

    for table_name, filepath, date_cols in tables:
        df = pd.read_csv(filepath, parse_dates=date_cols)
        df.to_sql(table_name, conn,
                  if_exists="replace",
                  index=False)

        print(f"  ✓ {table_name:<12}: {len(df):>7,} rows loaded")

    conn.close()
    print(f"\n  Database saved: {DB_PATH}")
    print("=" * 50)


def verify_database():

    conn = get_connection()
    print("\n\nVERIFYING DATABASE")
    print("=" * 50)

    tables = ["branches", "products", "customers", "sales", "inventory"]

    for table in tables:
        # cursor lets you run raw SQL
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
        count  = cursor.fetchone()[0]   # fetchone() gets the first row
        print(f"  {table:<12}: {count:>7,} rows")
        
    print("\n  Testing JOIN (sales + branches)...")
    test_query = """
        SELECT
            b.branch_name,
            COUNT(s.invoice_id)        AS total_orders,
            ROUND(SUM(s.total_amount)) AS total_revenue
        FROM sales s
        JOIN branches b ON s.branch_id = b.branch_id
        GROUP BY b.branch_name
        ORDER BY total_revenue DESC
        LIMIT 3
    """
    result = pd.read_sql(test_query, conn)
    print(result.to_string(index=False))

    conn.close()
    print("\n  ✓ Database is working correctly")


if __name__ == "__main__":
    load_all_tables()
    verify_database()