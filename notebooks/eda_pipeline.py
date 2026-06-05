"""
Pharmacy Intelligence System 
EDA & Cleaning Pipeline
"""

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────
RAW_PATH = "data/raw/"
PROC_PATH = "data/processed/"
IMG_PATH = "images/"
# ── Load Data ─────────────────────────────────────────
print("Loading data...")

sales    = pd.read_csv(f"{RAW_PATH}sales.csv", parse_dates=["sales_date"])
products    = pd.read_csv(f"{RAW_PATH}products.csv")
customers   = pd.read_csv(f"{RAW_PATH}customers.csv", parse_dates=["registration_date"])
branches    = pd.read_csv(f"{RAW_PATH}branches.csv")
inventory    = pd.read_csv(f"{RAW_PATH}inventory.csv", parse_dates=["expiry_date"])

print("Data loaded successfully!\n")
# ── inspect data ────────────────────────────────────────

print("=" * 45)
print("DATASET SHAPES")
print("=" * 45)
print(f"Sales: {sales.shape[0]:>7,} rows x {sales.shape[1]} cols")
print(f"Products: {products.shape[0]:>7,} rows x {products.shape[1]} cols")
print(f"Customers: {customers.shape[0]:>7,} rows x {customers.shape[1]} cols")
print(f"Branches: {branches.shape[0]:>7,} rows x {branches.shape[1]} cols")
print(f"Inventory: {inventory.shape[0]:>7,} rows x {inventory.shape[1]} cols")
# DATA TYPES
print("\n\nSALES - DATA TYPES")
print("=" * 45)
print(sales.dtypes)
# MISSING VALUES
print("\n\nMISSING VALUES CHECK")
print("=" * 45)
for name, df in [("sales", sales), ("products", products), ("customers", customers), ("branches", branches), ("inventory", inventory)]:
    nulls = df.isnull().sum().sum()
    print(f"{name:<12}: {nulls} missing values")
# DUPLICATES CHECK
print("\n\nDUPLICATES CHECK")
print("=" * 45)
print(f" Sales duplicates: {sales.duplicated().sum()}")
print(f" Invoice ID duplicates: {sales['invoice_id'].duplicated().sum()}")    
# NUMARIC SUMMARY FOR SALES
print("\n\nSALES - NUMERIC SUMMARY")
print("=" * 45)
print(sales[["quantity_sold", "unit_price", "discount_pct", "total_amount" ]].describe().round(2))

# ── CLEANING ─────────────────────────────────────────────

print("\n\nCLEANING...")
print("=" * 45)

# Remove any duplicate rows (there shouldn't be any, but always check)
before = len(sales)
sales = sales.drop_duplicates()
print(f"  Duplicates removed: {before - len(sales)}")

# Remove rows where total_amount is 0 or negative — can't have a ₹0 sale
before = len(sales)
sales = sales[sales["total_amount"] > 0]
print(f"  Zero/negative sales removed: {before - len(sales)}")

# Make sure quantity is at least 1
before = len(sales)
sales = sales[sales["quantity_sold"] >= 1]
print(f"  Invalid quantity rows removed: {before - len(sales)}")

print(f"\n  ✓ Final sales rows: {len(sales):,}")

# ── ENRICH DATA & FEATURE ENGINEERING ─────────────────────────────

print("\n\nFEATURE ENGINEERING...")
print("=" * 45)

# From sales_date, extract time components
sales["year"]       = sales["sales_date"].dt.year
sales["month"]      = sales["sales_date"].dt.month
sales["month_name"] = sales["sales_date"].dt.strftime("%b")   # Jan, Feb...
sales["quarter"]    = sales["sales_date"].dt.quarter           # 1, 2, 3, 4
sales["is_weekend"] = sales["day_of_week"].isin(["Saturday", "Sunday"])
sales["revenue_band"] = pd.cut(
    sales["total_amount"],
    bins   = [0,   200,     500,      1000,      5000,   999999],
    labels = ["<₹200", "₹200-500", "₹500-1K", "₹1K-5K", "₹5K+"]
)

print("  ✓ Added: year, month, month_name, quarter, is_weekend, revenue_band")

# Customer age groups
customers["age_group"] = pd.cut(
    customers["age"],
    bins   = [0,  25,  35,  50,  65, 100],
    labels = ["18-25", "26-35", "36-50", "51-65", "65+"]
)
print("  ✓ Added: age_group to customers")

# Inventory health flags
today = pd.Timestamp("2024-12-31")
inventory["days_to_expiry"] = (inventory["expiry_date"] - today).dt.days
inventory["is_low_stock"]   = inventory["stock_quantity"] <= inventory["reorder_level"]
inventory["is_near_expiry"] = inventory["days_to_expiry"].between(0, 90)

# Readable status label
inventory["stock_status"] = np.select(
    condlist = [
        inventory["stock_quantity"] == 0,
        inventory["stock_quantity"] <= inventory["reorder_level"] * 0.5,
        inventory["stock_quantity"] <= inventory["reorder_level"],
    ],
    choicelist = ["Out of Stock", "Critical", "Low Stock"],
    default    = "Adequate"
)

print("  ✓ Added: days_to_expiry, is_low_stock, is_near_expiry, stock_status")


# ── BUSINESS SUMMARY ──────────────────────────────────
print("\n\nBUSINESS SUMMARY")
print("=" * 45)
print(f"  Total Revenue (2 yrs) : ₹{sales['total_amount'].sum():>15,.0f}")
print(f"  Avg Order Value       : ₹{sales['total_amount'].mean():>15,.2f}")
print(f"  Unique Customers      :  {sales['customer_id'].nunique():>14,}")
print(f"  Top Category (rev)    :  {sales.groupby('category')['total_amount'].sum().idxmax():>14}")
print(f"  Top Branch (rev)      :  {sales.merge(branches[['branch_id','branch_name']], on='branch_id').groupby('branch_name')['total_amount'].sum().idxmax()}")
print(f"  Low Stock Items       :  {inventory['is_low_stock'].sum():>14,}")
print(f"  Near-Expiry Items     :  {inventory['is_near_expiry'].sum():>14,}")


# ── SAVE CLEANED FILES ──────────────────────────────────
import os
os.makedirs(PROC_PATH, exist_ok=True)

sales.to_csv(f"{PROC_PATH}sales_clean.csv",         index=False)
customers.to_csv(f"{PROC_PATH}customers_clean.csv", index=False)
inventory.to_csv(f"{PROC_PATH}inventory_clean.csv", index=False)

print("\n\n✓ Cleaned files saved to data/processed/")

# ── VISUALIZATION ─────────────────────────────────────
import os
os.makedirs(IMG_PATH, exist_ok=True)

print("\n\nGENERATING CHARTS...")
print("=" * 45)


# ── Chart 1: Monthly Revenue Trend ─────────────────

monthly_rev = (
    sales
    .groupby(["year", "month", "month_name"])["total_amount"]
    .sum()
    .reset_index()
    .sort_values(["year", "month"])
)
monthly_rev["period"] = monthly_rev["month_name"] + " " + monthly_rev["year"].astype(str)

fig, ax = plt.subplots(figsize=(14, 5))

# Separate color for each year
colors = ["#0F4C75" if y == 2023 else "#34ACE0" for y in monthly_rev["year"]]
ax.bar(monthly_rev["period"], monthly_rev["total_amount"],
       color=colors, width=0.7, edgecolor="white")

# 3-month moving average line — shows the trend beyond noise
moving_avg = monthly_rev["total_amount"].rolling(window=3).mean()
ax.plot(monthly_rev["period"], moving_avg,
        color="#E74C3C", linewidth=2.5,
        marker="o", markersize=4, label="3-Month Moving Avg")

ax.set_title("Monthly Revenue Trend (2023–2024)",
             fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Revenue (₹)")
ax.set_xlabel("")
ax.legend()
ax.grid(axis="y", alpha=0.3)
ax.spines[["top", "right"]].set_visible(False)
plt.xticks(rotation=45, ha="right", fontsize=8)

# Format y-axis: show ₹1.2M instead of 1200000
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M")
)

plt.tight_layout()
plt.savefig(f"{IMG_PATH}monthly_trend.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ Chart 1 saved: monthly_trend.png")


# ── Chart 2: Revenue by Category ───────────────────
cat_rev = (
    sales.groupby("category")["total_amount"]
    .sum()
    .sort_values(ascending=True)   
)

fig, ax = plt.subplots(figsize=(10, 7))
colors  = ["#0F4C75"] * len(cat_rev)
colors[-1] = "#E74C3C"   

ax.barh(cat_rev.index, cat_rev.values, color=colors,
        edgecolor="white", height=0.65)

# Add value labels on each bar
for i, val in enumerate(cat_rev.values):
    ax.text(val + cat_rev.max() * 0.01, i,
            f"₹{val/1e6:.2f}M",
            va="center", fontsize=9, fontweight="bold")

ax.set_title("Revenue by Medicine Category",
             fontsize=13, fontweight="bold", pad=12)
ax.set_xlabel("Total Revenue (₹)")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", alpha=0.3)

plt.tight_layout()
plt.savefig(f"{IMG_PATH}category_revenue.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ Chart 2 saved: category_revenue.png")


# ── Chart 3: Payment Method Mix ────────────────────
pay_counts = sales["payment_method"].value_counts()

fig, ax = plt.subplots(figsize=(7, 7))
colors  = ["#0F4C75", "#1B6CA8", "#34ACE0", "#F39C12", "#E74C3C"]

wedges, texts, autotexts = ax.pie(
    pay_counts.values,
    labels     = pay_counts.index,
    colors     = colors,
    autopct    = "%1.1f%%",
    startangle = 90,
    wedgeprops = dict(width=0.55, edgecolor="white", linewidth=2)
)

for at in autotexts:
    at.set_fontsize(10)
    at.set_fontweight("bold")

ax.set_title("Payment Method Distribution",
             fontsize=13, fontweight="bold", pad=20)

plt.tight_layout()
plt.savefig(f"{IMG_PATH}payment_mix.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ Chart 3 saved: payment_mix.png")

print("\n✓ All charts saved to images/")
print("\nPhase 3 complete!")