import os
import json
import pandas as pd

# 1. Setup: Change this to the path of your directory
folder_path = "ddb_dump/sensor-data/data"

all_records = []


# 2. Helper function to "flatten" DynamoDB JSON
def extract_value(dynamo_item):
    """
    Converts {'humidity': {'N': '0.4'}} -> {'humidity': 0.4}
    """
    parsed_item = {}
    for key, value_dict in dynamo_item.items():
        # check if it's a Number
        if "N" in value_dict:
            parsed_item[key] = float(value_dict["N"])
        # check if it's a String
        elif "S" in value_dict:
            parsed_item[key] = value_dict["S"]
        # Add boolean or other types if needed, but your data seems to be N/S
    return parsed_item


# 3. Loop through every file in the folder
print(f"Scanning {folder_path}...")

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r") as f:
            data = json.load(f)

            # The key in your new format is 'Items', not 'data'
            if "Items" in data:
                for item in data["Items"]:
                    # Extract values and add to our master list
                    flat_record = extract_value(item)
                    all_records.append(flat_record)

# 4. Convert to DataFrame
df = pd.DataFrame(all_records)

if not df.empty:
    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["sortKey"], unit="ms")

    # Optional: Sort by time
    df = df.sort_values("timestamp")

    # Save to CSV
    output_file = "merged_dynamodb_data.csv"
    df.to_csv(output_file, index=False)
    print(f"Success! Processed {len(df)} records into {output_file}")
    print(df.head())
else:
    print("No data found. Check your folder path and file structure.")
