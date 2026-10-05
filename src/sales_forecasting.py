
import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# 1. PROJECT PATHS
# ==========================================

DATA_PATH = "data/cleaned_sales_data.csv"
MODEL_PATH = Path("models/sales_forecasting_model.joblib")
FORECAST_PATH = Path("data/sales_forecast.csv")

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. LOAD DATA
# ==========================================

print("=" * 60)
print("AI BUSINESS INTELLIGENCE PROJECT")
print("SALES FORECASTING - MACHINE LEARNING")
print("=" * 60)

df = pd.read_csv(DATA_PATH)

df["Order_Date"] = pd.to_datetime(
    df["Order_Date"],
    errors="coerce"
)

print("\nDataset loaded successfully.")
print("Total rows:", len(df))


# ==========================================
# 3. CREATE MONTHLY SALES DATA
# ==========================================

df["Month"] = df["Order_Date"].dt.to_period("M")

monthly_sales = (
    df.groupby("Month")["Total_Sales"]
    .sum()
    .reset_index()
)

monthly_sales["Month"] = monthly_sales["Month"].dt.to_timestamp()

monthly_sales = monthly_sales.sort_values("Month").reset_index(drop=True)


print("\n--- MONTHLY SALES DATA ---")
print(monthly_sales)


# ==========================================
# 4. FEATURE ENGINEERING
# ==========================================

monthly_sales["Year"] = monthly_sales["Month"].dt.year
monthly_sales["Month_Number"] = monthly_sales["Month"].dt.month

# Sequential time index
monthly_sales["Time_Index"] = np.arange(len(monthly_sales))

# Lag features
monthly_sales["Lag_1"] = monthly_sales["Total_Sales"].shift(1)
monthly_sales["Lag_2"] = monthly_sales["Total_Sales"].shift(2)
monthly_sales["Lag_3"] = monthly_sales["Total_Sales"].shift(3)

# Rolling average
monthly_sales["Rolling_Mean_3"] = (
    monthly_sales["Total_Sales"]
    .shift(1)
    .rolling(window=3)
    .mean()
)


# ==========================================
# 5. REMOVE ROWS WITH MISSING FEATURES
# ==========================================

model_data = monthly_sales.dropna().reset_index(drop=True)

print("\n--- MODEL DATA ---")
print("Rows available for ML:", len(model_data))

if len(model_data) < 8:
    raise ValueError(
        "Not enough monthly data for a meaningful ML demonstration. "
        "At least 8 usable months are recommended."
    )


# ==========================================
# 6. DEFINE FEATURES AND TARGET
# ==========================================

features = [
    "Year",
    "Month_Number",
    "Time_Index",
    "Lag_1",
    "Lag_2",
    "Lag_3",
    "Rolling_Mean_3"
]

X = model_data[features]
y = model_data["Total_Sales"]


# ==========================================
# 7. TIME-BASED TRAIN / TEST SPLIT
# ==========================================

# Do NOT randomly shuffle time-series data.
# Earlier months -> training
# Later months -> testing

split_index = int(len(model_data) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("\n--- TRAIN / TEST SPLIT ---")
print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))


# ==========================================
# 8. CREATE ML MODEL
# ==========================================

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=8,
    random_state=42,
    min_samples_leaf=2
)


# ==========================================
# 9. TRAIN MODEL
# ==========================================

print("\nTraining Random Forest model...")

model.fit(X_train, y_train)

print("Model training completed.")


# ==========================================
# 10. TEST MODEL
# ==========================================

predictions = model.predict(X_test)


# ==========================================
# 11. MODEL EVALUATION
# ==========================================

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)


print("\n--- MODEL EVALUATION ---")
print(f"MAE  : ₹{mae:,.2f}")
print(f"RMSE : ₹{rmse:,.2f}")
print(f"R²   : {r2:.4f}")


# ==========================================
# 12. DISPLAY ACTUAL VS PREDICTED
# ==========================================

comparison = pd.DataFrame({
    "Month": model_data.iloc[split_index:]["Month"].values,
    "Actual_Sales": y_test.values,
    "Predicted_Sales": predictions
})

print("\n--- ACTUAL VS PREDICTED SALES ---")
print(comparison.to_string(index=False))


# ==========================================
# 13. TRAIN FINAL MODEL ON ALL DATA
# ==========================================

final_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=8,
    random_state=42,
    min_samples_leaf=2
)

final_model.fit(X, y)


# ==========================================
# 14. CREATE FUTURE FORECASTS
# ==========================================

forecast_months = 3

history = monthly_sales[
    ["Month", "Total_Sales"]
].copy()

future_predictions = []


for _ in range(forecast_months):

    next_month = (
        history["Month"].max()
        + pd.DateOffset(months=1)
    )

    next_time_index = len(monthly_sales) + len(future_predictions)

    lag_1 = history["Total_Sales"].iloc[-1]

    lag_2 = history["Total_Sales"].iloc[-2]

    lag_3 = history["Total_Sales"].iloc[-3]

    rolling_mean_3 = (
        history["Total_Sales"]
        .iloc[-3:]
        .mean()
    )

    future_features = pd.DataFrame([{
        "Year": next_month.year,
        "Month_Number": next_month.month,
        "Time_Index": next_time_index,
        "Lag_1": lag_1,
        "Lag_2": lag_2,
        "Lag_3": lag_3,
        "Rolling_Mean_3": rolling_mean_3
    }])

    predicted_sales = final_model.predict(
        future_features
    )[0]

    predicted_sales = max(
        0,
        float(predicted_sales)
    )

    future_predictions.append({
        "Month": next_month,
        "Forecasted_Sales": predicted_sales
    })

    # Add prediction to history so next month
    # can use the previous forecast as lag.
    history = pd.concat(
        [
            history,
            pd.DataFrame([{
                "Month": next_month,
                "Total_Sales": predicted_sales
            }])
        ],
        ignore_index=True
    )


forecast_df = pd.DataFrame(
    future_predictions
)


# ==========================================
# 15. SAVE FORECAST
# ==========================================

forecast_df["Month"] = forecast_df[
    "Month"
].dt.strftime("%Y-%m")

forecast_df.to_csv(
    FORECAST_PATH,
    index=False
)


# ==========================================
# 16. SAVE TRAINED MODEL
# ==========================================

model_package = {
    "model": final_model,
    "features": features,
    "model_name": "RandomForestRegressor",
    "forecast_horizon_months": forecast_months
}

joblib.dump(
    model_package,
    MODEL_PATH
)


# ==========================================
# 17. DISPLAY FUTURE FORECAST
# ==========================================

print("\n--- FUTURE SALES FORECAST ---")

print(forecast_df.to_string(index=False))


# ==========================================
# 18. FINAL SUMMARY
# ==========================================

print("\n" + "=" * 60)
print("SALES FORECASTING COMPLETED SUCCESSFULLY")
print("=" * 60)

print("\nModel:")
print("Random Forest Regressor")

print("\nEvaluation:")
print(f"MAE  : ₹{mae:,.2f}")
print(f"RMSE : ₹{rmse:,.2f}")
print(f"R²   : {r2:.4f}")

print("\nSaved model:")
print(MODEL_PATH)

print("\nSaved forecast:")
print(FORECAST_PATH)

print("\n" + "=" * 60)

