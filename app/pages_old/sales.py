"""
Sales Analytics Page — deep dive with interactive filters.
"""

import streamlit as st
import plotly.express as px
import pandas as pd

PRIMARY  = "#0F4C75"
SECONDARY = "#34ACE0"
DANGER   = "#E74C3C"


def show(sales, inventory, products, customers, branches):

    st.markdown("# 📈 Sales Analytics")
    st.divider()

    # ── Sidebar filters ─────────────────────────────
    with st.expander("🎛  Filters — click to expand", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            years = st.multiselect(
                "Year",
                options = [2023, 2024],
                default = [2023, 2024]
            )
        with col2:
            categories = st.multiselect(
                "Category",
                options = sorted(sales["category"].unique()),
                default = list(sales["category"].unique())
            )
        with col3:
            payments = st.multiselect(
                "Payment Method",
                options = sales["payment_method"].unique(),
                default = list(sales["payment_method"].unique())
            )

    mask = (
        sales["year"].isin(years) &
        sales["category"].isin(categories) &
        sales["payment_method"].isin(payments)
    )
    filtered = sales[mask]

    # Show how many rows survived the filter
    st.caption(f"Showing {len(filtered):,} transactions "
               f"({len(filtered)/len(sales)*100:.1f}% of total)")

    # ── Filtered KPIs ───────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenue",       f"₹{filtered['total_amount'].sum()/1e6:.2f}M")
    c2.metric("Transactions",  f"{len(filtered):,}")
    c3.metric("Avg Order",     f"₹{filtered['total_amount'].mean():.0f}")
    c4.metric("Avg Discount",  f"{filtered['discount_pct'].mean():.1f}%")

    st.divider()

    # ── Top 15 Medicines ────────────────────────────
    st.markdown("### Top 15 Medicines by Revenue")
    top15 = (
        filtered
        .groupby(["medicine_name", "category"])["total_amount"]
        .sum()
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )
    fig = px.bar(
        top15,
        x       = "total_amount",
        y       = "medicine_name",
        color   = "category",
        orientation = "h",
        template    = "plotly_white",
        labels  = {"total_amount": "Revenue (₹)", "medicine_name": ""},
        color_discrete_sequence = px.colors.qualitative.Vivid,
    )
    fig.update_xaxes(tickprefix="₹", tickformat=",.0f")
    fig.update_layout(height=500, yaxis=dict(autorange="reversed"),
                      margin=dict(t=20))
    st.plotly_chart(fig, width='stretch')

    st.divider()

    # ── Heatmap: sales by day of week and month ─────
    st.markdown("### Sales Heatmap — Day of Week × Month")
    st.caption("Darker = higher revenue. Spot your peak selling days.")

    # Pivot: rows = day of week, columns = month
    heatmap_data = (
        filtered
        .groupby(["day_of_week", "month_name"])["total_amount"]
        .sum()
        .unstack()
        .fillna(0)
    )
    # Reorder rows and columns logically
    day_order = ["Monday","Tuesday","Wednesday","Thursday",
                 "Friday","Saturday","Sunday"]
    mon_order = ["Jan","Feb","Mar","Apr","May","Jun",
                 "Jul","Aug","Sep","Oct","Nov","Dec"]

    heatmap_data = heatmap_data.reindex(
        [d for d in day_order if d in heatmap_data.index]
    )
    heatmap_data = heatmap_data.reindex(
        columns=[m for m in mon_order if m in heatmap_data.columns]
    )

    fig3 = px.imshow(
        heatmap_data,
        color_continuous_scale = "Blues",
        labels = dict(color="Revenue (₹)"),
        aspect = "auto",
        template = "plotly_white",
    )
    fig3.update_layout(height=320, margin=dict(t=20))
    st.plotly_chart(fig3, width='stretch')

    # ── Payment method breakdown ────────────────────
    st.divider()
    st.markdown("### Payment Method Breakdown")

    col_l, col_r = st.columns(2)
    with col_l:
        pay_rev = (filtered.groupby("payment_method")["total_amount"]
                   .sum().reset_index()
                   .sort_values("total_amount", ascending=False))
        fig4 = px.bar(pay_rev, x="payment_method", y="total_amount",
                      color="payment_method", template="plotly_white",
                      labels={"total_amount":"Revenue","payment_method":""},
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig4.update_yaxes(tickprefix="₹", tickformat=",.0f")
        fig4.update_layout(height=320, showlegend=False, margin=dict(t=20))
        st.plotly_chart(fig4, width='stretch')

    with col_r:
        pay_cnt = filtered["payment_method"].value_counts().reset_index()
        pay_cnt.columns = ["payment_method", "count"]
        fig5 = px.pie(pay_cnt, values="count", names="payment_method",
                      hole=0.45, template="plotly_white",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig5.update_layout(height=320, margin=dict(t=20))
        st.plotly_chart(fig5, width='stretch')