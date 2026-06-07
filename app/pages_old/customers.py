"""
Customer Insights Page — RFM segmentation and demographics.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

PRIMARY   = "#0F4C75"
SECONDARY = "#34ACE0"


def build_rfm(sales, customers):
    """
    RFM = Recency, Frequency, Monetary
    The standard framework for customer segmentation.

    Recency   = how recently did they buy? (lower days = better)
    Frequency = how many times did they buy?
    Monetary  = how much total did they spend?
    """
    today = pd.Timestamp("2024-12-31")

    rfm = (
        sales
        .groupby("customer_id")
        .agg(
            frequency   = ("invoice_id",    "count"),
            monetary    = ("total_amount",  "sum"),
            last_purchase = ("sales_date",  "max"),
        )
        .reset_index()
    )
    rfm["recency_days"] = (today - rfm["last_purchase"]).dt.days

    # Score each dimension 1–5 using quintiles
    # pd.qcut divides into 5 equal-sized groups
    rfm["R"] = pd.qcut(rfm["recency_days"],
                        q=5, labels=[5,4,3,2,1]).astype(int)
    rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"),
                        q=5, labels=[1,2,3,4,5]).astype(int)
    rfm["M"] = pd.qcut(rfm["monetary"].rank(method="first"),
                        q=5, labels=[1,2,3,4,5]).astype(int)

    # Assign business segment based on RFM scores
    def assign_segment(row):
        if row["R"] >= 4 and row["F"] >= 4:   return "Champion"
        elif row["R"] >= 3 and row["F"] >= 3: return "Loyal"
        elif row["R"] >= 4 and row["F"] <= 2: return "New Customer"
        elif row["R"] <= 2 and row["F"] >= 4: return "At Risk"
        elif row["R"] <= 2 and row["M"] >= 4: return "Can't Lose"
        else:                                  return "Need Attention"

    rfm["segment"] = rfm.apply(assign_segment, axis=1)

    # Merge with customer demographics
    rfm = rfm.merge(
        customers[["customer_id","age","gender","city",
                   "loyalty_member","age_group"]],
        on="customer_id"
    )
    return rfm


def show(sales, inventory, products, customers, branches):

    st.markdown("# 👥 Customer Insights")
    st.divider()

    rfm = build_rfm(sales, customers)

    # ── KPIs ───────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers",  f"{len(rfm):,}")
    c2.metric("Loyalty Members",
              f"{(customers['loyalty_member']=='Yes').sum():,}")
    c3.metric("Avg Customer Value", f"₹{rfm['monetary'].mean():.0f}")
    c4.metric("Champions",
              f"{(rfm['segment']=='Champion').sum()}")

    st.divider()

    # ── RFM Segments ────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Customer Segments (RFM)")
        st.caption("Based on recency, frequency and spend in the last 2 years.")

        seg = (
            rfm.groupby("segment")
            .agg(customers=("customer_id","count"),
                 revenue   =("monetary",   "sum"))
            .sort_values("revenue", ascending=False)
            .reset_index()
        )
        fig = px.bar(
            seg, x="segment", y="revenue",
            color="customers",
            color_continuous_scale=[SECONDARY, PRIMARY],
            labels={"revenue":"Total Revenue","segment":"Segment"},
            template="plotly_white",
        )
        fig.update_yaxes(tickprefix="₹", tickformat=",.0f")
        fig.update_layout(height=380, margin=dict(t=20))
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.markdown("### Revenue by Age Group & Gender")

        age_g = (
            rfm.groupby(["age_group","gender"])["monetary"]
            .sum().reset_index()
        )
        fig2 = px.bar(
            age_g, x="age_group", y="monetary",
            color="gender", barmode="group",
            color_discrete_map={"Male": PRIMARY, "Female": "#E91E8C"},
            labels={"monetary":"Revenue","age_group":"Age Group"},
            template="plotly_white",
        )
        fig2.update_yaxes(tickprefix="₹", tickformat=",.0f")
        fig2.update_layout(height=380, margin=dict(t=20))
        st.plotly_chart(fig2, width='stretch')

    # ── Top customers table ─────────────────────────
    st.divider()
    st.markdown("### Top 20 Customers by Lifetime Value")

    top_custs = (
        rfm[["customer_id","age","gender","city",
             "loyalty_member","frequency","monetary","segment"]]
        .sort_values("monetary", ascending=False)
        .head(20)
        .copy()
    )
    top_custs["monetary"] = top_custs["monetary"].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(top_custs, width='stretch', height=400)