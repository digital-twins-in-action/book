#!/usr/bin/env python3
"""
Minimal self-contained Feast demo with temperature/humidity sensor features
No external files required - generates data in-memory
"""

import pandas as pd
from datetime import datetime, timedelta
from feast import FeatureStore, Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64
import tempfile
import os


def create_sensor_data():
    """Generate in-memory sensor data with engineered features"""

    # Generate raw sensor readings
    data = []
    base_time = datetime.now() - timedelta(hours=100)

    for hour in range(100):
        for sensor in ["sensor_001", "sensor_002", "sensor_003"]:
            timestamp = base_time + timedelta(hours=hour)
            temp = 0 + (hour % 12) + (0 if sensor == "sensor_001" else 2)
            humidity = 60 + (hour % 10)

            # Engineer features
            temp_deviation = abs(temp - 22)  # Deviation from optimal
            comfort_index = 1.0 if (20 <= temp <= 24 and 50 <= humidity <= 70) else 0.0
            heat_index = temp + (humidity * 0.1)  # Simple heat index

            data.append(
                {
                    "sensor_id": sensor,
                    "event_timestamp": timestamp,
                    "avg_temp_24h": temp,
                    "avg_humidity_24h": humidity,
                    "temp_deviation": temp_deviation,
                    "comfort_index": comfort_index,
                    "heat_index": heat_index,
                    "reading_count": 24,
                }
            )

    return pd.DataFrame(data)


def setup_feast(sensor_df):
    """Setup Feast with sensor features"""

    # Create temp directory
    repo_dir = tempfile.mkdtemp()
    os.chdir(repo_dir)

    # Save data as parquet
    sensor_df.to_parquet("sensor_features.parquet", index=False)

    # Feast config
    with open("feature_store.yaml", "w") as f:
        f.write(
            """
project: sensor_features
registry: registry.db
provider: local
online_store:
    type: sqlite
    path: online_store.db
"""
        )

    # Define entity and feature view
    sensor_entity = Entity(name="sensor_id", description="Sensor ID")

    sensor_features = FeatureView(
        name="sensor_stats",
        entities=[sensor_entity],
        ttl=timedelta(days=1),
        schema=[
            Field(name="avg_temp_24h", dtype=Float32),
            Field(name="avg_humidity_24h", dtype=Float32),
            Field(name="temp_deviation", dtype=Float32),
            Field(name="comfort_index", dtype=Float32),
            Field(name="heat_index", dtype=Float32),
            Field(name="reading_count", dtype=Int64),
        ],
        source=FileSource(
            path="sensor_features.parquet", timestamp_field="event_timestamp"
        ),
    )

    # Initialize Feast
    fs = FeatureStore(".")
    fs.apply([sensor_entity, sensor_features])

    return fs


def demo_feast():
    """Run complete Feast demo"""

    print("🌡️ Feast Sensor Features Demo")
    print("=" * 35)

    # Generate sensor data
    sensor_df = create_sensor_data()
    print(f"📊 Generated {len(sensor_df)} sensor feature records")

    # Setup Feast
    fs = setup_feast(sensor_df)
    print("✅ Feast configured")

    # Materialize features
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    fs.materialize(start_time, end_time)
    print("✅ Features materialized")

    # Get online features
    features = fs.get_online_features(
        features=[
            "sensor_stats:avg_temp_24h",
            "sensor_stats:comfort_index",
            "sensor_stats:heat_index",
        ],
        entity_rows=[{"sensor_id": "sensor_001"}, {"sensor_id": "sensor_002"}],
    )

    print("\n📦 Online Features Retrieved:")
    result_df = features.to_df()

    # Debug: Show actual column names
    print("Available columns:", list(result_df.columns))
    print(result_df.to_string(index=False))

    # ML prediction using features (handle different column name formats)
    print("\n🤖 HVAC Control Recommendations:")
    for _, row in result_df.iterrows():
        sensor_id = row["sensor_id"]

        # Try different possible column name formats
        temp_col = None
        comfort_col = None
        heat_col = None

        for col in result_df.columns:
            if "avg_temp_24h" in col:
                temp_col = col
            elif "comfort_index" in col:
                comfort_col = col
            elif "heat_index" in col:
                heat_col = col

        if temp_col and comfort_col and heat_col:
            temp = row[temp_col]
            comfort = row[comfort_col]
            heat_idx = row[heat_col]

            if comfort == 1.0:
                action = "✅ OPTIMAL - No action needed"
            elif temp > 24:
                action = "❄️ COOLING - Reduce temperature"
            elif temp < 20:
                action = "🔥 HEATING - Increase temperature"
            else:
                action = "💨 VENTILATION - Adjust humidity"

            print(f"  {sensor_id}: {action}")
            print(f"    (temp: {temp:.1f}°C, heat index: {heat_idx:.1f})")
        else:
            print(f"  {sensor_id}: Column mapping issue")


if __name__ == "__main__":
    demo_feast()

    print("\n✨ Feast Benefits for IoT:")
    print("  ✅ Real-time feature serving")
    print("  ✅ Engineered features (comfort index, heat index)")
    print("  ✅ ML model integration")
    print("  ✅ Consistent train/serve features")
