import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

filename = "datapipeline/2025_export.parquet"
df = pd.read_parquet(filename)

print(df.head(10))

# Drop rows where the target is missing (NaN)
target_col = "f_temp_indoor"
df = df.dropna(subset=[target_col])

# Define Features
feature_cols = [
    "f_t_lag_3h",  # Thermal Memory
    "f_temp_outdoor",
    "f_solar_norm",  # External Forcing
    "f_hour_sin",
    "f_hour_cos",  # Time Context
]

split_date = "2025-11-01"
train = df.loc[df.index < split_date].copy()
test = df.loc[df.index >= split_date].copy()

X_train, y_train = train[feature_cols], train[target_col]
X_test, y_test = test[feature_cols], test[target_col]

model = HistGradientBoostingRegressor(random_state=21)
model.fit(X_train, y_train)

test["prediction"] = model.predict(X_test)
mae = mean_absolute_error(test[target_col], test["prediction"])

print(f"Mean Absolute Error (Normalized): {mae:.4f}")

subset = test.loc["2025-11-01":"2025-11-07"]

plt.figure(figsize=(10, 5))
plt.plot(
    subset.index, subset[target_col], label="Actual Temp", color="black", alpha=0.6
)
plt.plot(
    subset.index,
    subset["prediction"],
    label="Prediction",
    color="orange",
    linestyle="--",
)

plt.xlabel("Date", fontsize=20, fontweight="bold")
plt.ylabel("Temperature", fontsize=20, fontweight="bold")

plt.tick_params(axis="both", labelsize=16)
plt.legend(fontsize=16, framealpha=0.9)

plt.tight_layout()
plt.show()
