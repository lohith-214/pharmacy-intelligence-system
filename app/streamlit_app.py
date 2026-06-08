"""
Pharmacy Intelligence System
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Page config — must be first ─────────────────────────
st.set_page_config(
    page_title="Pharmacy Intelligence",
    page_icon="💊",
    layout="wide",
)

# ── Constants ────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIMARY   = "#0F4C75"
SECONDARY = "#34ACE0"
SUCCESS   = "#27AE60"
WARNING   = "#F39C12"
DANGER    = "#E74C3C"

# ══════════════════════════════════════════════════════════
# DATA LOADING — cached so it only runs once
# ══════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 💊 PharmIntel")
    st.markdown("*Retail Pharmacy Analytics*")
    st.divider()
    page = st.radio(
        "Navigate to",
        options=[
            "🏠  Home Dashboard",
            "📈  Sales Analytics",
            "📦  Inventory Analytics",
            "👥  Customer Insights",
        ]
    )
    st.divider()
    st.caption("Data: Jan 2023 – Dec 2024")
    st.caption("50,000 transactions · 8 branches")


# ── Load once, use everywhere ────────────────────────────
sales, inventory, products, customers, branches = load_data()


# ══════════════════════════════════════════════════════════
# PAGE 1 — HOME DASHBOARD
# ══════════════════════════════════════════════════════════
if "Home" in page:

    st.markdown("# 💊 Pharmacy Intelligence System")
    st.markdown("*Executive Overview — 2023 to 2024*")
    st.divider()

    # ── KPI calculations ─────────────────────────────
    rev_2023 = sales[sales["year"] == 2023]["total_amount"].sum()
    rev_2024 = sales[sales["year"] == 2024]["total_amount"].sum()
    yoy      = ((rev_2024 - rev_2023) / rev_2023) * 100

    # ── KPI Row 1 ────────────────────────────────────
    st.markdown("### Key Performance Indicators")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue",
              f"₹{sales['total_amount'].sum()/1e6:.2f}M",
              delta=f"YoY {yoy:+.1f}%")
    c2.metric("Total Transactions", f"{len(sales):,}")
    c3.metric("Active Customers",   f"{sales['customer_id'].nunique():,}")
    c4.metric("Avg Order Value",    f"₹{sales['total_amount'].mean():.0f}")

    # ── KPI Row 2 ────────────────────────────────────
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Inventory Value",
              f"₹{inventory['stock_value'].sum()/1e6:.2f}M")
    c6.metric("Products Tracked", f"{len(products)}")
    c7.metric("⚠ Low Stock Alerts",
              f"{int(inventory['is_low_stock'].sum())}",
              delta="Needs reorder", delta_color="inverse")
    c8.metric("⚠ Near-Expiry Items",
              f"{int(inventory['is_near_expiry'].sum())}",
              delta="Next 90 days", delta_color="inverse")

    st.divider()

    # ── Monthly Revenue Trend ────────────────────────
    st.markdown("### Monthly Revenue Trend")
    monthly = (
        sales
        .groupby(["year", "month", "month_name"])["total_amount"]
        .sum().reset_index()
        .sort_values(["year", "month"])
    )
    monthly["period"] = (monthly["month_name"] + " "
                         + monthly["year"].astype(str))

    fig = px.bar(
        monthly, x="period", y="total_amount", color="year",
        color_discrete_map={2023: PRIMARY, 2024: SECONDARY},
        labels={"total_amount": "Revenue (₹)", "period": ""},
        template="plotly_white",
    )
    ma = monthly["total_amount"].rolling(3).mean()
    fig.add_trace(go.Scatter(
        x=monthly["period"], y=ma, name="3-Month Moving Avg",
        line=dict(color=DANGER, width=2.5, dash="dot"),
        mode="lines+markers", marker=dict(size=4),
    ))
    fig.update_layout(height=380, xaxis_tickangle=-35,
                      margin=dict(t=20, b=60),
                      legend=dict(orientation="h", y=1.08))
    fig.update_yaxes(tickprefix="₹", tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Category pie + Branch bar ────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("### Revenue by Category")
        cat = (sales.groupby("category")["total_amount"]
               .sum().sort_values(ascending=False).reset_index())
        fig2 = px.pie(
            cat, values="total_amount", names="category",
            hole=0.45, template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig2.update_traces(textposition="inside", textinfo="percent")
        fig2.update_layout(height=380, margin=dict(t=20, b=20),
                           legend=dict(font_size=10))
        st.plotly_chart(fig2, use_container_width=True)

    with col_r:
        st.markdown("### Branch Revenue Ranking")
        br = (
            sales
            .merge(branches[["branch_id", "branch_name"]], on="branch_id")
            .groupby("branch_name")["total_amount"]
            .sum().sort_values(ascending=True).reset_index()
        )
        br["branch_short"] = br["branch_name"].apply(
            lambda x: x[:20] + "…" if len(x) > 20 else x
        )
        fig3 = px.bar(
            br, x="total_amount", y="branch_short",
            orientation="h", color="total_amount",
            color_continuous_scale=[SECONDARY, PRIMARY],
            labels={"total_amount": "Revenue (₹)", "branch_short": ""},
            template="plotly_white",
        )
        fig3.update_xaxes(tickprefix="₹", tickformat=",.0f")
        fig3.update_layout(height=380, coloraxis_showscale=False,
                           margin=dict(t=20, b=20))
        st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════
# PAGE 2 — SALES ANALYTICS
# ══════════════════════════════════════════════════════════
elif "Sales" in page:

    st.markdown("# 📈 Sales Analytics")
    st.divider()

    # ── Filters ──────────────────────────────────────
    with st.expander("🎛  Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            years = st.multiselect("Year", [2023, 2024],
                                   default=[2023, 2024])
        with col2:
            cats = st.multiselect(
                "Category",
                options=sorted(sales["category"].unique()),
                default=list(sales["category"].unique())
            )
        with col3:
            pays = st.multiselect(
                "Payment Method",
                options=list(sales["payment_method"].unique()),
                default=list(sales["payment_method"].unique())
            )

    filtered = sales[
        sales["year"].isin(years) &
        sales["category"].isin(cats) &
        sales["payment_method"].isin(pays)
    ]
    st.caption(f"Showing {len(filtered):,} of {len(sales):,} transactions "
               f"({len(filtered)/len(sales)*100:.1f}%)")

    # ── Filtered KPIs ────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenue",      f"₹{filtered['total_amount'].sum()/1e6:.2f}M")
    c2.metric("Transactions", f"{len(filtered):,}")
    c3.metric("Avg Order",    f"₹{filtered['total_amount'].mean():.0f}")
    c4.metric("Avg Discount", f"{filtered['discount_pct'].mean():.1f}%")

    st.divider()

    # ── Top 15 medicines ─────────────────────────────
    st.markdown("### Top 15 Medicines by Revenue")
    top15 = (
        filtered
        .groupby(["medicine_name", "category"])["total_amount"]
        .sum().sort_values(ascending=False).head(15).reset_index()
    )
    fig = px.bar(
        top15, x="total_amount", y="medicine_name",
        color="category", orientation="h",
        template="plotly_white",
        labels={"total_amount": "Revenue (₹)", "medicine_name": ""},
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig.update_xaxes(tickprefix="₹", tickformat=",.0f")
    fig.update_layout(height=500, yaxis=dict(autorange="reversed"),
                      margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Heatmap ──────────────────────────────────────
    st.markdown("### Sales Heatmap — Day of Week × Month")
    hmap = (
        filtered
        .groupby(["day_of_week", "month_name"])["total_amount"]
        .sum().unstack().fillna(0)
    )
    day_order = ["Monday","Tuesday","Wednesday",
                 "Thursday","Friday","Saturday","Sunday"]
    mon_order = ["Jan","Feb","Mar","Apr","May","Jun",
                 "Jul","Aug","Sep","Oct","Nov","Dec"]
    hmap = hmap.reindex([d for d in day_order if d in hmap.index])
    hmap = hmap.reindex(
        columns=[m for m in mon_order if m in hmap.columns]
    )
    fig3 = px.imshow(hmap, color_continuous_scale="Blues",
                     labels=dict(color="Revenue (₹)"),
                     aspect="auto", template="plotly_white")
    fig3.update_layout(height=320, margin=dict(t=20))
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── Payment breakdown ────────────────────────────
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
        fig4.update_layout(height=320, showlegend=False,
                           margin=dict(t=20))
        st.plotly_chart(fig4, use_container_width=True)

    with col_r:
        pay_cnt = filtered["payment_method"].value_counts().reset_index()
        pay_cnt.columns = ["payment_method", "count"]
        fig5 = px.pie(pay_cnt, values="count", names="payment_method",
                      hole=0.45, template="plotly_white",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig5.update_layout(height=320, margin=dict(t=20))
        st.plotly_chart(fig5, use_container_width=True)


# ══════════════════════════════════════════════════════════
# PAGE 3 — INVENTORY ANALYTICS
# ══════════════════════════════════════════════════════════
elif "Inventory" in page:

    st.markdown("# 📦 Inventory Analytics")
    st.divider()

    inv = (
        inventory
        .merge(products[["product_id","medicine_name","category"]],
               on="product_id")
        .merge(branches[["branch_id","branch_name"]], on="branch_id")
    )

    # ── KPIs ─────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Stock Value",
              f"₹{inv['stock_value'].sum()/1e6:.2f}M")
    c2.metric("Total SKUs",
              f"{inv['product_id'].nunique()}")
    c3.metric("Low / Critical Stock",
              f"{int(inv['is_low_stock'].sum())}",
              delta="⚠ Needs action", delta_color="inverse")
    c4.metric("Near Expiry (90d)",
              f"{int(inv['is_near_expiry'].sum())}",
              delta="⚠ Review now", delta_color="inverse")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Stock Status Overview")
        status = inv["stock_status"].value_counts().reset_index()
        status.columns = ["Status", "Count"]
        color_map = {"Adequate": SUCCESS, "Low Stock": WARNING,
                     "Critical": DANGER, "Out of Stock": "#8B0000"}
        fig = px.bar(status, x="Status", y="Count",
                     color="Status", color_discrete_map=color_map,
                     template="plotly_white")
        fig.update_layout(height=350, showlegend=False,
                          margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Stock Value by Category")
        cat_val = (inv.groupby("category")["stock_value"]
                   .sum().sort_values(ascending=True).reset_index())
        fig2 = px.bar(
            cat_val, x="stock_value", y="category",
            orientation="h", color="stock_value",
            color_continuous_scale=["#BDC3C7", PRIMARY],
            labels={"stock_value":"Stock Value (₹)","category":""},
            template="plotly_white",
        )
        fig2.update_xaxes(tickprefix="₹", tickformat=",.0f")
        fig2.update_layout(height=350, coloraxis_showscale=False,
                           margin=dict(t=20))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Near-expiry table ────────────────────────────
    st.divider()
    st.markdown("### ⚠ Near-Expiry Alert — Next 90 Days")

    near = (
        inv[inv["is_near_expiry"]][[
            "medicine_name","category","branch_name",
            "stock_quantity","expiry_date",
            "days_to_expiry","stock_value"
        ]]
        .sort_values("days_to_expiry").head(30).copy()
    )
    near["expiry_date"]    = near["expiry_date"].dt.strftime("%Y-%m-%d")
    near["days_to_expiry"] = near["days_to_expiry"].astype(int)
    near["stock_value"]    = near["stock_value"].apply(
                                 lambda x: f"₹{x:,.0f}")

    def color_rows(row):
        if row["days_to_expiry"] <= 30:
            return ["background-color:#FDECEA"] * len(row)
        elif row["days_to_expiry"] <= 60:
            return ["background-color:#FFF3CD"] * len(row)
        return [""] * len(row)

    st.dataframe(near.style.apply(color_rows, axis=1),
                 use_container_width=True, height=400)

    # ── Low stock table ──────────────────────────────
    st.divider()
    st.markdown("### 🔴 Low Stock — Reorder Required")
    low = (
        inv[inv["is_low_stock"]][[
            "medicine_name","category","branch_name",
            "stock_quantity","reorder_level",
            "stock_status","supplier_name"
        ]]
        .sort_values("stock_quantity")
    )
    st.dataframe(low, use_container_width=True, height=300)


# ══════════════════════════════════════════════════════════
# PAGE 4 — CUSTOMER INSIGHTS
# ══════════════════════════════════════════════════════════
elif "Customer" in page:

    st.markdown("# 👥 Customer Insights")
    st.divider()

    # ── Build RFM table ──────────────────────────────
    today = pd.Timestamp("2024-12-31")
    rfm = (
        sales
        .groupby("customer_id")
        .agg(
            frequency    =("invoice_id",   "count"),
            monetary     =("total_amount", "sum"),
            last_purchase=("sales_date",   "max"),
        )
        .reset_index()
    )
    rfm["recency_days"] = (today - rfm["last_purchase"]).dt.days

    rfm["R"] = pd.qcut(rfm["recency_days"],
                        q=5, labels=[5,4,3,2,1]).astype(int)
    rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"),
                        q=5, labels=[1,2,3,4,5]).astype(int)
    rfm["M"] = pd.qcut(rfm["monetary"].rank(method="first"),
                        q=5, labels=[1,2,3,4,5]).astype(int)

    def assign_segment(row):
        if   row["R"] >= 4 and row["F"] >= 4: return "Champion"
        elif row["R"] >= 3 and row["F"] >= 3: return "Loyal"
        elif row["R"] >= 4 and row["F"] <= 2: return "New Customer"
        elif row["R"] <= 2 and row["F"] >= 4: return "At Risk"
        elif row["R"] <= 2 and row["M"] >= 4: return "Can't Lose"
        else:                                  return "Need Attention"

    rfm["segment"] = rfm.apply(assign_segment, axis=1)
    rfm = rfm.merge(
        customers[["customer_id","age","gender",
                   "city","loyalty_member","age_group"]],
        on="customer_id"
    )

    # ── KPIs ─────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers",    f"{len(rfm):,}")
    c2.metric("Loyalty Members",
              f"{(customers['loyalty_member']=='Yes').sum():,}")
    c3.metric("Avg Customer Value", f"₹{rfm['monetary'].mean():.0f}")
    c4.metric("Champions",
              f"{(rfm['segment']=='Champion').sum()}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Customer Segments (RFM)")
        seg = (
            rfm.groupby("segment")
            .agg(customers=("customer_id","count"),
                 revenue   =("monetary",   "sum"))
            .sort_values("revenue", ascending=False)
            .reset_index()
        )
        fig = px.bar(
            seg, x="segment", y="revenue", color="customers",
            color_continuous_scale=[SECONDARY, PRIMARY],
            labels={"revenue":"Total Revenue","segment":""},
            template="plotly_white",
        )
        fig.update_yaxes(tickprefix="₹", tickformat=",.0f")
        fig.update_layout(height=380, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Revenue by Age Group & Gender")
        age_g = (rfm.groupby(["age_group","gender"])["monetary"]
                 .sum().reset_index())
        fig2 = px.bar(
            age_g, x="age_group", y="monetary",
            color="gender", barmode="group",
            color_discrete_map={"Male":PRIMARY,"Female":"#E91E8C"},
            labels={"monetary":"Revenue","age_group":"Age Group"},
            template="plotly_white",
        )
        fig2.update_yaxes(tickprefix="₹", tickformat=",.0f")
        fig2.update_layout(height=380, margin=dict(t=20))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Top customers ────────────────────────────────
    st.divider()
    st.markdown("### Top 20 Customers by Lifetime Value")
    top_c = (
        rfm[["customer_id","age","gender","city",
             "loyalty_member","frequency","monetary","segment"]]
        .sort_values("monetary", ascending=False)
        .head(20).copy()
    )
    top_c["monetary"] = top_c["monetary"].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(top_c, use_container_width=True, height=400)