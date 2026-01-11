import os
import json
import pandas as pd
import datetime

# --- CONFIGURATION ---
INPUT_DIR = "electricity_raw"
OUTPUT_FILE = "hourly_energy_stats.csv"


def process_energy_data():
    all_rows = []

    print(f"Reading files from {INPUT_DIR}...")
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]

    for filename in files:
        with open(os.path.join(INPUT_DIR, filename), "r") as f:
            try:
                data = json.load(f)
                base_date_str = data.get("startDate")
                consumption_vals = data.get("kwHalfHourlyValues", [])
                generation_vals = data.get("kwhHalfHourlyValuesGeneration", [])

                if not base_date_str or not consumption_vals:
                    continue

                base_date = pd.to_datetime(base_date_str)

                for i in range(len(consumption_vals)):
                    timestamp = base_date + datetime.timedelta(minutes=30 * i)

                    # Convert nulls to 0.0 and ensure float type
                    cons = (
                        consumption_vals[i] if consumption_vals[i] is not None else 0.0
                    )
                    gen = (
                        generation_vals[i]
                        if (i < len(generation_vals) and generation_vals[i] is not None)
                        else 0.0
                    )

                    all_rows.append(
                        {
                            "timestamp": timestamp,
                            "consumption_kw": float(cons),
                            "generation_kw": float(gen),
                        }
                    )

            except (json.JSONDecodeError, ValueError) as e:
                print(f"Skipping {filename} due to error: {e}")

    if not all_rows:
        print("No valid data found.")
        return

    df = pd.DataFrame(all_rows)
    df.set_index("timestamp", inplace=True)

    # --- THE FIX ---
    # We use .mean() to get the average kW over the hour.
    # Because Average kW * 1 Hour = Total kWh, this gives the correct energy volume.
    hourly_df = df.resample("H").mean()

    hourly_df.reset_index(inplace=True)

    # Rename for clarity in your Digital Twin's database
    hourly_df.rename(
        columns={
            "consumption_kw": "consumption_kWh",
            "generation_kw": "generation_kWh",
        },
        inplace=True,
    )

    hourly_df.to_csv(OUTPUT_FILE, index=False)
    print(f"--- SUCCESS ---")
    print(f"Final output now reflects kWh (hourly averages).")
    print(hourly_df.head())


if __name__ == "__main__":
    process_energy_data()
