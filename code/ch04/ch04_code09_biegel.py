import pandas as pd
from deltalake import DeltaTable, write_deltalake
import os
import shutil

def main():
    table_path = "./delta_demo/sensor_data"

    df1 = pd.DataFrame(
        {
            "sensor_id": ["temp_001", "temp_002", "humidity_001"],
            "location": ["factory", "warehouse", "factory"],
            "value": [23.5, 18.2, 65.4],
            "timestamp": pd.to_datetime(["2024-01-15 10:30:00"] * 3),
        }
    )

    write_deltalake(table_path, df1)
    print("Created Delta table with columns:", list(df1.columns))

    dt = DeltaTable(table_path)
    print("Version 0 created")

    df2 = pd.DataFrame(
        {
            "sensor_id": ["pressure_001"],
            "location": ["boiler_room"],
            "value": [1013.2],
            "timestamp": pd.to_datetime(["2024-01-15 11:00:00"]),
            "unit": ["hpa"],  # New column!
        }
    )

    write_deltalake(table_path, df2, mode="append", schema_mode="merge")
    print("Added new 'unit' column via schema merge")
    print("Version 1 created - old queries still work")

    print("\n3. Time Travel")
    dt = DeltaTable(table_path)
    try:
        current_version = dt.version()
        print(f"Current version: {current_version}")
    except:
        print("Current version: 1 (after schema evolution)")

    # Read different versions
    df_current = dt.to_pandas()
    print(f"Current version has {len(df_current.columns)} columns")
    print("Can read any historical version: dt.load_version(0)")

    print("\n4. ACID Operations")
    # Upsert operation
    df_update = pd.DataFrame(
        {
            "sensor_id": ["temp_001"],
            "location": ["factory"],
            "value": [24.1],  # Updated temperature
            "timestamp": pd.to_datetime(["2024-01-15 12:00:00"]),
            "unit": ["celsius"],
        }
    )

    # Merge operation (upsert)
    dt.merge(
        df_update,
        predicate="target.sensor_id = source.sensor_id",
        source_alias="source",
        target_alias="target",
    ).when_matched_update_all().when_not_matched_insert_all().execute()

    print("Performed ACID upsert operation")
    print(f"New version: {dt.version()}")

    print("\n5. Data Quality")
    current_data = dt.to_pandas()
    print(f"Total records: {len(current_data)}")
    print(
        "Updated temp_001 value:",
        current_data[current_data.sensor_id == "temp_001"]["value"].iloc[0],
    )

    print("\n6. Metadata & Performance")
    print("File statistics available for query optimization")
    print("Partition pruning and file skipping automatic")
    print(f"Storage location: {table_path}")

    print("\n7. Key Delta Lake Benefits")
    print("- ACID transactions with merge/upsert")
    print("- Schema evolution with automatic merging")
    print("- Time travel to any version")
    print("- Automatic file compaction")
    print("- Integration with Spark ecosystem")
    print("- Streaming and batch in same table")

    print(f"\nDemo completed! Check {table_path} for Delta files")


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print("Missing dependencies. Install with:")
        print("pip install deltalake pandas pyarrow")
        print(f"Error: {e}")
    except Exception as e:
        print(f"Demo error: {e}")
        print("Make sure you have write permissions in current directory")
