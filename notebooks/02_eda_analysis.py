
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

DATA_PATH = "data/cleaned_sales_data.csv"
CHART_PATH = Path("static/charts")

# Create charts folder if it does not exist
CHART_PATH.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. LOAD DATASET
# ==========================================

df = pd.read_csv(DATA_PATH)

# Convert Order_Date to datetime
df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")


print("=" * 60)
print("AI BUSINESS INTELLIGENCE PROJECT")
print("EXPLORATORY DATA ANALYSIS")
print("=" * 60)


# ==========================================
# 3. BASIC DATA INFORMATION
# ==========================================

print("\n--- DATASET INFORMATION ---")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())


# ==========================================
# 4. BUSINESS KPIs
# ==========================================

total_sales = df["Total_Sales"].sum()
total_orders = df["Order_ID"].nunique()
total_quantity = df["Quantity"].sum()
average_order_value = total_sales / total_orders
total_customers = df["Customer_ID"].nunique()


print("\n--- BUSINESS KPIs ---")
print(f"Total Sales: ₹{total_sales:,.2f}")
print(f"Total Orders: {total_orders:,}")
print(f"Total Quantity Sold: {total_quantity:,}")
print(f"Total Customers: {total_customers:,}")
print(f"Average Order Value: ₹{average_order_value:,.2f}")


# ==========================================
# 5. CATEGORY-WISE SALES
# ==========================================

category_sales = (
    df.groupby("Category")["Total_Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n--- CATEGORY-WISE SALES ---")
print(category_sales)


# ==========================================
# 6. REGION-WISE SALES
# ==========================================

region_sales = (
    df.groupby("Region")["Total_Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n--- REGION-WISE SALES ---")
print(region_sales)


# ==========================================
# 7. PRODUCT-WISE SALES
# ==========================================

product_sales = (
    df.groupby("Product")["Total_Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n--- PRODUCT-WISE SALES ---")
print(product_sales)


# ==========================================
# 8. MONTHLY SALES
# ==========================================

df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)

monthly_sales = (
    df.groupby("Month")["Total_Sales"]
    .sum()
)

print("\n--- MONTHLY SALES ---")
print(monthly_sales)


# ==========================================
# 9. CUSTOMER-WISE SALES
# ==========================================

customer_sales = (
    df.groupby("Customer_ID")["Total_Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n--- TOP 10 CUSTOMERS ---")
print(customer_sales.head(10))


# ==========================================
# 10. CHART 1 — CATEGORY SALES
# ==========================================

plt.figure(figsize=(10, 6))

sns.barplot(
    x=category_sales.index,
    y=category_sales.values
)

plt.title("Sales by Category")
plt.xlabel("Category")
plt.ylabel("Total Sales")

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig(CHART_PATH / "category_sales.png")
plt.close()


# ==========================================
# 11. CHART 2 — REGION SALES
# ==========================================

plt.figure(figsize=(10, 6))

sns.barplot(
    x=region_sales.index,
    y=region_sales.values
)

plt.title("Sales by Region")
plt.xlabel("Region")
plt.ylabel("Total Sales")

plt.tight_layout()

plt.savefig(CHART_PATH / "region_sales.png")
plt.close()


# ==========================================
# 12. CHART 3 — PRODUCT SALES
# ==========================================

plt.figure(figsize=(10, 6))

sns.barplot(
    x=product_sales.index,
    y=product_sales.values
)

plt.title("Sales by Product")
plt.xlabel("Product")
plt.ylabel("Total Sales")

plt.xticks(rotation=30)
plt.tight_layout()

plt.savefig(CHART_PATH / "product_sales.png")
plt.close()


# ==========================================
# 13. CHART 4 — MONTHLY SALES TREND
# ==========================================

plt.figure(figsize=(12, 6))

plt.plot(
    monthly_sales.index,
    monthly_sales.values,
    marker="o"
)

plt.title("Monthly Sales Trend")
plt.xlabel("Month")
plt.ylabel("Total Sales")

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(CHART_PATH / "monthly_sales.png")
plt.close()


# ==========================================
# 14. CHART 5 — SALES DISTRIBUTION
# ==========================================

plt.figure(figsize=(10, 6))

sns.histplot(
    df["Total_Sales"],
    bins=30,
    kde=True
)

plt.title("Sales Distribution")
plt.xlabel("Order Sales")
plt.ylabel("Number of Orders")

plt.tight_layout()

plt.savefig(CHART_PATH / "sales_distribution.png")
plt.close()


# ==========================================
# 15. SAVE SUMMARY FILES
# ==========================================

category_sales.to_csv(
    "data/category_sales_summary.csv",
    header=["Total_Sales"]
)

region_sales.to_csv(
    "data/region_sales_summary.csv",
    header=["Total_Sales"]
)

product_sales.to_csv(
    "data/product_sales_summary.csv",
    header=["Total_Sales"]
)

monthly_sales.to_csv(
    "data/monthly_sales_summary.csv",
    header=["Total_Sales"]
)


# ==========================================
# 16. FINAL REPORT
# ==========================================

print("\n" + "=" * 60)
print("EDA COMPLETED SUCCESSFULLY")
print("=" * 60)

print("\nCharts saved in:")
print("static/charts/")

print("\nGenerated charts:")
print("1. category_sales.png")
print("2. region_sales.png")
print("3. product_sales.png")
print("4. monthly_sales.png")
print("5. sales_distribution.png")

print("\nSummary files saved in:")
print("data/")

print("\n" + "=" * 60)
