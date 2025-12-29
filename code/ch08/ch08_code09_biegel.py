import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 1. Full-Order Model (FOM) Simulation Proxy
# ==========================================


def full_order_model_simulation(power_setting, outdoor_temp):
    """
    Represents a complex, time-consuming simulation of room temperature (T_room)
    based on Heater Power (P) and Outdoor Temperature (T_out).
    """
    T_ambient = 20.0  # Base ambient temperature (°C)
    # Simple, non-linear relationship (simulating complex thermal dynamics)
    T_room = (
        T_ambient
        + 0.5 * power_setting
        - 0.1 * (outdoor_temp - T_ambient)
        + np.random.normal(0, 0.5)
    )
    return T_room


# 2. Offline Phase: Training Data Generation
# ==========================================

N_samples = 100
# Generate random data points for inputs
P_train = np.random.uniform(0, 10, N_samples)  # Heater Power (0 to 10)
T_out_train = np.random.uniform(10, 35, N_samples)  # Outdoor Temp (10°C to 35°C)

# Compute the output (costly step in real simulation)
T_room_output = np.array(
    [full_order_model_simulation(p, t) for p, t in zip(P_train, T_out_train)]
)

X_train = np.column_stack((P_train, T_out_train))  # Features: [P, T_out]
y_train = T_room_output  # Target: [T_room]

# 3. ROM Creation and Training
# ============================

# Create the Reduced Order Model (Linear Regression)
rom_model = LinearRegression()

# Train the ROM on the FOM data
rom_model.fit(X_train, y_train)

print("--- ROM Training Results ---")
print(f"ROM Coefficients (P, T_out): {rom_model.coef_}")
print(f"ROM Intercept: {rom_model.intercept_:.2f}")

# 4. Online Phase: Fast Prediction Example
# ========================================

P_new = 8.0  # New Heater power
T_out_new = 28.0  # New outdoor temperature

X_new = np.array([[P_new, T_out_new]])

# Fast prediction using the ROM (milliseconds)
T_room_rom = rom_model.predict(X_new)[0]

# Comparison with the slow FOM (for validation, not online use)
T_room_fom = full_order_model_simulation(P_new, T_out_new)

print("\n--- Prediction Comparison ---")
print(f"ROM Predicted Room Temp: {T_room_rom:.2f} °C")
print(f"FOM Actual Room Temp: {T_room_fom:.2f} °C (with noise)")

# 5. Plotting the ROM Performance (2D Slice)
# ==========================================

# To visualize the 3D fit in 2D, we fix the Outdoor Temperature (T_out)
T_fixed_plot = 25.0
P_plot = np.linspace(0, 10, 50)  # Range of Heater Power for plotting

# Create a new feature array for the plot line: [[P1, T_fixed], [P2, T_fixed], ...]
X_plot = np.column_stack((P_plot, np.full_like(P_plot, T_fixed_plot)))
T_room_rom_plot = rom_model.predict(X_plot)

# Get the corresponding *actual* FOM data points near the fixed T_out
# We use a small tolerance to select nearby points for the scatter plot
TOLERANCE = 1.5
near_fixed_t_indices = np.where(np.abs(T_out_train - T_fixed_plot) < TOLERANCE)
P_scatter = P_train[near_fixed_t_indices]
T_room_scatter = T_room_output[near_fixed_t_indices]

plt.figure(figsize=(10, 6))
# Plot the scattered, noisy FOM data points (the data used for training)
plt.scatter(
    P_scatter,
    T_room_scatter,
    color="blue",
    label="FOM Data Points (Near $T_{out}=25°C$)",
    alpha=0.6,
    edgecolors="w",
)
# Plot the ROM prediction line for the fixed T_out
plt.plot(
    P_plot,
    T_room_rom_plot,
    color="red",
    linestyle="-",
    linewidth=2,
    label=f"ROM Prediction Line ($T_{{out}}={T_fixed_plot}°C$)",
)

plt.title("Reduced Order Model (ROM) Fit: Room Temperature vs. Heater Power")
plt.xlabel("Heater Power Setting ($P$)")
plt.ylabel("Room Temperature ($T_{room}$, °C)")
plt.grid(True, linestyle="--", alpha=0.7)
plt.legend()
plt.show()
