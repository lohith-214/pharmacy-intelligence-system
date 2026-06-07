"""
Home Dashboard — executive overview.
Shows KPI cards, revenue trend, category split, branch comparison.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import get_kpis

# ── Color palette (consistent across all pages) ────
PRIMARY   = "#0F4C75"
SECONDARY = "#34ACE0"
SUCCESS   = "#27AE60"
WARNING   = "#F39C12"
DANGER    = "#E74C3C"


def kpi_card(col, label, value, delta=None, delta_good=True):
    with col:
        st.metric(
            label  = label,
            value  = value,
            delta  = delta,
        )


def show(sales, inventory, products, customers, branches):

    st.markdown("# 💊 Pharmacy Intelligence System")
    st.markdown("*Executive Overview — 2023 to 2024*")
    st.divider()

    # ── KPI Row 1 ───────────────────────────────────
    kpis = get_kpis(sales, inventory)

    st.markdown("### Key Performance Indicators")
    c1, c2, c3, c4 = st.columns(4)

    kpi_card(c1, "Total Revenue",
             f"₹{kpis['total_revenue']/1e6:.2f}M",
             delta=f"YoY {kpis['yoy_growth']:+.1f}%")

    kpi_card(c2, "Total Transactions",
             f"{kpis['total_orders']:,}")

    kpi_card(c3, "Active Customers",
             f"{kpis['active_customers']:,}")

    kpi_card(c4, "Avg Order Value",
             f"₹{kpis['avg_order_value']:.0f}")

    # ── KPI Row 2 ───────────────────────────────────
    c5, c6, c7, c8 = st.columns(4)

    kpi_card(c5, "Inventory Value",
             f"₹{kpis['inventory_value']/1e6:.2f}M")

    kpi_card(c6, "Products Tracked",
             f"{len(products)}")

    # For alerts, we want to show them as warnings
    kpi_card(c7, "⚠ Low Stock Alerts",
             f"{kpis['low_stock_count']}",
             delta="Needs reorder",
             delta_good=False)

    kpi_card(c8, "⚠ Near-Expiry Items",
             f"{kpis['near_expiry_count']}",
             delta="Next 90 days",
             delta_good=False)

    st.divider()

    # ── Monthly Revenue Trend ────────────────────────
    st.markdown("### Monthly Revenue Trend")

    monthly = (
        sales
        .groupby(["year", "month", "month_name"])["total_amount"]
        .sum()
        .reset_index()
        .sort_values(["year", "month"])
    )
    monthly["period"] = monthly["month_name"] + " " + monthly["year"].astype(str)

    fig = px.bar(
        monthly,
        x     = "period",
        y     = "total_amount",
        color = "year",
        color_discrete_map = {2023: PRIMARY, 2024: SECONDARY},
        labels = {"total_amount": "Revenue (₹)", "period": ""},
        template = "plotly_white",
    )

    # Add moving average line on top of the bars
    ma = monthly["total_amount"].rolling(3).mean()
    fig.add_trace(go.Scatter(
        x    = monthly["period"],
        y    = ma,
        name = "3-Month Moving Avg",
        line = dict(color=DANGER, width=2.5, dash="dot"),
        mode = "lines+markers",
        marker = dict(size=4),
    ))

    fig.update_layout(
        height  = 380,
        xaxis_tickangle = -35,
        margin  = dict(t=20, b=60),
        legend  = dict(orientation="h", y=1.08),
    )
    fig.update_yaxes(tickprefix="₹", tickformat=",.0f")
    st.plotly_chart(fig, width='stretch')

    st.divider()

    # ── Category + Branch side by side ──────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Revenue by Category")
        cat = (sales.groupby("category")["total_amount"]
               .sum().sort_values(ascending=False).reset_index())
        fig2 = px.pie(
            cat, values="total_amount", names="category",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2,
            template="plotly_white",
        )
        fig2.update_traces(textposition="inside", textinfo="percent")
        fig2.update_layout(height=380, margin=dict(t=20, b=20),
                           legend=dict(font_size=10))
        st.plotly_chart(fig2, width='stretch')

    with col_right:
        st.markdown("### Branch Revenue Ranking")
        br = (
            sales
            .merge(branches[["branch_id", "branch_name"]], on="branch_id")
            .groupby("branch_name")["total_amount"]
            .sum()
            .sort_values(ascending=True)
            .reset_index()
        )
        # Shorten long branch names for display
        br["branch_short"] = br["branch_name"].apply(
            lambda x: x[:20] + "…" if len(x) > 20 else x
        )
        fig3 = px.bar(
            br, x="total_amount", y="branch_short",
            orientation="h",
            color="total_amount",
            color_continuous_scale=[SECONDARY, PRIMARY],
            labels={"total_amount": "Revenue (₹)", "branch_short": ""},
            template="plotly_white",
        )
        fig3.update_xaxes(tickprefix="₹", tickformat=",.0f")
        fig3.update_layout(height=380, margin=dict(t=20, b=20),coloraxis_showscale=False)
        st.plotly_chart(fig3, width='stretch')