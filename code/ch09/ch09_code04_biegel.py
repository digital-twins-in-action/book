import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from filterpy.kalman import UnscentedKalmanFilter as UKF
from filterpy.kalman import MerweScaledSigmaPoints


# 1. The Physics Model
class TemperatureFMU:
    def __init__(self, t_initial=20.0):
        self.temp = t_initial
        self.time_constant = 1800  # Thermal inertia (seconds)

    def step(self, x, dt, u_hvac, u_ext):
        rate = ((0.8 * (u_hvac - x)) + (0.1 * (u_ext - x))) / self.time_constant
        return x + (rate * dt)


# 2. Wrapper for FilterPy
def fx(x, dt, u_hvac, u_ext):
    model = TemperatureFMU()
    return np.array([model.step(x[0], dt, u_hvac, u_ext)])


def hx(x):
    return np.array([x[0]])


def main():
    # --- Configuration ---
    dt = 600  # 10 minutes
    steps = 144  # 24 hours
    n_sensors = 5

    # --- Initialize UKF ---
    points = MerweScaledSigmaPoints(n=1, alpha=0.1, beta=2.0, kappa=1.0)
    kf = UKF(dim_x=1, dim_z=1, dt=dt, fx=fx, hx=hx, points=points)
    kf.x = np.array([22.0])
    kf.P *= 1.0
    kf.R = 0.05
    kf.Q = 0.1

    # --- Simulation Setup ---
    # Start at 9:00 PM (21:00)
    start_time = datetime.now().replace(hour=21, minute=0, second=0, microsecond=0)

    true_model = TemperatureFMU(t_initial=22.0)
    sensor_biases = np.linspace(-1.0, 1.0, n_sensors)

    times = []
    results = {
        "true": [],
        "estimate": [],
        "uncertainty": [],
        "measurements": [],
        "hvac": [],
        "external": [],
    }

    # --- Main Loop ---
    for step in range(steps):
        current_time = start_time + timedelta(minutes=10 * step)
        hour = (current_time.hour + current_time.minute / 60) % 24
        times.append(current_time)

        # 1. Environment
        ext_temp = 18 + 8 * np.sin(2 * np.pi * (hour - 6) / 24)
        hvac_setpoint = 22.0 if 6 <= hour <= 22 else 20.0

        # 2. True System Evolution
        true_temp = true_model.step(true_model.temp, dt, hvac_setpoint, ext_temp)
        true_temp += np.random.normal(0, 0.1)
        true_model.temp = true_temp

        # 3. Generate Sensor Measurements
        current_readings = [
            true_temp + b + np.random.normal(0, 0.5) for b in sensor_biases
        ]
        avg_measurement = np.mean(current_readings)

        # 4. UKF Predict & Update
        kf.predict(dt=dt, u_hvac=hvac_setpoint, u_ext=ext_temp)
        kf.update(avg_measurement)

        # 5. Store Data
        results["true"].append(true_temp)
        results["estimate"].append(kf.x[0])
        results["uncertainty"].append(np.sqrt(kf.P[0, 0]))
        results["measurements"].append(current_readings)
        results["hvac"].append(hvac_setpoint)
        results["external"].append(ext_temp)

    # --- Plotting ---
    time_hours = [(t - times[0]).total_seconds() / 3600 for t in times]
    true_temps = np.array(results["true"])
    estimated_temps = np.array(results["estimate"])
    uncertainties = np.array(results["uncertainty"])
    measurements_array = np.array(results["measurements"])
    hvac_setpoints = np.array(results["hvac"])
    external_temps = np.array(results["external"])

    fig, axes = plt.subplots(2, 1, figsize=(14, 12))

    # Plot 1: Temperature tracking
    axes[0].plot(time_hours, true_temps, "g-", label="True Temperature", linewidth=3)
    axes[0].plot(time_hours, estimated_temps, "b-", label="UKF Estimate", linewidth=3)
    axes[0].fill_between(
        time_hours,
        estimated_temps - 2 * uncertainties,
        estimated_temps + 2 * uncertainties,
        alpha=0.2,
        color="blue",
        label="±2σ Uncertainty",
    )
    axes[0].plot(
        time_hours,
        measurements_array[:, 0],
        "r.",
        alpha=0.4,
        markersize=6,
        label="IoT Sensor Sample",
    )
    axes[0].plot(
        time_hours, hvac_setpoints, "k--", alpha=0.7, linewidth=2, label="HVAC Setpoint"
    )

    axes[0].set_ylabel("Temperature (°C)", fontsize=20, fontweight="bold")
    axes[0].tick_params(axis="both", labelsize=16)

    # FIXED: Moved legend to bottom right
    axes[0].legend(fontsize=14, loc="lower right", framealpha=0.9)
    axes[0].grid(True, alpha=0.3)

    # Plot 2: Performance analysis
    errors = true_temps - estimated_temps
    axes[1].plot(time_hours, errors, "purple", linewidth=2.5, label="Estimation Error")
    axes[1].plot(
        time_hours,
        external_temps,
        "orange",
        alpha=0.6,
        linewidth=2.5,
        label="External Temperature",
    )
    axes[1].axhline(y=0, color="black", linestyle="-", alpha=0.3)

    axes[1].set_xlabel("Time (hours since 8pm)", fontsize=20, fontweight="bold")
    axes[1].set_ylabel("Temperature (°C)", fontsize=20, fontweight="bold")
    axes[1].tick_params(axis="both", labelsize=16)
    axes[1].legend(fontsize=14, loc="upper right")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout(pad=3.0)
    plt.savefig("iot_temperature_9pm_legend_br.png", dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
