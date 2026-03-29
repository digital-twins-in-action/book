import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

filename = "datapipeline/2025_export.parquet"
df = pd.read_parquet(filename)

target_col = "pm25_living_room"

if target_col not in df.columns:
    print(f"Error: '{target_col}' not found.")
    print("Available PM columns:", [c for c in df.columns if "pm" in c.lower()])
    raise KeyError(f"Please update 'target_col' with one of the columns above.")

analysis_df = df[[target_col]].dropna().copy()
analysis_df.rename(columns={target_col: "value"}, inplace=True)

window_size = 24  # 24-hour rolling window

analysis_df["rolling_mean"] = analysis_df["value"].rolling(window=window_size).mean()
analysis_df["rolling_std"] = analysis_df["value"].rolling(window=window_size).std()

analysis_df["z_score"] = (
    (analysis_df["value"] - analysis_df["rolling_mean"]) / analysis_df["rolling_std"]
).bfill()

november_df = analysis_df.loc["2025-11"].copy()

z_threshold = 3
anomalies = november_df[np.abs(november_df["z_score"]) > z_threshold]

print(f"Air Quality Anomalies detected in November: {len(anomalies)}")

plt.figure(figsize=(16, 8))

# Plot Raw Data
plt.plot(
    november_df.index,
    november_df["value"],
    label="PM2.5 Concentration",
    color="#2ca02c",
    alpha=0.5,
    linewidth=2,
)

# Plot Rolling Mean
plt.plot(
    november_df.index,
    november_df["rolling_mean"],
    label="24h Rolling Mean",
    color="black",
    linestyle="--",
    linewidth=2.5,
)

# Plot the "Normal" Band
plt.fill_between(
    november_df.index,
    november_df["rolling_mean"] - (z_threshold * november_df["rolling_std"]),
    november_df["rolling_mean"] + (z_threshold * november_df["rolling_std"]),
    color="gray",
    alpha=0.2,
    label=f"Normal Range (±{z_threshold}$\\sigma$)",
)

# Plot Anomalies
plt.scatter(
    anomalies.index,
    anomalies["value"],
    color="red",
    s=120,
    zorder=5,
    label=f"Anomaly (> {z_threshold}$\\sigma$)",
)

plt.xlabel("Date", fontsize=20, fontweight="bold")
plt.ylabel("Concentration (µg/m³)", fontsize=20, fontweight="bold")

plt.legend(loc="upper left", fontsize=16, framealpha=0.9)
plt.grid(True, alpha=0.3)

ax = plt.gca()
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

ax.tick_params(axis="both", labelsize=16)

plt.tight_layout()

plt.show()
