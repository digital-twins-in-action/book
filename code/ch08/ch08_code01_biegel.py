import pandas as pd

df = pd.read_csv("data/powerpal.csv")

df["datetime_local"] = pd.to_datetime(df["datetime_local"])

df["datetime_local"] = pd.to_datetime(df["datetime_local"])
df = df.set_index("datetime_local").tz_localize("Australia/Perth")
resampled_df = df.resample("h").agg({"watt_hours": "sum", "cost_dollars": "sum"})

print(resampled_df)
