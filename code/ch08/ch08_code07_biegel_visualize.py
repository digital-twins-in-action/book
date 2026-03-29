import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor


def visualize_model_prediction():
    filename = "datapipeline/2025_export.parquet"
    df = pd.read_parquet(filename)

    df = df.reset_index().rename(columns={"index": "timestamp"})
    df["timestamp"] = pd.to_datetime(df["datetime_perth"])

    df["item_id"] = "Home_Digital_Twin"

    prediction_length = 48

    train_df = (
        df.groupby("item_id")
        .apply(lambda x: x.iloc[:-prediction_length])
        .reset_index(drop=True)
    )

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

    train_data = TimeSeriesDataFrame.from_data_frame(
        train_df, id_column="item_id", timestamp_column="timestamp"
    )
    future_covariates = TimeSeriesDataFrame.from_data_frame(
        future_covariates_df, id_column="item_id", timestamp_column="timestamp"
    )

    model_path = "models/prediction/electricity_consumption_model"
    print(f"Loading trained model from {model_path}...")
    predictor = TimeSeriesPredictor.load(model_path)

    predictions = predictor.predict(train_data, known_covariates=future_covariates)

    history_window = 24
    history_subset = train_df.iloc[-history_window:]

    item_id = "Home_Digital_Twin"
    pred_item = predictions.loc[item_id]

    plt.figure(figsize=(16, 8))

    # A. Plot History (Context)
    plt.plot(
        history_subset["timestamp"],
        history_subset["synergy_net"],
        label="Past 24h History",
        color="gray",
        linestyle="--",
        alpha=0.7,
        linewidth=2.5,  # *** INCREASED LINEWIDTH ***
    )

    # B. Plot Actual Future (Ground Truth)
    plt.plot(
        future_df["timestamp"],
        future_df["synergy_net"],
        label="Actual net electricity (ground truth)",
        color="black",
        linewidth=3,  # *** INCREASED LINEWIDTH ***
    )

    # C. Plot Forecast (Mean)
    plt.plot(
        pred_item.index,
        pred_item["mean"],
        label="AI forecast (mean)",
        color="blue",
        linewidth=3,  # *** INCREASED LINEWIDTH ***
    )

    # D. Plot Uncertainty Intervals
    plt.fill_between(
        pred_item.index,
        pred_item["0.1"],
        pred_item["0.9"],
        color="blue",
        alpha=0.15,
        label="80% Confidence Interval",
    )

    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%a"))

    plt.ylabel("Net electricity (kWh)", fontsize=20, fontweight="bold")
    plt.xlabel("Time (Hour & Day)", fontsize=20, fontweight="bold")

    plt.tick_params(axis="both", labelsize=16)

    plt.axhline(0, color="k", linewidth=1.5)
    plt.grid(True, alpha=0.3)

    plt.legend(loc="upper left", fontsize=16, framealpha=0.9)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    visualize_model_prediction()
