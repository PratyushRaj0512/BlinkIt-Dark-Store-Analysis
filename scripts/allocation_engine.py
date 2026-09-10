"""
allocation_engine.py
---------------------
Answers: "If we reallocate the SAME total inventory across stores in
proportion to demand (instead of the current, roughly even split), how
much lost revenue can we recover?"
"""

import pandas as pd
import numpy as np

orders = pd.read_csv("../data/orders.csv", parse_dates=["timestamp"])
products = pd.read_csv("../data/products.csv")

summary = (
    orders.groupby(["store_id", "sku_id"])
    .agg(
        total_demand=("demand_qty", "sum"),
        total_fulfilled=("fulfilled_qty", "sum"),
        total_lost_units=("lost_qty", "sum"),
        lost_revenue=("lost_revenue", "sum"),
        unit_price=("unit_price", "first"),
    )
    .reset_index()
)

sku_totals = summary.groupby("sku_id")["total_demand"].sum().rename("citywide_demand")
summary = summary.merge(sku_totals, on="sku_id")
summary["demand_share"] = summary["total_demand"] / summary["citywide_demand"]

citywide_budget = summary.groupby("sku_id")["total_fulfilled"].sum().rename("citywide_budget")
summary = summary.merge(citywide_budget, on="sku_id")

summary["recommended_allocation"] = (summary["demand_share"] * summary["citywide_budget"]).round(0)
summary["current_allocation"] = summary["total_fulfilled"]
summary["allocation_delta"] = summary["recommended_allocation"] - summary["current_allocation"]

def estimate_new_lost_units(row):
    if row["recommended_allocation"] >= row["total_demand"]:
        return 0
    return row["total_demand"] - row["recommended_allocation"]

summary["new_lost_units"] = summary.apply(estimate_new_lost_units, axis=1).clip(lower=0)
summary["recovered_units"] = (summary["total_lost_units"] - summary["new_lost_units"]).clip(lower=0)
summary["recovered_revenue"] = summary["recovered_units"] * summary["unit_price"]

total_lost_revenue_before = summary["lost_revenue"].sum()
total_recovered_revenue = summary["recovered_revenue"].sum()
pct_recovered = total_recovered_revenue / total_lost_revenue_before * 100

print("=" * 60)
print("INVENTORY REALLOCATION SIMULATION - RESULTS")
print("=" * 60)
print(f"Baseline lost revenue (30 days): Rs. {total_lost_revenue_before:,.0f}")
print(f"Recoverable revenue            : Rs. {total_recovered_revenue:,.0f}")
print(f"Percentage of leakage recovered: {pct_recovered:.1f}%")
print(f"Projected ANNUALIZED recovery   : Rs. {total_recovered_revenue*12:,.0f}")
print("=" * 60)

summary.merge(products[["sku_id", "sku_name", "category"]], on="sku_id") \
    .sort_values("recovered_revenue", ascending=False) \
    .to_csv("../data/allocation_recommendation.csv", index=False)

print("\nSaved to ../data/allocation_recommendation.csv")