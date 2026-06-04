"""
Pharmacy Intelligence System
Data Generator — creates 5 realistic CSV files
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ── Configuration ──────────────────────────────────────────
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

NUM_SALES     = 50_000   
NUM_CUSTOMERS = 3_000
START_DATE    = datetime(2023, 1, 1)
END_DATE      = datetime(2024, 12, 31)

# Where to save the files
OUTPUT_PATH = "data/raw/"
os.makedirs(OUTPUT_PATH, exist_ok=True)  # creates folder if it doesn't exist


# ══════════════════════════════════════════════════════
# TABLE 1: BRANCHES
# ══════════════════════════════════════════════════════
def generate_branches():
    """8 pharmacy branches across 3 Indian cities."""

    branches = [
        {"branch_id": "BR01", "branch_name": "Apollo Banjara Hills",
         "city": "Hyderabad", "manager": "Rajesh Kumar"},

        {"branch_id": "BR02", "branch_name": "Apollo Jubilee Hills",
         "city": "Hyderabad", "manager": "Priya Sharma"},

        {"branch_id": "BR03", "branch_name": "MedPlus Madhapur",
         "city": "Hyderabad", "manager": "Suresh Reddy"},

        {"branch_id": "BR04", "branch_name": "MedPlus Secunderabad",
         "city": "Hyderabad", "manager": "Anitha Rao"},

        {"branch_id": "BR05", "branch_name": "Apollo Bangalore Central",
         "city": "Bangalore", "manager": "Vikram Singh"},

        {"branch_id": "BR06", "branch_name": "MedPlus Koramangala",
         "city": "Bangalore", "manager": "Deepa Nair"},

        {"branch_id": "BR07", "branch_name": "Apollo Chennai OMR",
         "city": "Chennai",   "manager": "Ramesh Iyer"},

        {"branch_id": "BR08", "branch_name": "MedPlus Adyar",
         "city": "Chennai",   "manager": "Kavitha Menon"},
    ]

    return pd.DataFrame(branches)


# ══════════════════════════════════════════════════════
# TABLE 2: PRODUCTS
# ══════════════════════════════════════════════════════
def generate_products():
    """
    74 medicines organized by category.
    Each category has a price range and a demand level.
    demand_tier controls how often this category appears in sales.
    """

    # Dictionary: category → list of medicines, price range, demand
    CATALOG = {
        "Antibiotics": {
            "medicines":    ["Amoxicillin 500mg", "Azithromycin 250mg",
                             "Ciprofloxacin 500mg", "Doxycycline 100mg",
                             "Metronidazole 400mg", "Levofloxacin 500mg"],
            "price_range":  (45, 320),
            "demand":       "high"
        },
        "Analgesics": {
            "medicines":    ["Paracetamol 500mg", "Ibuprofen 400mg",
                             "Diclofenac 50mg", "Aspirin 75mg",
                             "Tramadol 50mg", "Naproxen 250mg"],
            "price_range":  (12, 180),
            "demand":       "very_high"
        },
        "Cardiovascular": {
            "medicines":    ["Atorvastatin 10mg", "Amlodipine 5mg",
                             "Metoprolol 50mg", "Losartan 50mg",
                             "Ramipril 5mg", "Rosuvastatin 10mg",
                             "Clopidogrel 75mg", "Telmisartan 40mg"],
            "price_range":  (55, 620),
            "demand":       "high"
        },
        "Diabetes": {
            "medicines":    ["Metformin 500mg", "Glimepiride 2mg",
                             "Insulin Glargine", "Sitagliptin 100mg",
                             "Vildagliptin 50mg", "Dapagliflozin 10mg"],
            "price_range":  (85, 1200),
            "demand":       "high"
        },
        "Vitamins & Supplements": {
            "medicines":    ["Vitamin C 500mg", "Vitamin D3 1000IU",
                             "B-Complex", "Calcium + D3",
                             "Omega-3 Fish Oil", "Multivitamin",
                             "Iron + Folic Acid", "Zinc 50mg"],
            "price_range":  (60, 450),
            "demand":       "very_high"
        },
        "Gastroenterology": {
            "medicines":    ["Omeprazole 20mg", "Pantoprazole 40mg",
                             "Ondansetron 4mg", "Domperidone 10mg",
                             "Loperamide 2mg", "Lactulose Syrup"],
            "price_range":  (25, 280),
            "demand":       "high"
        },
        "Respiratory": {
            "medicines":    ["Salbutamol Inhaler", "Budesonide Inhaler",
                             "Montelukast 10mg", "Cetirizine 10mg",
                             "Levocetrizine 5mg", "Fexofenadine 120mg"],
            "price_range":  (55, 780),
            "demand":       "medium"
        },
        "Dermatology": {
            "medicines":    ["Clotrimazole Cream", "Betamethasone Cream",
                             "Tretinoin Gel", "Terbinafine 250mg",
                             "Ketoconazole Shampoo"],
            "price_range":  (80, 520),
            "demand":       "medium"
        },
        "Neurology": {
            "medicines":    ["Gabapentin 300mg", "Pregabalin 75mg",
                             "Alprazolam 0.5mg", "Escitalopram 10mg",
                             "Donepezil 10mg"],
            "price_range":  (95, 980),
            "demand":       "medium"
        },
        "Pediatrics": {
            "medicines":    ["Paracetamol Syrup", "Amoxicillin Syrup",
                             "ORS Sachet", "Zinc Syrup",
                             "Multivitamin Drops", "Iron Syrup"],
            "price_range":  (30, 250),
            "demand":       "high"
        },
        "Hormones & Thyroid": {
            "medicines":    ["Levothyroxine 50mcg", "Progesterone 200mg",
                             "Prednisolone 5mg", "Testosterone Gel"],
            "price_range":  (75, 650),
            "demand":       "medium"
        },
        "Ophthalmology": {
            "medicines":    ["Timolol Eye Drops", "Ciprofloxacin Eye Drops",
                             "Lubricating Eye Drops", "Latanoprost Drops"],
            "price_range":  (45, 380),
            "demand":       "low"
        },
    }

    products = []
    prod_id  = 1

    for category, info in CATALOG.items():
        for medicine in info["medicines"]:

            low, high  = info["price_range"]
            unit_price = round(np.random.uniform(low, high), 2)

            # Cost price is always 55–75% of selling price
            cost_price = round(unit_price * np.random.uniform(0.55, 0.75), 2)

            products.append({
                "product_id":    f"PRD{prod_id:04d}",  # PRD0001, PRD0002 ...
                "medicine_name": medicine,
                "category":      category,
                "unit_price":    unit_price,
                "cost_price":    cost_price,
                "supplier_name": random.choice([
                    "Sun Pharmaceuticals", "Cipla Ltd",
                    "Dr. Reddy's Labs",    "Lupin Pharma",
                    "Mankind Pharma",      "Abbott India"
                ]),
                "demand_tier": info["demand"],
            })
            prod_id += 1

    return pd.DataFrame(products)


# ══════════════════════════════════════════════════════
# TABLE 3: CUSTOMERS
# ══════════════════════════════════════════════════════
def generate_customers():
    """3,000 customers with realistic Indian demographics."""

    customers = []

    for i in range(1, NUM_CUSTOMERS + 1):

        age = int(np.random.choice(
            # The 4 choices             # Their probabilities (must sum to 1.0)
            [np.random.randint(18, 30),
             np.random.randint(31, 45),
             np.random.randint(46, 60),
             np.random.randint(60, 80)],
            p=[0.15, 0.30, 0.35, 0.20]
        ))

        customers.append({
            "customer_id":       f"CUST{i:05d}",
            "age":               age,
            "gender":            random.choice(["Male", "Female"]),
            "city":              np.random.choice(
                                     ["Hyderabad", "Bangalore", "Chennai"],
                                     p=[0.50, 0.30, 0.20]
                                 ),
            "repeat_customer":   "Yes" if np.random.rand() > 0.35 else "No",
            "loyalty_member":    "Yes" if np.random.rand() > 0.55 else "No",
            "registration_date": (
                START_DATE + timedelta(days=random.randint(0, 180))
            ).strftime("%Y-%m-%d"),
        })

    return pd.DataFrame(customers)


# ══════════════════════════════════════════════════════
# TABLE 4: SALES  (the most important table)
# ══════════════════════════════════════════════════════
def generate_sales(products_df, customers_df, branches_df):
    """
    50,000 transactions with realistic patterns:
    - Seasonal spikes by medicine category
    - Branch performance differences
    - Exponential quantity distribution
    - Indian payment method preferences
    """

    # demand_tier → how often a category gets picked
    DEMAND_WEIGHT = {
        "very_high": 4.5,
        "high":      3.0,
        "medium":    1.8,
        "low":       0.9
    }

    # Build probability weights for product selection
    prod_weights = products_df["demand_tier"].map(DEMAND_WEIGHT).values.copy()
    prod_weights = prod_weights / prod_weights.sum()   

    # Branches don't perform equally — BR01 gets the most business
    branch_weights = np.array([0.18, 0.16, 0.14, 0.12, 0.13, 0.10, 0.09, 0.08])
    branch_weights = branch_weights / branch_weights.sum()

    PAYMENT_METHODS = ["Cash", "UPI", "Credit Card", "Debit Card", "Health Insurance"]
    PAYMENT_WEIGHTS = [0.30,   0.35,  0.12,          0.13,         0.10]

    total_days = (END_DATE - START_DATE).days
    sales = []

    for i in range(1, NUM_SALES + 1):

        sale_date = START_DATE + timedelta(days=random.randint(0, total_days))
        month     = sale_date.month
        product   = products_df.sample(1, weights=prod_weights).iloc[0]
        category  = product["category"]

        # ── Seasonal logic ──────────────────────────────
        # Some categories sell more in specific months
        seasonal_boost = 1.0

        if category in ["Respiratory", "Analgesics"] and month in [11, 12, 1, 2]:
            seasonal_boost = 1.8   # winter: more colds, more pain relief

        elif category in ["Gastroenterology", "Antibiotics"] and month in [7, 8, 9]:
            seasonal_boost = 1.6   # monsoon: more infections

        elif category == "Vitamins & Supplements" and month in [4, 5, 6]:
            seasonal_boost = 1.4   # summer: more health consciousness

        branch   = branches_df.sample(1, weights=branch_weights).iloc[0]
        customer = customers_df.sample(1).iloc[0]

        # Quantity: exponential distribution (most = 1-3 units, rarely 10+)
        qty = max(1, int(np.random.exponential(2.5) * seasonal_boost))

        unit_price = round(product["unit_price"] * np.random.uniform(0.95, 1.05), 2)

        # Discount: most transactions have no discount
        discount = float(np.random.choice(
            [0,   0,   0,   5,   10,  15],
            p=   [0.50, 0.20, 0.10, 0.10, 0.06, 0.04]
        ))

        total = round(qty * unit_price * (1 - discount / 100), 2)

        sales.append({
            "invoice_id":     f"INV{i:07d}",
            "branch_id":      branch["branch_id"],
            "product_id":     product["product_id"],
            "medicine_name":  product["medicine_name"],
            "category":       category,
            "quantity_sold":  qty,
            "unit_price":     unit_price,
            "discount_pct":   discount,
            "total_amount":   total,
            "payment_method": np.random.choice(PAYMENT_METHODS, p=PAYMENT_WEIGHTS),
            "sales_date":     sale_date.strftime("%Y-%m-%d"),
            "sales_month":    sale_date.strftime("%Y-%m"),
            "customer_id":    customer["customer_id"],
            "day_of_week":    sale_date.strftime("%A"),
        })

    return pd.DataFrame(sales)


# ══════════════════════════════════════════════════════
# TABLE 5: INVENTORY
# ══════════════════════════════════════════════════════
def generate_inventory(products_df, branches_df):
    """
    One row per product per branch — 74 products × 8 branches = 592 rows.
    Some items are deliberately low stock (alert scenario).
    Some items are near expiry (another alert scenario).
    """

    inventory = []
    today     = END_DATE   

    for _, product in products_df.iterrows():
        for _, branch in branches_df.iterrows():

            # Base stock depends on demand tier
            demand_mult = {"very_high": 1.0, "high": 0.75,
                           "medium": 0.5, "low": 0.3}
            base_stock  = int(np.random.uniform(20, 500)
                             * demand_mult.get(product["demand_tier"], 0.5))

            # 8% of items are critically low stock (triggers alerts)
            if np.random.rand() < 0.08:
                base_stock = random.randint(0, 12)

            reorder_level   = int(base_stock * np.random.uniform(0.15, 0.25))
            max_stock_level = int(base_stock * np.random.uniform(2.5, 4.0))

            # Expiry: 5% near expiry (≤30 days), 10% in 31–90 days, rest fine
            days_to_expiry = int(np.random.choice(
                [random.randint(7,  30),
                 random.randint(31, 90),
                 random.randint(91, 365),
                 random.randint(366, 730)],
                p=[0.05, 0.10, 0.40, 0.45]
            ))
            expiry_date = (today + timedelta(days=days_to_expiry)).strftime("%Y-%m-%d")

            inventory.append({
                "inventory_id":      f"INV-{product['product_id']}-{branch['branch_id']}",
                "product_id":        product["product_id"],
                "branch_id":         branch["branch_id"],
                "stock_quantity":    base_stock,
                "reorder_level":     reorder_level,
                "max_stock_level":   max_stock_level,
                "supplier_name":     product["supplier_name"],
                "batch_number":      f"BATCH{random.randint(100000, 999999)}",
                "expiry_date":       expiry_date,
                "warehouse_location":random.choice(["WH-HYD-01", "WH-HYD-02",
                                                    "WH-BLR-01", "WH-CHN-01"]),
                "unit_cost":         product["cost_price"],
                "stock_value":       round(base_stock * product["cost_price"], 2),
            })

    return pd.DataFrame(inventory)


# ══════════════════════════════════════════════════════
# MAIN — runs all 5 generators
# ══════════════════════════════════════════════════════
if __name__ == "__main__":

    print("=" * 50)
    print("  Pharmacy Intelligence — Data Generator")
    print("=" * 50)

    print("\n[1/5] Generating branches...")
    branches_df = generate_branches()
    branches_df.to_csv(f"{OUTPUT_PATH}branches.csv", index=False)
    print(f"      ✓ {len(branches_df)} branches saved")

    print("[2/5] Generating products...")
    products_df = generate_products()
    products_df.to_csv(f"{OUTPUT_PATH}products.csv", index=False)
    print(f"      ✓ {len(products_df)} products saved")

    print("[3/5] Generating customers...")
    customers_df = generate_customers()
    customers_df.to_csv(f"{OUTPUT_PATH}customers.csv", index=False)
    print(f"      ✓ {len(customers_df)} customers saved")

    print("[4/5] Generating sales (50,000 rows — takes ~30 seconds)...")
    sales_df = generate_sales(products_df, customers_df, branches_df)
    sales_df.to_csv(f"{OUTPUT_PATH}sales.csv", index=False)
    print(f"      ✓ {len(sales_df):,} sales saved")
    print(f"      ✓ Total revenue: ₹{sales_df['total_amount'].sum():,.0f}")

    print("[5/5] Generating inventory...")
    inventory_df = generate_inventory(products_df, branches_df)
    inventory_df.to_csv(f"{OUTPUT_PATH}inventory.csv", index=False)
    print(f"      ✓ {len(inventory_df)} inventory records saved")

    print("\n" + "=" * 50)
    print("  All 5 files saved to data/raw/")
    print("=" * 50)