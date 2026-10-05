
import pandas as pd
import numpy as np

# ==========================================
# 1. LOAD DATASET
# ==========================================

df = pd.read_csv("data/sales_data.csv")

print("=" * 50)
print("AI BUSINESS INTELLIGENCE PROJECT")
print("DATA CLEANING AND QUALITY CHECKS")
print("=" * 50)

# ==========================================
# 2. BASIC DATA INFORMATION
# ==========================================

print("\n--- DATASET PREVIEW ---")
print(df.head())

print("\n--- DATASET SHAPE ---")
print(df.shape)

print("\n--- DATASET INFORMATION ---")
df.info()

# ==========================================
# 3. CHECK MISSING VALUES
# ==========================================

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

# ==========================================
# 4. CHECK DUPLICATES
# ==========================================

print("\n--- DUPLICATE CHECK ---")
print("Duplicate rows:", df.duplicated().sum())
print(
    "Duplicate Order IDs:",
    df["Order_ID"].duplicated().sum()
)

# ==========================================
# 5. CONVERT DATE FORMAT
# ==========================================

df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce"
)

print("\n--- DATE VALIDATION ---")
print(
    "Invalid dates:",
    df["Order_Date"].isna().sum()
)

# ==========================================
# 6. CHECK INVALID VALUES
# ==========================================

print("\n--- INVALID VALUES ---")

print(
    "Invalid quantity:",
    (df["Quantity"] <= 0).sum()
)

print(
    "Invalid unit price:",
    (df["Unit_Price"] <= 0).sum()
)

print(
    "Invalid discount:",
    (
        (df["Discount_Pct"] < 0) |
        (df["Discount_Pct"] > 1)
    ).sum()
)

# ==========================================
# 7. VERIFY SALES CALCULATION
# ==========================================

expected_sales = (
    df["Quantity"]
    * df["Unit_Price"]
    * (1 - df["Discount_Pct"])
)

incorrect_sales = ~np.isclose(
    df["Total_Sales"],
    expected_sales,
    equal_nan=False
)

print(
    "Incorrect sales calculations:",
    incorrect_sales.sum()
)

# ==========================================
# 8. DATA CLEANING
# ==========================================

initial_rows = len(df)

# Remove duplicate Order IDs
df = df.drop_duplicates(
    subset=["Order_ID"],
    keep="first"
)

# Remove rows with invalid dates
df = df.dropna(
    subset=["Order_Date"]
)

# Remove invalid numerical records
df = df[
    (df["Quantity"] > 0) &
    (df["Unit_Price"] > 0) &
    (df["Discount_Pct"].between(0, 1))
].copy()

# Remove records with incorrect sales
df = df[
    np.isclose(
        df["Total_Sales"],
        df["Quantity"]
        * df["Unit_Price"]
        * (1 - df["Discount_Pct"])
    )
].copy()

# ==========================================
# 9. SAVE CLEANED DATASET
# ==========================================

df = df.reset_index(drop=True)

df.to_csv(
    "data/cleaned_sales_data.csv",
    index=False
)

# ==========================================
# 10. FINAL REPORT
# ==========================================

removed_rows = initial_rows - len(df)

print("\n--- CLEANING SUMMARY ---")
print("Initial rows:", initial_rows)
print("Removed rows:", removed_rows)
print("Final rows:", len(df))
print("Final columns:", len(df.columns))

print("\n--- FINAL DATASET ---")
print(df.head())

print("\n--- FINAL MISSING VALUES ---")
print(df.isnull().sum())

print("\nCleaned dataset saved successfully!")
print("File: data/cleaned_sales_data.csv")

print("\n" + "=" * 50)
print("DATA CLEANING COMPLETED")
print("=" * 50)