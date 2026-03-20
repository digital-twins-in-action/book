import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor


def visualize_model_prediction():
    # 1. Load Data
    filename = "datapipeline/2025_export.parquet"
    df = pd.read_parquet(filename)

    df = df.reset_index().rename(columns={"index": "timestamp"})
    df["timestamp"] = pd.to_datetime(df["datetime_perth"])  # <--- Crucial Fix

    df["item_id"] = "Home_Digital_Twin"

    # 2. Re-create the "Future" Split
    # We must recreate the exact same split so we have the "Future Covariates" (Weather)
    # to feed into the model for prediction.
    prediction_length = 48

    # History (Train)
    train_df = (
        df.groupby("item_id")
        .apply(lambda x: x.iloc[:-prediction_length])
        .reset_index(drop=True)
    )

    # Future (Test/Ground Truth)
    future_df = (
        df.groupby("item_id")
        .apply(lambda x: x.iloc[-prediction_length:])
        .reset_index(drop=True)
    )

    # Extract only the weather columns for the model input
    future_covariates_df = future_df[
        [
            "item_id",
            "timestamp",
            "om_temperature",
            "om_humidity",
            "om_radiation",
            "om_cloud_cover",
        ]
    ]

    # Convert to AutoGluon format
    train_data = TimeSeriesDataFrame.from_data_frame(
        train_df, id_column="item_id", timestamp_column="timestamp"
    )
    future_covariates = TimeSeriesDataFrame.from_data_frame(
        future_covariates_df, id_column="item_id", timestamp_column="timestamp"
    )

    # 3. Load the Existing Model
    # We do NOT use fit(). We load the saved predictor.
    model_path = "models/prediction/electricity_consumption_model"
    print(f"Loading trained model from {model_path}...")
    predictor = TimeSeriesPredictor.load(model_path)

    # 4. Generate Forecast
    print("Generating forecast...")
    predictions = predictor.predict(train_data, known_covariates=future_covariates)

    # 5. Create Custom Visualization
    print("Plotting...")

    # We will plot the last 24 hours of history + the 48 hours of prediction
    history_window = 24
    history_subset = train_df.iloc[-history_window:]

    # Extract forecast for the specific item (assuming single item 'Home_Digital_Twin')
    item_id = "Home_Digital_Twin"
    pred_item = predictions.loc[item_id]

    plt.figure(figsize=(15, 7))

    # A. Plot History (Context)
    plt.plot(
        history_subset["timestamp"],
        history_subset["synergy_net"],
        label="Past 24h History",
        color="gray",
        linestyle="--",
        alpha=0.7,
    )

    # B. Plot Actual Future (Ground Truth)
    plt.plot(
        future_df["timestamp"],
        future_df["synergy_net"],
        label="Actual net electricity (ground truth)",
        color="black",
        linewidth=2,
    )

    # C. Plot Forecast (Mean)
    plt.plot(
        pred_item.index,
        pred_item["mean"],
        label="AI forecast (mean)",
        color="blue",
        linewidth=2,
    )

    # D. Plot Uncertainty Intervals (e.g., 10%-90%)
    plt.fill_between(
        pred_item.index,
        pred_item["0.1"],
        pred_item["0.9"],
        color="blue",
        alpha=0.15,
        label="80% Confidence Interval",
    )

    # Formatting the X-Axis for "Hours"
    plt.gca().xaxis.set_major_locator(
        mdates.HourLocator(interval=4)
    )  # Tick every 4 hours
    plt.gca().xaxis.set_major_formatter(
        mdates.DateFormatter("%H:%M\n%a")
    )  # Format: 14:00 Mon

    plt.title("742 Evergreen Terrace electricity forecast")
    plt.ylabel("Net electricity (kWh)")
    plt.xlabel("Time (Hour & Day)")
    plt.axhline(0, color="k", linewidth=0.5)  # Zero line for reference
    plt.grid(True, alpha=0.3)
    plt.legend(loc="upper left")
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    visualize_model_prediction()
