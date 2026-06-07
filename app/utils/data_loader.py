import pandas as pd
import streamlit as st
import os


BASE = "/home/lohitech/pharmacy_intel"

# NEW — works on any machine
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@st.cache_data(ttl=600)
def load_data():
    sales = pd.read_csv(
        f"{BASE}/data/processed/sales_clean.csv",
        parse_dates=["sales_date"]
    )
    inventory = pd.read_csv(
        f"{BASE}/data/processed/inventory_clean.csv",
        parse_dates=["expiry_date"]
    )
    products  = pd.read_csv(f"{BASE}/data/raw/products.csv")
    customers = pd.read_csv(f"{BASE}/data/processed/customers_clean.csv")
    branches  = pd.read_csv(f"{BASE}/data/raw/branches.csv")

    return sales, inventory, products, customers, branches


def get_kpis(sales, inventory):
    rev_2023 = sales[sales["year"] == 2023]["total_amount"].sum()
    rev_2024 = sales[sales["year"] == 2024]["total_amount"].sum()
    yoy      = ((rev_2024 - rev_2023) / rev_2023) * 100

    return {
        "total_revenue":     sales["total_amount"].sum(),
        "total_orders":      len(sales),
        "active_customers":  sales["customer_id"].nunique(),
        "avg_order_value":   sales["total_amount"].mean(),
        "inventory_value":   inventory["stock_value"].sum(),
        "low_stock_count":   int(inventory["is_low_stock"].sum()),
        "near_expiry_count": int(inventory["is_near_expiry"].sum()),
        "yoy_growth":        yoy,
    }