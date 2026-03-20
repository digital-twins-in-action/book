import pandas as pd
import numpy as np


def process_synergy(df):
    """Process Synergy: Ensuring Perth time alignment, renaming, and net calc."""
    # Convert timestamp - Synergy data from our previous script is naive
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Synergy is already in Perth time (AWST), but we localize it to
    # match the index type of your other dataframes
    df = df.set_index("timestamp").tz_localize("Australia/Perth")

    # 1. Rename to final schema first
    df = df.rename(
        columns={
            "consumption_kWh": "synergy_consumption",
            "generation_kWh": "synergy_production",
        }
    )

    # 2. Calculate Net (Production - Consumption)
    # Positive = Sending to grid (Export)
    # Negative = Drawing from grid (Import)
    df["synergy_net"] = df["synergy_production"] - df["synergy_consumption"]

    return df


def process_dynamodb(df):

    # Remove entries where temperature is 23.05 and humidity is 0.4
    if "temperature" in df.columns and "humidity" in df.columns:
        anomaly_mask = (df["temperature"] == 23.05) & (df["humidity"] == 0.4)
        removed_count = anomaly_mask.sum()
        print(
            f"Removed {removed_count} readings based on anomaly filter (Temp=23.05, Hum=0.4)."
        )
        df = df[~anomaly_mask].copy()

    """Process DynamoDB: Pivoting partKeys and extracting all available measurements."""
    # 1. Basic Cleaning
    df["timestamp"] = pd.to_datetime(df["sortKey"], unit="ms")
    df = df.set_index("timestamp").tz_localize("UTC").tz_convert("Australia/Perth")

    # 2. Pre-process non-numeric columns (like PIR motion)
    if "pir" in df.columns:
        # Convert strings to numeric activity level (1=motion, 0=idle)
        df["pir"] = df["pir"].map({"trigger": 1, "idle": 0})

    # 3. Define sensor mapping per instructions
    mappings = {
        "a840411971871c86": "outdoor",
        "24e124710b423527": "living_room",
        "a84041ce41845d13": "indoor",
        "24e124148e423058": "fridge",
    }

    # Measurement columns to consider (excluding ID/Time keys)
    exclude_cols = ["sortKey", "partKey", "timestamp"]
    potential_measurements = [c for c in df.columns if c not in exclude_cols]

    # Map for cleaner column naming in the final Digital Twin model
    short_names = {
        "temperature": "temp",
        "humidity": "hum",
        "presssure": "pres",  # Handling the typo 'presssure' in the source data
        "energyConsumption": "energy",
    }

    room_dfs = []

    # 4. Dynamic Extraction and Resampling
    for pkey, room_name in mappings.items():
        # Filter for this specific sensor
        room_data = df[df["partKey"] == pkey][potential_measurements].copy()

        # Drop columns that are entirely NaN for this specific sensor
        room_data = room_data.dropna(how="all", axis=1)

        # Ensure we only include numeric data for the mean calculation
        room_data = room_data.select_dtypes(include=[np.number])

        if not room_data.empty:
            # Rename columns: {short_name}_{room_name}
            room_data.columns = [
                f"{short_names.get(c, c)}_{room_name}" for c in room_data.columns
            ]

            # Resample to hourly mean
            room_resampled = room_data.resample("h").mean()
            room_dfs.append(room_resampled)

    # 5. Combine sensor dataframes
    df_rooms = pd.concat(room_dfs, axis=1)
    return df_rooms


def process_open_meteo(df):
    rename_map = {
        "cloud_cover (%)": "om_cloud_cover",
        "temperature_2m (°C)": "om_temperature",
        "relative_humidity_2m (%)": "om_humidity",
        "rain (mm)": "om_rain",
        "direct_radiation_instant (W/m²)": "om_radiation",
    }

    df = df.rename(columns=rename_map)
    df["time"] = pd.to_datetime(df["time"])
    return df.set_index("time").tz_localize("Australia/Perth").resample("h").mean()


def process_solar_pv(df):
    rename_map = {"Energy [kWh]": "pv_energy", "Power [W]": "pv_power"}
    df = df.rename(columns=rename_map)

    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df = df.set_index("Datetime").tz_localize("Australia/Perth")
    return df.resample("h").agg({"pv_energy": "sum", "pv_power": "mean"})


def process_powerpal(df):
    rename_map = {"watt_hours": "pp_energy", "cost_dollars": "pp_cost"}
    df = df.rename(columns=rename_map)

    df["datetime_local"] = pd.to_datetime(df["datetime_local"])
    df = df.set_index("datetime_local").tz_localize("Australia/Perth")
    return df.resample("h").agg({"pp_energy": "sum"})


def add_ml_features(df):
    """
    Computes normalized, temporal, and lagged features with prefix 'f_'.
    """
    df = df.copy()

    # Helper: Min-Max Normalize
    def min_max_normalize(series):
        if series.max() == series.min():
            return 0
        return (series - series.min()) / (series.max() - series.min())

    # A. Normalization (Creating f_ columns, preserving originals)
    # -----------------------------------------------------------
    if "temp_indoor" in df.columns:
        df["f_temp_indoor"] = min_max_normalize(df["temp_indoor"])

    if "temp_outdoor" in df.columns:
        df["f_temp_outdoor"] = min_max_normalize(df["temp_outdoor"])

    # 'pv_power' comes from process_solar_pv (originally 'Power [W]')
    if "pv_power" in df.columns:
        df["f_solar_norm"] = min_max_normalize(df["pv_power"])

    if "synergy_consumption" in df.columns:
        df["f_grid_import_norm"] = min_max_normalize(df["synergy_consumption"])

    if "synergy_production" in df.columns:
        df["f_grid_export_norm"] = min_max_normalize(df["synergy_production"])

    # B. Temporal Features: Cyclical Encoding
    # -----------------------------------------------------------
    # Use index hour
    hours = df.index.hour
    df["f_hour_sin"] = np.sin(2 * np.pi * hours / 24)
    df["f_hour_cos"] = np.cos(2 * np.pi * hours / 24)

    # C. Lagged Features: Thermal Inertia
    # -----------------------------------------------------------
    # We shift the NORMALIZED feature ('f_temp_indoor')
    if "f_temp_indoor" in df.columns:
        df["f_t_lag_1h"] = df["f_temp_indoor"].shift(1)
        df["f_t_lag_2h"] = df["f_temp_indoor"].shift(2)
        df["f_t_lag_3h"] = df["f_temp_indoor"].shift(3)

    # D. Virtual Sensors: Delta
    # -----------------------------------------------------------
    if "f_temp_indoor" in df.columns and "f_temp_outdoor" in df.columns:
        df["f_indoor_outdoor_delta"] = df["f_temp_indoor"] - df["f_temp_outdoor"]

    return df


def run_pipeline(files):
    # Load and process DynamoDB with all attributes
    df_rooms = process_dynamodb(pd.read_csv(files["dynamo"], low_memory=False))

    # Process other sources (using try/except in case files are missing during testing)
    others = []
    for key, func in [
        ("meteo", process_open_meteo),
        ("solar", process_solar_pv),
        ("powerpal", process_powerpal),
        ("synergy", process_synergy),
    ]:
        try:
            others.append(func(pd.read_csv(files[key])))
        except FileNotFoundError:
            continue

    # Final Alignment
    merged = pd.concat([df_rooms] + others, axis=1).sort_index()

    print("4. Generating ML features (f_ prefix)...")
    merged = add_ml_features(merged)

    # Final Formatting for Perth/Singapore alignment
    merged["datetime_perth"] = merged.index.strftime("%Y-%m-%d %H:00:00")
    merged["epoch"] = merged.index.astype("int64") // 10**9

    return merged


# Configuration
files = {
    "dynamo": "ddb_timeseries.csv",
    "meteo": "open_meteo.csv",
    "solar": "solorpv.csv",
    "powerpal": "powerpal.csv",
    "synergy": "synergy.csv",
}

if __name__ == "__main__":
    final_df = run_pipeline(files)

    final_df = final_df.loc["2025-01-01":"2025-12-08"]

    # 2. Export to CSV
    final_df.to_csv("datapipeline/2025_export.csv")

    # 3. Export to Parquet
    # Note: Requires pyarrow or fastparquet installed
    final_df.to_parquet("datapipeline/2025_export.parquet")

    print(f"Extraction complete for 2025. Rows exported: {len(final_df)}")
    print("New columns include:")
    # Print only living room and fridge columns to verify
    print([c for c in final_df.columns if "living_room" in c or "fridge" in c])
