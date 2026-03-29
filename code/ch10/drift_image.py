import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

reference_data = [1.8, 2.0, 1.9, 2.1, 2.0, 1.95, 2.05]
current_data = [2.4, 2.5, 2.6, 2.3, 2.7, 2.5, 2.6]

df = pd.DataFrame(
    {
        "Power Output (kW)": reference_data + current_data,
        "Dataset": ["Reference (training)"] * len(reference_data)
        + ["Current (production)"] * len(current_data),
    }
)

sns.set_style("whitegrid")
plt.figure(figsize=(10, 6))

sns.kdeplot(
    data=df,
    x="Power Output (kW)",
    hue="Dataset",
    fill=True,
    common_norm=False,
    palette=["#1f77b4", "#ff7f0e"],
    alpha=0.3,
    linewidth=2,
)

plt.title("Solar power output data drift", fontsize=24, fontweight="bold", pad=20)
plt.xlabel("Solar power output (kW)", fontsize=20, fontweight="bold")
plt.ylabel("Density (frequency)", fontsize=20, fontweight="bold")
plt.xlim(1.5, 3.0)  # Focus on the relevant area

plt.tick_params(axis="both", labelsize=16)

legend = plt.gca().get_legend()
if legend:
    plt.setp(legend.get_texts(), fontsize="16")
    plt.setp(legend.get_title(), fontsize="16", fontweight="bold")


plt.tight_layout()
plt.show()
