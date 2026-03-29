import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df = pd.read_csv("datapipeline/2025_export.csv", parse_dates=["datetime_perth"])

start_date = "2025-07-01"
end_date = "2025-12-01"
mask = (df["datetime_perth"] >= start_date) & (df["datetime_perth"] < end_date)
df_subset = df.loc[mask].copy()

df_subset["Grid_Import_kWh"] = df_subset["synergy_consumption"]
df_subset["Export_kWh"] = df_subset["synergy_production"]
df_subset["Solar_kWh"] = df_subset["pv_energy"]
df_subset["Est_Load_kWh"] = (
    df_subset["synergy_consumption"]
    + df_subset["pv_energy"]
    - df_subset["synergy_production"]
)

df_subset["Temperature"] = df_subset["temp_outdoor"]
df_subset["Humidity"] = df_subset["hum_outdoor"]

df_subset.set_index("datetime_perth", inplace=True)

daily_energy = (
    df_subset[["Grid_Import_kWh", "Solar_kWh", "Est_Load_kWh", "Export_kWh"]]
    .resample("D")
    .sum()
)
daily_weather = df_subset[["Temperature", "Humidity"]].resample("D").mean()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), sharex=True)

ax1.plot(
    daily_energy.index,
    daily_energy["Est_Load_kWh"],
    label="Est. Home Load",
    color="black",
    linestyle=":",
    linewidth=2.5,
)
ax1.plot(
    daily_energy.index,
    daily_energy["Solar_kWh"],
    label="Solar Production",
    color="orange",
    alpha=0.8,
    linewidth=2.5,
)

# Fill Import (Blue) - Positive
ax1.fill_between(
    daily_energy.index,
    0,
    daily_energy["Grid_Import_kWh"],
    color="blue",
    alpha=0.3,
    label="Grid Import",
)

# Fill Export (Green) - NEGATIVE
ax1.fill_between(
    daily_energy.index,
    0,
    -daily_energy["Export_kWh"],
    color="green",
    alpha=0.3,
    label="Export",
)

ax1.axhline(0, color="black", linewidth=1.5)

ax1.set_ylabel("Daily energy (kWh)", fontsize=20, fontweight="bold")
ax1.legend(loc="upper left", fontsize=16, framealpha=0.9)
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis="y", labelsize=16)

# Bottom Panel: Weather
color = "tab:red"

ax2.set_ylabel("Avg temperature (°C)", color=color, fontsize=20, fontweight="bold")
ax2.plot(
    daily_weather.index,
    daily_weather["Temperature"],
    color=color,
    label="Temperature",
    linewidth=2.5,
)
ax2.tick_params(axis="y", labelcolor=color, labelsize=16)
ax2.tick_params(axis="x", labelsize=16)

ax3 = ax2.twinx()
color = "tab:cyan"
ax3.set_ylabel("Avg humidity (%)", color=color, fontsize=20, fontweight="bold")
ax3.plot(
    daily_weather.index,
    daily_weather["Humidity"],
    color=color,
    linestyle="--",
    label="Humidity",
    linewidth=2.5,
)
ax3.tick_params(axis="y", labelcolor=color, labelsize=16)

ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax2.xaxis.set_major_locator(mdates.MonthLocator())

plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0, ha="center")

plt.tight_layout()

plt.show()
