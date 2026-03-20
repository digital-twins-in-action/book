import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

filename = "datapipeline/2025_export.parquet"
df = pd.read_parquet(filename)

# Select both relevant columns
features = ["voltage_fridge", "power_fridge"]

analysis_df = df[features].copy()

# Rename for clarity (optional, but matches your previous pattern)
analysis_df.rename(
    columns={"voltage_fridge": "voltage", "power_fridge": "power"}, inplace=True
)

analysis_df = analysis_df.dropna()

# Create X using both voltage and power
X = analysis_df[["voltage", "power"]].values

clf = IsolationForest(contamination=0.01, random_state=42)
analysis_df["anomaly"] = clf.fit_predict(X)

anomalies = analysis_df[analysis_df["anomaly"] == -1]

print(f"Number of anomalies detected: {len(anomalies)}")
print(anomalies.head())

# Separate the data for easier plotting
normal_data = analysis_df[analysis_df["anomaly"] == 1]
anomaly_data = analysis_df[analysis_df["anomaly"] == -1]

plt.figure(figsize=(10, 6))

# Plot normal points (Blue, transparent to see density)
plt.scatter(
    normal_data["voltage"],
    normal_data["power"],
    c="blue",
    s=10,
    alpha=0.3,
    label="Normal Operation",
)

# Plot anomalies (Red, slightly larger to stand out)
plt.scatter(
    anomaly_data["voltage"],
    anomaly_data["power"],
    c="red",
    s=60,
    edgecolor="k",
    label="Anomaly",
)

plt.title("Refrigerator anomaly detection: voltage versus power")
plt.xlabel("Voltage (V)")
plt.ylabel("Power (W)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)

plt.show()
