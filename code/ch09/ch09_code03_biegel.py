import pandas as pd

# 1. Create simple dummy data representing 10 hours of temperature readings
# We use a clear rising trend so you can easily spot the shifts
data = {"indoor_temp": [20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5]}
df = pd.DataFrame(data)

# 2. Create lag features for the last 3 hours
# This allows the model to see the "trajectory" of the heat
df["indoor_temp_lag_1"] = df["indoor_temp"].shift(1)
df["indoor_temp_lag_2"] = df["indoor_temp"].shift(2)
df["indoor_temp_lag_3"] = df["indoor_temp"].shift(3)

# 3. Shifting creates NaN values for the first 3 rows, which we drop
df = df.dropna()

# 4. Display the result
# Notice how the 'current' temp in the first row is 21.5,
# and the lags show the history (21.0, 20.5, 20.0)
print(
    df[["indoor_temp", "indoor_temp_lag_1", "indoor_temp_lag_2", "indoor_temp_lag_3"]]
)
