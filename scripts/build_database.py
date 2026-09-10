import sqlite3
import pandas as pd

conn = sqlite3.connect("../data/blinkit_lucknow.db")

stores = pd.read_csv("../data/stores.csv")
products = pd.read_csv("../data/products.csv")
orders = pd.read_csv("../data/orders.csv", parse_dates=["timestamp"])
inventory = pd.read_csv("../data/inventory_snapshot.csv", parse_dates=["date"])

stores.to_sql("stores", conn, if_exists="replace", index=False)
products.to_sql("products", conn, if_exists="replace", index=False)
orders.to_sql("orders", conn, if_exists="replace", index=False)
inventory.to_sql("inventory_snapshot", conn, if_exists="replace", index=False)

conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_store ON orders(store_id);")
conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_sku ON orders(sku_id);")
conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_ts ON orders(timestamp);")

conn.commit()
conn.close()
print("blinkit_lucknow.db created successfully with 4 tables + indexes.")