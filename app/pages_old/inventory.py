"""
Inventory Analytics Page — stock alerts and expiry risk.
"""

import streamlit as st
import plotly.express as px
import pandas as pd

DANGER  = "#E74C3C"
WARNING = "#F39C12"
SUCCESS = "#27AE60"
PRIMARY = "#0F4C75"


def show(sales, inventory, products, customers, branches):

    st.markdown("# 📦 Inventory Analytics")
    st.divider()

    # Merge product and branch names into inventory for display
    inv = (
        inventory
        .merge(products[["product_id", "medicine_name", "category"]], on="product_id")
        .merge(branches[["branch_id", "branch_name"]], on="branch_id")
    )

    # ── KPIs ───────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Stock Value",   f"₹{inv['stock_value'].sum()/1e6:.2f}M")
    c2.metric("Total SKUs",          f"{inv['product_id'].nunique()}")
    c3.metric("Low / Critical Stock",f"{int(inv['is_low_stock'].sum())}",
              delta="⚠ Needs action", delta_color="inverse")
    c4.metric("Near Expiry (90d)",   f"{int(inv['is_near_expiry'].sum())}",
              delta="⚠ Review now",  delta_color="inverse")

    st.divider()

    # ── Two charts side by side ─────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Stock Status Overview")
        status = inv["stock_status"].value_counts().reset_index()
        status.columns = ["Status", "Count"]

        color_map = {
            "Adequate":     SUCCESS,
            "Low Stock":    WARNING,
            "Critical":     DANGER,
            "Out of Stock": "#8B0000",
        }
        fig = px.bar(
            status, x="Status", y="Count",
            color="Status",
            color_discrete_map=color_map,
            template="plotly_white",
        )
        fig.update_layout(height=350, showlegend=False, margin=dict(t=20))
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.markdown("### Stock Value by Category")
        cat_val = (
            inv.groupby("category")["stock_value"]
            .sum()
            .sort_values(ascending=True)
            .reset_index()
        )
        fig2 = px.bar(
            cat_val, x="stock_value", y="category",
            orientation="h",
            color="stock_value",
            color_continuous_scale=["#BDC3C7", PRIMARY],
            labels={"stock_value": "Stock Value (₹)", "category": ""},
            template="plotly_white",
        )
        fig2.update_xaxes(tickprefix="₹", tickformat=",.0f")
        fig2.update_layout(height=350, coloraxis_showscale=False,
                           margin=dict(t=20))
        st.plotly_chart(fig2, width='stretch')

    # ── Near-Expiry Alert Table ─────────────────────
    st.divider()
    st.markdown("### ⚠ Near-Expiry Alert — Next 90 Days")
    st.caption("Items in red expire within 30 days. Immediate action required.")

    near = (
        inv[inv["is_near_expiry"]][[
            "medicine_name", "category", "branch_name",
            "stock_quantity", "expiry_date",
            "days_to_expiry", "stock_value"
        ]]
        .sort_values("days_to_expiry")
        .head(30)
        .copy()
    )

    # Format for display
    near["expiry_date"]   = near["expiry_date"].dt.strftime("%Y-%m-%d")
    near["days_to_expiry"]= near["days_to_expiry"].astype(int)
    near["stock_value"]   = near["stock_value"].apply(lambda x: f"₹{x:,.0f}")

    # Color rows by urgency
    def color_rows(row):
        if row["days_to_expiry"] <= 30:
            return ["background-color: #FDECEA"] * len(row)
        elif row["days_to_expiry"] <= 60:
            return ["background-color: #FFF3CD"] * len(row)
        return [""] * len(row)

    st.dataframe(
        near.style.apply(color_rows, axis=1),
        width='stretch',
        height=400,
    )

    # ── Low Stock Table ─────────────────────────────
    st.divider()
    st.markdown("### 🔴 Low Stock — Reorder Required")

    low = (
        inv[inv["is_low_stock"]][[
            "medicine_name", "category", "branch_name",
            "stock_quantity", "reorder_level",
            "stock_status", "supplier_name"
        ]]
        .sort_values("stock_quantity")
    )
    st.dataframe(low, width='stretch', height=300)