import pandas as pd
import numpy as np


def process_solar_data(input_file, output_file):
    # 1. Read the CSV data
    # We skip the first row (SerialNr) and use ';' as the separator
    df = pd.read_csv(input_file, sep=";", skiprows=1)

    # 2. Function to clean the scientific notation (e.g. "1800e0" -> 1800.0)
    def parse_value(val):
        if isinstance(val, str):
            try:
                return float(val)
            except ValueError:
                return np.nan  # Return NaN if it's text (like log messages)
        return val

    # List of columns that contain measurement data to clean
    # (Excluding Date, Time, IDs, and Description)
    data_columns = [
        "Periode [s]",
        "Energy [Ws]",
        "Reactive Energy L[Vars]",
        "Reactive Energy C[Vars]",
        "Uac L1 [V]",
        "Uac L2 [V]",
        "Uac L3 [V]",
        "Iac L1 [A]",
        "Iac L2 [A]",
        "Iac L3 [A]",
        "Udc MPPT1[V]",
        "Idc MPPT1[A]",
        "Udc MPPT2[V]",
        "Idc MPPT2[A]",
    ]

    # Apply the cleaning function to these columns
    for col in data_columns:
        if col in df.columns:
            df[col] = df[col].apply(parse_value)

    # 3. Create Timestamp Columns
    # Combine Date and Time into a proper datetime object
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])

    # Create Epoch Timestamp (seconds since Jan 1, 1970)
    df["Epoch"] = df["Datetime"].astype("int64") // 10**9

    # 4. Filter and Calculate
    # Remove rows that don't have energy data (system logs)
    df_clean = df[df["Energy [Ws]"].notna()].copy()

    # Calculate Energy in kWh (1 kWh = 3,600,000 Joules/Ws)
    df_clean["Energy [kWh]"] = df_clean["Energy [Ws]"] / 3_600_000

    # Calculate Average Power in Watts (Energy / Time Period)
    df_clean["Power [W]"] = df_clean["Energy [Ws]"] / df_clean["Periode [s]"]

    # 5. Select and Reorder Final Columns
    # You can adjust this list to keep/remove columns as needed
    final_columns = [
        "Datetime",
        "Epoch",
        "Energy [kWh]",
        "Power [W]",
        "Uac L1 [V]",
        "Iac L1 [A]",
        "Udc MPPT1[V]",
        "Idc MPPT1[A]",
        "Periode [s]",
        "Energy [Ws]",
    ]

    # Select only the columns that exist in our data
    final_columns = [c for c in final_columns if c in df_clean.columns]
    final_df = df_clean[final_columns]

    # Sort by time
    final_df = final_df.sort_values("Datetime")

    # 6. Save to CSV
    # index=False ensures we don't save the row numbers
    final_df.to_csv(output_file, index=False)
    print(f"Successfully saved processed data to {output_file}")
    return final_df


# --- Usage ---
# Replace 'DATA.CSV' with your actual filename if different
df = process_solar_data("DATA.CSV", "solar_data_clean.csv")
