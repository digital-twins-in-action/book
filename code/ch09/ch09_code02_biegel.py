import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Create a dummy dataframe with 24 hours
df = pd.DataFrame({"hour": range(24)})

# 2. Apply the Cyclical Encoding (Sine and Cosine)
# We divide by 24 because that is the period of the cycle
df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

# 3. Print the first few rows to see the values
print(df.head())

# 4. Visualize it: Plot Sine vs Cosine
plt.figure(figsize=(6, 6))
plt.scatter(df["hour_sin"], df["hour_cos"], c=df.index, cmap="twilight")

# Label a few key hours to show the "Clock" effect
for i, txt in enumerate(df["hour"]):
    if i % 3 == 0:  # Label every 3rd hour
        plt.annotate(txt, (df["hour_sin"][i], df["hour_cos"][i]), fontsize=12)

plt.title("Cyclical encoding of time")
plt.xlabel("Sine component")
plt.ylabel("Cosine component")
plt.grid(True)
plt.axhline(0, color="black", linewidth=0.5)
plt.axvline(0, color="black", linewidth=0.5)
plt.show()
