import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def full_order_model_simulation(power_setting, outdoor_temp):
    T_ambient = 20.0
    T_room = (
        T_ambient
        + 0.5 * power_setting
        - 0.1 * (outdoor_temp - T_ambient)
        + np.random.normal(0, 0.5)
    )
    return T_room


N_samples = 100
P_train = np.random.uniform(0, 10, N_samples)
T_out_train = np.random.uniform(10, 35, N_samples)

T_room_output = np.array(
    [full_order_model_simulation(p, t) for p, t in zip(P_train, T_out_train)]
)

X_train = np.column_stack((P_train, T_out_train))
y_train = T_room_output

rom_model = LinearRegression()
rom_model.fit(X_train, y_train)

T_fixed_plot = 25.0
P_plot = np.linspace(0, 10, 50)
X_plot = np.column_stack((P_plot, np.full_like(P_plot, T_fixed_plot)))
T_room_rom_plot = rom_model.predict(X_plot)

TOLERANCE = 1.5
near_fixed_t_indices = np.where(np.abs(T_out_train - T_fixed_plot) < TOLERANCE)
P_scatter = P_train[near_fixed_t_indices]
T_room_scatter = T_room_output[near_fixed_t_indices]

plt.figure(figsize=(12, 7))

plt.scatter(
    P_scatter,
    T_room_scatter,
    color="blue",
    s=80,
    label=f"FOM Data Points (Near $T_{{out}}={T_fixed_plot}°C$)",
    alpha=0.6,
    edgecolors="w",
    zorder=2,
)

plt.plot(
    P_plot,
    T_room_rom_plot,
    color="red",
    linestyle="-",
    linewidth=4,
    label=f"ROM Prediction Line ($T_{{out}}={T_fixed_plot}°C$)",
    zorder=3,
)

plt.xlabel("Heater Power Setting ($P$)", fontsize=20, fontweight="bold")
plt.ylabel("Room Temperature ($T_{room}$, °C)", fontsize=20, fontweight="bold")

plt.tick_params(axis="both", labelsize=16)
plt.legend(fontsize=14, framealpha=0.9, loc="upper left")
plt.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()
