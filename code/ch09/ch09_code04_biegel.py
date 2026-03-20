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
    """State transition function for the UKF"""
    model = TemperatureFMU()
    return np.array([model.step(x[0], dt, u_hvac, u_ext)])


def hx(x):
    """Measurement function"""
    return np.array([x[0]])


def main():
    # --- Configuration ---
    dt = 600  # 10 minutes
    steps = 144  # 24 hours
    n_sensors = 5

    # --- Initialize UKF ---
    points = MerweScaledSigmaPoints(n=1, alpha=0.1, beta=2.0, kappa=1.0)

    kf = UKF(dim_x=1, dim_z=1, dt=dt, fx=fx, hx=hx, points=points)
    kf.x = np.array([22.0])  # Initial estimate
    kf.P *= 1.0  # Initial uncertainty

    # MATCHING ORIGINAL MATH:
    # Original used measurement_noise=0.25 (variance) per sensor.
    # It averaged 5 sensors. Variance of mean = Var / N = 0.25 / 5 = 0.05
    kf.R = 0.05

    # Original used process_noise=0.1 (variance)
    kf.Q = 0.1

    # --- Simulation Setup ---
    # To ensure the curve looks like a day cycle, we mock a start time
    # start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = datetime.now()

    true_model = TemperatureFMU(t_initial=22.0)
    sensor_biases = np.linspace(-1.0, 1.0, n_sensors)

    # Storage
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
        hour = current_time.hour + current_time.minute / 60
        times.append(current_time)

        # 1. Environment
        ext_temp = 18 + 8 * np.sin(2 * np.pi * (hour - 6) / 24)

        if 6 <= hour <= 22:
            hvac_setpoint = 22.0
        else:
            hvac_setpoint = 20.0

        # 2. True System Evolution
        # Calculate physics step
        true_temp = true_model.step(true_model.temp, dt, hvac_setpoint, ext_temp)
        # Add random process noise (crucial for the "wiggle" in the green line)
        true_temp += np.random.normal(0, 0.1)
        true_model.temp = true_temp

        # 3. Generate Sensor Measurements
        current_readings = []
        for bias in sensor_biases:
            # True + Bias + Random Noise (std=0.5)
            reading = true_temp + bias + np.random.normal(0, 0.5)
            current_readings.append(reading)

        # We feed the AVERAGE to the UKF
        avg_measurement = np.mean(current_readings)

        # 4. UKF Predict & Update
        kf.predict(dt=dt, u_hvac=hvac_setpoint, u_ext=ext_temp)
        kf.update(avg_measurement)

        # 5. Store Data
        results["true"].append(true_temp)
        results["estimate"].append(kf.x[0])
        results["uncertainty"].append(np.sqrt(kf.P[0, 0]))
        results["measurements"].append(current_readings)  # Store all raw readings
        results["hvac"].append(hvac_setpoint)
        results["external"].append(ext_temp)

    # --- Plotting ---
    # Convert to numpy arrays for plotting
    time_hours = [(t - times[0]).total_seconds() / 3600 for t in times]
    true_temps = np.array(results["true"])
    estimated_temps = np.array(results["estimate"])
    uncertainties = np.array(results["uncertainty"])
    measurements_array = np.array(results["measurements"])  # Shape: (steps, n_sensors)
    hvac_setpoints = np.array(results["hvac"])
    external_temps = np.array(results["external"])

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # Plot 1: Temperature tracking
    axes[0].plot(time_hours, true_temps, "g-", label="True Temperature", linewidth=2)
    axes[0].plot(time_hours, estimated_temps, "b-", label="UKF Estimate", linewidth=2)

    # Uncertainty bounds
    axes[0].fill_between(
        time_hours,
        estimated_temps - 2 * uncertainties,
        estimated_temps + 2 * uncertainties,
        alpha=0.3,
        color="blue",
        label="±2σ Uncertainty",
    )

    # Sample sensor readings (Plotting only 1 sensor for clarity, same as original)
    axes[0].plot(
        time_hours,
        measurements_array[:, 0],
        "r.",
        alpha=0.5,
        markersize=3,
        label="IoT Sensor Sample",
    )

    # HVAC setpoint
    axes[0].plot(time_hours, hvac_setpoints, "k--", alpha=0.7, label="HVAC Setpoint")

    axes[0].set_ylabel("Temperature (°C)")
    axes[0].set_title("IoT Temperature Monitoring with FMU-UKF")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Plot 2: Performance analysis
    errors = true_temps - estimated_temps
    axes[1].plot(time_hours, errors, "purple", label="Estimation Error")
    axes[1].plot(
        time_hours, external_temps, "orange", alpha=0.7, label="External Temperature"
    )
    axes[1].axhline(y=0, color="black", linestyle="-", alpha=0.3)

    axes[1].set_xlabel("Time (hours)")
    axes[1].set_ylabel("Temperature (°C)")
    axes[1].set_title("Estimation Error and External Conditions")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("iot_temperature.png", dpi=150, bbox_inches="tight")
    plt.show()

    # Metrics
    rmse = np.sqrt(np.mean(errors**2))
    print(f"RMSE: {rmse:.3f}°C")


if __name__ == "__main__":
    main()
