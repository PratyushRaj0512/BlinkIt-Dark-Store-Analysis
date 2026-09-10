import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# ------------------------------------------------------------------
# 1. STORE MASTER (12 dark stores across real Lucknow localities)
# ------------------------------------------------------------------
stores = pd.DataFrame([
    {"store_id": "LKO01", "store_name": "Gomti Nagar",   "zone": "East",    "lat": 26.8541, "lon": 81.0067, "store_tier": "Tier1"},
    {"store_id": "LKO02", "store_name": "Hazratganj",    "zone": "Central", "lat": 26.8467, "lon": 80.9462, "store_tier": "Tier1"},
    {"store_id": "LKO03", "store_name": "Indira Nagar",  "zone": "East",    "lat": 26.8809, "lon": 80.9989, "store_tier": "Tier2"},
    {"store_id": "LKO04", "store_name": "Aliganj",       "zone": "North",   "lat": 26.8912, "lon": 80.9328, "store_tier": "Tier2"},
    {"store_id": "LKO05", "store_name": "Alambagh",      "zone": "South",   "lat": 26.8103, "lon": 80.9077, "store_tier": "Tier2"},
    {"store_id": "LKO06", "store_name": "Chinhat",       "zone": "East",    "lat": 26.8783, "lon": 81.0553, "store_tier": "Tier3"},
    {"store_id": "LKO07", "store_name": "Mahanagar",     "zone": "North",   "lat": 26.8674, "lon": 80.9482, "store_tier": "Tier2"},
    {"store_id": "LKO08", "store_name": "Aminabad",      "zone": "Central", "lat": 26.8467, "lon": 80.9219, "store_tier": "Tier1"},
    {"store_id": "LKO09", "store_name": "Rajajipuram",   "zone": "West",    "lat": 26.8267, "lon": 80.8794, "store_tier": "Tier3"},
    {"store_id": "LKO10", "store_name": "Telibagh",      "zone": "South",   "lat": 26.7742, "lon": 80.9358, "store_tier": "Tier3"},
    {"store_id": "LKO11", "store_name": "Jankipuram",    "zone": "North",   "lat": 26.9187, "lon": 80.9548, "store_tier": "Tier3"},
    {"store_id": "LKO12", "store_name": "Cantt",         "zone": "Central", "lat": 26.8306, "lon": 80.9598, "store_tier": "Tier2"},
])

# ------------------------------------------------------------------
# 2. PRODUCT MASTER (18 SKUs across 6 categories)
# ------------------------------------------------------------------
products = pd.DataFrame([
    {"sku_id": "SKU001", "sku_name": "Amul Toned Milk 500ml",     "category": "Dairy",        "price": 27,  "shelf_life_days": 3},
    {"sku_id": "SKU002", "sku_name": "Amul Butter 100g",          "category": "Dairy",        "price": 58,  "shelf_life_days": 60},
    {"sku_id": "SKU003", "sku_name": "Brown Eggs (6 pcs)",        "category": "Dairy",        "price": 48,  "shelf_life_days": 15},
    {"sku_id": "SKU004", "sku_name": "Tomato 500g",               "category": "Fruits & Veg", "price": 22,  "shelf_life_days": 5},
    {"sku_id": "SKU005", "sku_name": "Onion 1kg",                 "category": "Fruits & Veg", "price": 35,  "shelf_life_days": 14},
    {"sku_id": "SKU006", "sku_name": "Banana Dozen",              "category": "Fruits & Veg", "price": 45,  "shelf_life_days": 5},
    {"sku_id": "SKU007", "sku_name": "Lays Classic 52g",          "category": "Snacks",       "price": 20,  "shelf_life_days": 120},
    {"sku_id": "SKU008", "sku_name": "Maggi Noodles 70g",         "category": "Snacks",       "price": 14,  "shelf_life_days": 240},
    {"sku_id": "SKU009", "sku_name": "Britannia Good Day 100g",   "category": "Snacks",       "price": 30,  "shelf_life_days": 180},
    {"sku_id": "SKU010", "sku_name": "Coca-Cola 750ml",           "category": "Beverages",    "price": 40,  "shelf_life_days": 270},
    {"sku_id": "SKU011", "sku_name": "Real Fruit Juice 1L",       "category": "Beverages",    "price": 110, "shelf_life_days": 180},
    {"sku_id": "SKU012", "sku_name": "Bisleri Water 1L",          "category": "Beverages",    "price": 20,  "shelf_life_days": 365},
    {"sku_id": "SKU013", "sku_name": "Surf Excel 1kg",            "category": "Household",    "price": 130, "shelf_life_days": 720},
    {"sku_id": "SKU014", "sku_name": "Colgate Toothpaste 100g",   "category": "Personal Care","price": 55,  "shelf_life_days": 730},
    {"sku_id": "SKU015", "sku_name": "Dettol Handwash 200ml",     "category": "Personal Care","price": 65,  "shelf_life_days": 730},
    {"sku_id": "SKU016", "sku_name": "boAt Earbuds",              "category": "Electronics",  "price": 1499,"shelf_life_days": 3650},
    {"sku_id": "SKU017", "sku_name": "Phone Charging Cable",      "category": "Electronics",  "price": 299, "shelf_life_days": 3650},
    {"sku_id": "SKU018", "sku_name": "Birthday Candles Pack",     "category": "General",      "price": 40,  "shelf_life_days": 3650},
])

# Demand weight = relative popularity of an SKU (drives Poisson lambda)
demand_weight = {
    "SKU001": 9.0, "SKU002": 3.5, "SKU003": 4.0, "SKU004": 8.5, "SKU005": 7.5,
    "SKU006": 6.0, "SKU007": 5.5, "SKU008": 6.5, "SKU009": 3.0, "SKU010": 4.5,
    "SKU011": 2.0, "SKU012": 5.0, "SKU013": 1.8, "SKU014": 1.5, "SKU015": 1.2,
    "SKU016": 0.3, "SKU017": 0.8, "SKU018": 0.5,
}

# Store demand multiplier (Tier1 = busiest)
store_multiplier = {"Tier1": 1.6, "Tier2": 1.0, "Tier3": 0.55}

# ------------------------------------------------------------------
# 3. HOURLY DEMAND CURVE (quick-commerce: breakfast + evening peaks)
# ------------------------------------------------------------------
hour_curve = {
    0: 0.1, 1: 0.05, 2: 0.03, 3: 0.02, 4: 0.02, 5: 0.05,
    6: 0.3, 7: 0.6, 8: 0.9, 9: 0.8, 10: 0.6, 11: 0.5,
    12: 0.7, 13: 0.6, 14: 0.4, 15: 0.4, 16: 0.5, 17: 0.7,
    18: 1.0, 19: 1.3, 20: 1.4, 21: 1.2, 22: 0.7, 23: 0.3,
}

START_DATE = datetime(2026, 8, 1)
NUM_DAYS = 30

order_rows = []
inventory_rows = []
order_id_counter = 1

for store in stores.itertuples():
    opening_stock = {sku: np.random.randint(40, 120) for sku in products["sku_id"]}

    for day in range(NUM_DAYS):
        current_date = START_DATE + timedelta(days=day)
        is_weekend = current_date.weekday() >= 5
        payday_bump = 1.25 if current_date.day <= 3 else 1.0
        weekend_bump = 1.2 if is_weekend else 1.0

        for sku_row in products.itertuples():
            sku = sku_row.sku_id
            replenish_qty = np.random.randint(15, 45)
            opening_stock[sku] = opening_stock[sku] + replenish_qty
            inventory_rows.append({
                "date": current_date.date(),
                "store_id": store.store_id,
                "sku_id": sku,
                "opening_stock": opening_stock[sku],
            })

        for hour in range(24):
            hour_factor = hour_curve[hour]
            for sku_row in products.itertuples():
                sku = sku_row.sku_id
                base_lambda = (
                    demand_weight[sku]
                    * store_multiplier[store.store_tier]
                    * hour_factor
                    * payday_bump
                    * weekend_bump
                )
                demand_qty = np.random.poisson(max(base_lambda, 0.01))
                if demand_qty == 0:
                    continue

                available = opening_stock[sku]
                fulfilled_qty = min(demand_qty, available)
                stockout_flag = 1 if fulfilled_qty < demand_qty else 0
                opening_stock[sku] = max(available - fulfilled_qty, 0)

                order_rows.append({
                    "order_id": f"ORD{order_id_counter:07d}",
                    "timestamp": datetime.combine(current_date.date(), datetime.min.time()) + timedelta(hours=hour),
                    "store_id": store.store_id,
                    "sku_id": sku,
                    "demand_qty": demand_qty,
                    "fulfilled_qty": fulfilled_qty,
                    "lost_qty": demand_qty - fulfilled_qty,
                    "stockout_flag": stockout_flag,
                    "unit_price": products.loc[products.sku_id == sku, "price"].values[0],
                })
                order_id_counter += 1

orders_df = pd.DataFrame(order_rows)
inventory_df = pd.DataFrame(inventory_rows)

orders_df["revenue"] = orders_df["fulfilled_qty"] * orders_df["unit_price"]
orders_df["lost_revenue"] = orders_df["lost_qty"] * orders_df["unit_price"]

stores.to_csv("../data/stores.csv", index=False)
products.to_csv("../data/products.csv", index=False)
orders_df.to_csv("../data/orders.csv", index=False)
inventory_df.to_csv("../data/inventory_snapshot.csv", index=False)

print("Data generation complete.")
print(f"Stores           : {len(stores)}")
print(f"Orders rows      : {len(orders_df):,}")
print(f"Inventory rows   : {len(inventory_df):,}")
print(f"Total lost revenue (30 days, {len(stores)} stores): Rs. {orders_df['lost_revenue'].sum():,.0f}")