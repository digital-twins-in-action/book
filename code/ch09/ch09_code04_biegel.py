import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1. Load Data
filename = "datapipeline/2025_export.parquet"
df = pd.read_parquet(filename)

# 2. Select Target: PM2.5 (Air Quality)
# We assume the column is named 'pm2.5_outdoor' based on your schema.
# If your sensor uses 'pm25', change this to 'pm25_outdoor'.
target_col = "pm25_living_room"

# Verify column exists before proceeding
if target_col not in df.columns:
    # Fallback to help you find the right name
    print(f"Error: '{target_col}' not found.")
    print("Available PM columns:", [c for c in df.columns if "pm" in c.lower()])
    raise KeyError(f"Please update 'target_col' with one of the columns above.")

analysis_df = df[[target_col]].dropna().copy()
analysis_df.rename(columns={target_col: "value"}, inplace=True)

# 3. Statistical Calculations (Calculate on ALL data first)
window_size = 24  # 24-hour rolling window

analysis_df["rolling_mean"] = analysis_df["value"].rolling(window=window_size).mean()
analysis_df["rolling_std"] = analysis_df["value"].rolling(window=window_size).std()

analysis_df["z_score"] = (
    (analysis_df["value"] - analysis_df["rolling_mean"]) / analysis_df["rolling_std"]
).bfill()

# 4. Filter for November 2025
# We use .loc[] to correctly slice the datetime index
november_df = analysis_df.loc["2025-11"].copy()

# 5. Anomaly Detection
# Air quality spikes are often one-sided (high values are bad),
# but Z-score captures unusual lows too. We'll stick to absolute deviation.
z_threshold = 3
anomalies = november_df[np.abs(november_df["z_score"]) > z_threshold]

print(f"Air Quality Anomalies detected in November: {len(anomalies)}")

# 6. Visualization
plt.figure(figsize=(15, 7))

# Plot Raw Data
plt.plot(
    november_df.index,
    november_df["value"],
    label="PM2.5 Concentration",
    color="#2ca02c",
    alpha=0.5,
)

# Plot Rolling Mean
plt.plot(
    november_df.index,
    november_df["rolling_mean"],
    label="24h Rolling Mean",
    color="black",
    linestyle="--",
    linewidth=1,
)

# Plot the "Normal" Band
plt.fill_between(
    november_df.index,
    november_df["rolling_mean"] - (z_threshold * november_df["rolling_std"]),
    november_df["rolling_mean"] + (z_threshold * november_df["rolling_std"]),
    color="gray",
    alpha=0.2,
    label=f"Normal Range (±{z_threshold}$\sigma$)",
)

# Plot Anomalies
plt.scatter(
    anomalies.index,
    anomalies["value"],
    color="red",
    s=60,
    zorder=5,
    label=f"Anomaly (> {z_threshold}$\sigma$)",
)

plt.title(
    f"PM2.5 air quality anomalies (threshold: {z_threshold}$\sigma$) - November 2025"
)
plt.ylabel("Concentration (µg/m³)")
plt.legend(loc="upper left")
plt.grid(True, alpha=0.3)

# Format X-Axis
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

plt.gcf().autofmt_xdate()

plt.tight_layout()
plt.show()
