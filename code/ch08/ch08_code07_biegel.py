import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

df = pd.read_parquet("datapipeline/2025_export.parquet")

df = df.reset_index().rename(columns={"index": "timestamp"})
df["timestamp"] = pd.to_datetime(df["datetime_perth"])
df["item_id"] = "Home_Digital_Twin"

prediction_length = 48

train_df = (
    df.groupby("item_id")
    .apply(lambda x: x.iloc[:-prediction_length])
    .reset_index(drop=True)
)

train_data = TimeSeriesDataFrame.from_data_frame(
    train_df, id_column="item_id", timestamp_column="timestamp"
)

predictor = TimeSeriesPredictor(
    prediction_length=prediction_length,
    target="synergy_net",
    path="models/prediction/electricity_consumption_model",
    known_covariates_names=[
        "om_temperature",
        "om_humidity",
        "om_radiation",
        "om_cloud_cover",
    ],
    eval_metric="MASE",
)

predictor.fit(train_data, presets="medium_quality", time_limit=600)
