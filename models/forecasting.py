"""
Pharmacy Intelligence System
Demand Forecasting Module
Uses Facebook Prophet for time-series forecasting.

What this file does:
  1. Prepares monthly sales data for Prophet
  2. Trains a forecast model
  3. Predicts the next 6 months
  4. Saves forecast charts to images/
  5. Prints business recommendations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

PROC_PATH = "data/processed/"
IMG_PATH  = "images/"


# ══════════════════════════════════════════════════════
# STEP 1: PREPARE DATA FOR PROPHET
# ══════════════════════════════════════════════════════
def prepare_monthly_data(sales, category=None):
    """
    Prophet requires exactly two columns:
      'ds' = date (Prophet's name for the date column)
      'y'  = the value to forecast

    If category is given, filter to that category only.
    Otherwise use all sales.
    """
    if category:
        data = sales[sales["category"] == category].copy()
    else:
        data = sales.copy()

    # Group by month 
    monthly = (
        data
        .groupby("sales_month")["total_amount"]
        .sum()
        .reset_index()
    )

    # Rename to what Prophet expects
    monthly["ds"] = pd.to_datetime(monthly["sales_month"])
    monthly["y"]  = monthly["total_amount"]
    monthly       = monthly[["ds", "y"]].sort_values("ds")

    return monthly


# ══════════════════════════════════════════════════════
# STEP 2: TRAIN AND FORECAST
# ══════════════════════════════════════════════════════
def run_forecast(monthly_data, periods=6, label="All Categories"):
    """
    Trains a Prophet model and returns the forecast DataFrame.

    Parameters:
      monthly_data : output from prepare_monthly_data()
      periods      : how many months ahead to forecast
      label        : used in chart titles and print statements
    """
    from prophet import Prophet

    print(f"\n  Training model for: {label}")
    print(f"  Training on {len(monthly_data)} months of data")

    # ── Configure the model ───────────────────────────
    model = Prophet(
        yearly_seasonality    = True,   # learns annual patterns
        weekly_seasonality    = False,  # we have monthly data, not daily
        daily_seasonality     = False,
        changepoint_prior_scale = 0.05, # how flexible the trend line is
                                        # higher = more wiggly
                                        # lower  = smoother
        seasonality_prior_scale = 10,
    )

    model.add_seasonality(
        name        = "quarterly",
        period      = 91.25,   # days in a quarter
        fourier_order = 5,     # complexity of the seasonality curve
    )

    # ── Train ─────────────────────────────────────────
    model.fit(monthly_data)

    # ── Create future dates ───────────────────────────
    future   = model.make_future_dataframe(periods=periods, freq="MS")

    # ── Predict ───────────────────────────────────────
    forecast = model.predict(future)

    return model, forecast


# ══════════════════════════════════════════════════════
# STEP 3: VISUALIZE
# ══════════════════════════════════════════════════════
def plot_forecast(monthly_data, forecast, label="All Categories"):
    """
    Creates a professional forecast chart showing:
    - Actual historical data (blue line)
    - Predicted future values (green dashed line)
    - 95% confidence interval (green shaded area)
    - A vertical line marking where forecast starts
    """
    # Split forecast into historical fit and future prediction
    last_actual_date = monthly_data["ds"].max()
    forecast_future  = forecast[forecast["ds"] > last_actual_date]
    forecast_hist    = forecast[forecast["ds"] <= last_actual_date]

    fig, ax = plt.subplots(figsize=(13, 5))

    # ── Plot actual data ──────────────────────────────
    ax.plot(monthly_data["ds"], monthly_data["y"],
            color="#0F4C75", linewidth=2.5,
            marker="o", markersize=5,
            label="Actual Sales", zorder=3)

    # ── Plot model fit on historical data ─────────────
    ax.plot(forecast_hist["ds"], forecast_hist["yhat"],
            color="#34ACE0", linewidth=1.5,
            linestyle="--", alpha=0.7,
            label="Model Fit")

    # ── Plot future forecast ──────────────────────────
    ax.plot(forecast_future["ds"], forecast_future["yhat"],
            color="#27AE60", linewidth=2.5,
            marker="s", markersize=6,
            linestyle="--", label="Forecast",
            zorder=3)

    # ── Confidence interval (shaded area) ─────────────
    ax.fill_between(
        forecast_future["ds"],
        forecast_future["yhat_lower"],
        forecast_future["yhat_upper"],
        alpha=0.15, color="#27AE60",
        label="95% Confidence Interval"
    )

    # ── Vertical line: forecast start ─────────────────
    ax.axvline(last_actual_date,
               color="#E74C3C", linestyle=":",
               linewidth=1.5, label="Forecast Start")

    # ── Formatting ────────────────────────────────────
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M")
    )
    ax.set_title(f"6-Month Sales Forecast — {label}",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    # Save the chart
    safe_label = label.replace(" ", "_").replace("&", "and").lower()
    filename   = f"{IMG_PATH}forecast_{safe_label}.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Chart saved: {filename}")

    return forecast_future


# ══════════════════════════════════════════════════════
# STEP 4: PRINT FORECAST TABLE
# ══════════════════════════════════════════════════════
def print_forecast_table(forecast_future, label):
    """Prints a clean table of predicted values."""

    print(f"\n  Forecast Table — {label}")
    print(f"  {'Month':<12} {'Forecast':>12} "
          f"{'Lower Bound':>14} {'Upper Bound':>14}")
    print(f"  {'-'*54}")

    for _, row in forecast_future.iterrows():
        print(f"  {row['ds'].strftime('%b %Y'):<12} "
              f"₹{row['yhat']:>10,.0f} "
              f"₹{row['yhat_lower']:>12,.0f} "
              f"₹{row['yhat_upper']:>12,.0f}")


# ══════════════════════════════════════════════════════
# STEP 5: ACCURACY CHECK
# ══════════════════════════════════════════════════════
def check_accuracy(monthly_data, forecast):
    """
    Measures how well the model fits historical data.
    We use MAPE — Mean Absolute Percentage Error.

    MAPE = average of |actual - predicted| / actual × 100
    Lower is better. Under 10% is good. Under 5% is excellent.
    """
    # Merge actual vs predicted on the same dates
    merged = monthly_data.merge(
        forecast[["ds", "yhat"]], on="ds"
    )

    # MAPE formula
    merged["error_pct"] = (
        abs(merged["y"] - merged["yhat"]) / merged["y"] * 100
    )
    mape = merged["error_pct"].mean()

    print(f"\n  Model Accuracy (MAPE): {mape:.2f}%")
    if mape < 5:
        print("  ✓ Excellent accuracy")
    elif mape < 10:
        print("  ✓ Good accuracy")
    else:
        print("  ⚠ Model needs tuning")

    return mape


# ══════════════════════════════════════════════════════
# STEP 6: BUSINESS RECOMMENDATIONS
# ══════════════════════════════════════════════════════
def generate_recommendations(sales, inventory, forecast_all):

    print("\n" + "=" * 55)
    print("  BUSINESS RECOMMENDATIONS")
    print("=" * 55)

    # 1. Revenue trend
    future = forecast_all[
        forecast_all["ds"] > pd.Timestamp("2024-12-31")
    ]
    avg_forecast = future["yhat"].mean()
    last_actual  = sales[sales["year"] == 2024]["total_amount"].sum() / 12

    growth = ((avg_forecast - last_actual) / last_actual) * 100
    print(f"\n 1. REVENUE OUTLOOK")
    print(f"    Avg monthly forecast : ₹{avg_forecast:,.0f}")
    print(f"    vs 2024 monthly avg  : ₹{last_actual:,.0f}")
    print(f"    Projected growth     : {growth:+.1f}%")
    if growth > 0:
        print(f"    → Increase procurement budget by ~{growth:.0f}%")
        print(f"    → Negotiate volume discounts with top suppliers")
    else:
        print(f"    → Investigate causes of declining demand")
        print(f"    → Consider promotional campaigns")

    # 2. Low season months
    monthly_avg = sales.groupby("month")["total_amount"].sum()
    low_months  = monthly_avg.nsmallest(3).index.tolist()
    month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                   7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    print(f"\n 2. SEASONAL PLANNING")
    low_names = [month_names[m] for m in low_months]
    print(f"    Historically weak months: {', '.join(low_names)}")
    print(f"    → Run loyalty promotions in {low_names[0]} and {low_names[1]}")
    print(f"    → Offer combo deals on vitamins/supplements")
    print(f"    → Push OTC products with discount coupons")

    # 3. Inventory risk
    near_expiry_value = inventory[
        inventory["is_near_expiry"]
    ]["stock_value"].sum()
    print(f"\n 3. INVENTORY RISK")
    print(f"    Near-expiry stock value : ₹{near_expiry_value:,.0f}")
    print(f"    → Run 'best-before deals' for near-expiry items")
    print(f"    → Negotiate return-to-supplier for slow movers")
    print(f"    → Implement FEFO picking (First Expire First Out)")

    # 4. Top category action
    top_cat = (sales.groupby("category")["total_amount"]
               .sum().idxmax())
    print(f"\n 4. CATEGORY STRATEGY")
    print(f"    Highest revenue category: {top_cat}")
    print(f"    → Expand {top_cat} SKUs with generic alternatives")
    print(f"    → Ensure 3-month safety stock for top {top_cat} SKUs")
    print(f"    → Train staff on {top_cat} product upselling")

    print("=" * 55)


# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
if __name__ == "__main__":

    print("=" * 55)
    print("  Demand Forecasting Module")
    print("=" * 55)

    # Load data
    sales     = pd.read_csv(f"{PROC_PATH}sales_clean.csv",
                             parse_dates=["sales_date"])
    inventory = pd.read_csv(f"{PROC_PATH}inventory_clean.csv",
                             parse_dates=["expiry_date"])

    # ── Forecast 1: All categories combined ──────────
    print("\n[1/3] Forecasting total sales...")
    monthly_all      = prepare_monthly_data(sales)
    model_all, fc_all = run_forecast(monthly_all,
                                      periods=6,
                                      label="All Categories")
    future_all       = plot_forecast(monthly_all, fc_all,
                                      label="All Categories")
    print_forecast_table(future_all, "All Categories")
    check_accuracy(monthly_all, fc_all)

    # ── Forecast 2: Diabetes category ────────────────
    print("\n[2/3] Forecasting Diabetes category...")
    monthly_dia       = prepare_monthly_data(sales, category="Diabetes")
    model_dia, fc_dia = run_forecast(monthly_dia,
                                      periods=6,
                                      label="Diabetes")
    future_dia        = plot_forecast(monthly_dia, fc_dia,
                                      label="Diabetes")
    print_forecast_table(future_dia, "Diabetes")
    check_accuracy(monthly_dia, fc_dia)

    # ── Forecast 3: Vitamins & Supplements ───────────
    print("\n[3/3] Forecasting Vitamins & Supplements...")
    monthly_vit       = prepare_monthly_data(sales,
                            category="Vitamins & Supplements")
    model_vit, fc_vit = run_forecast(monthly_vit,
                                      periods=6,
                                      label="Vitamins & Supplements")
    future_vit        = plot_forecast(monthly_vit, fc_vit,
                                      label="Vitamins & Supplements")
    print_forecast_table(future_vit, "Vitamins & Supplements")
    check_accuracy(monthly_vit, fc_vit)

    # ── Business recommendations ──────────────────────
    generate_recommendations(sales, inventory, fc_all)

    print("\n\n✓ Forecasting complete")
    print(f"  Charts saved to images/")
    print(f"  Open images/forecast_all_categories.png to view")