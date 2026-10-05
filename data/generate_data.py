
import pandas as pd
import numpy as np

# Random data ko repeatable banana
np.random.seed(42)

# Products aur unki prices
products = {
    "Laptop": 50000,
    "Mobile": 20000,
    "Headphones": 2000,
    "Keyboard": 1500,
    "Monitor": 12000
}

categories = {
    "Laptop": "Electronics",
    "Mobile": "Electronics",
    "Headphones": "Accessories",
    "Keyboard": "Accessories",
    "Monitor": "Electronics"
}

regions = ["North", "South", "East", "West"]

# Number of orders
n = 1000

# Generate sales data
product_list = np.random.choice(list(products.keys()), n)
quantity = np.random.randint(1, 6, n)
unit_price = [products[p] for p in product_list]
discount_pct = np.random.choice(
    [0, 0.05, 0.10, 0.15], n
)

df = pd.DataFrame({
    "Order_ID": [f"ORD{i:04d}" for i in range(1, n + 1)],
    "Order_Date": np.random.choice(
        pd.date_range("2025-01-01", "2025-12-31"),
        n
    ),
    "Customer_ID": np.random.choice(
        [f"CUST{i:03d}" for i in range(1, 301)], n
    ),
    "Product": product_list,
    "Category": [categories[p] for p in product_list],
    "Region": np.random.choice(regions, n),
    "Quantity": quantity,
    "Unit_Price": unit_price,
    "Discount_Pct": discount_pct
})

# Calculate final sales amount
df["Total_Sales"] = (
    df["Quantity"] * df["Unit_Price"]
    * (1 - df["Discount_Pct"])
).round(2)

# Save dataset
df.to_csv("data/sales_data.csv", index=False)

print("Dataset created successfully!")
print("Total records:", len(df))
print(df.head())