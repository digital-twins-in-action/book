"""
Air Conditioner Cooling Simulation using JAX-CFD

This example simulates airflow and temperature distribution in a room
with an air conditioner unit. It demonstrates:
- 2D incompressible Navier-Stokes equations
- Passive scalar transport for temperature
- Boundary conditions for AC inlet/outlet
- Real-time visualization of cooling effect

"""

import jax
import jax.numpy as jnp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize
from functools import partial

# Enable 64-bit precision for better numerical stability
jax.config.update("jax_enable_x64", True)


# =============================================================================
# Simulation Parameters
# =============================================================================

# Room dimensions (meters) - scaled to grid
ROOM_WIDTH = 5.0  # 5 meters wide
ROOM_HEIGHT = 3.0  # 3 meters tall

# Grid resolution
NX = 100  # grid points in x
NY = 60  # grid points in y

# Physical parameters
DX = ROOM_WIDTH / NX
DY = ROOM_HEIGHT / NY
DT = 0.005  # time step (seconds)

# Fluid properties (air at room temperature)
NU = 1.5e-5 * 1000  # kinematic viscosity (scaled for visualization)
ALPHA = 2.2e-5 * 1000  # thermal diffusivity (scaled)

# Temperature settings (Celsius)
T_INITIAL = 30.0  # Initial room temperature (hot day)
T_AC_OUTLET = 16.0  # AC outlet temperature (cold air)

# AC unit position and size (grid indices)
AC_X_START = 5
AC_X_END = 15
AC_Y_POS = NY - 2  # Near ceiling

# AC outlet velocity (m/s)
AC_VELOCITY = -0.5  # Downward flow


# =============================================================================
# Core CFD Functions
# =============================================================================


def create_initial_conditions():
    """Initialize velocity and temperature fields."""
    # Velocity components (u, v) - start at rest
    u = jnp.zeros((NY, NX))
    v = jnp.zeros((NY, NX))

    # Pressure field
    p = jnp.zeros((NY, NX))

    # Temperature field - uniform initial temperature
    T = jnp.ones((NY, NX)) * T_INITIAL

    return u, v, p, T


def apply_boundary_conditions(u, v, T):
    """Apply boundary conditions for walls and AC unit."""
    # Wall boundaries (no-slip for velocity)
    # Bottom wall
    u = u.at[0, :].set(0.0)
    v = v.at[0, :].set(0.0)

    # Top wall
    u = u.at[-1, :].set(0.0)
    v = v.at[-1, :].set(0.0)

    # Left wall
    u = u.at[:, 0].set(0.0)
    v = v.at[:, 0].set(0.0)

    # Right wall
    u = u.at[:, -1].set(0.0)
    v = v.at[:, -1].set(0.0)

    # AC unit boundary conditions (inlet)
    # Cold air blowing downward from AC
    u = u.at[AC_Y_POS, AC_X_START:AC_X_END].set(0.0)
    v = v.at[AC_Y_POS, AC_X_START:AC_X_END].set(AC_VELOCITY)
    T = T.at[AC_Y_POS, AC_X_START:AC_X_END].set(T_AC_OUTLET)

    # Adiabatic walls (no heat flux through walls)
    T = T.at[0, :].set(T[1, :])  # Bottom
    T = T.at[-1, :].set(T[-2, :])  # Top (except AC)
    T = T.at[:, 0].set(T[:, 1])  # Left
    T = T.at[:, -1].set(T[:, -2])  # Right

    # Re-apply AC temperature after adiabatic condition
    T = T.at[AC_Y_POS, AC_X_START:AC_X_END].set(T_AC_OUTLET)

    return u, v, T


def compute_divergence(u, v):
    """Compute velocity divergence."""
    dudx = (jnp.roll(u, -1, axis=1) - jnp.roll(u, 1, axis=1)) / (2 * DX)
    dvdy = (jnp.roll(v, -1, axis=0) - jnp.roll(v, 1, axis=0)) / (2 * DY)
    return dudx + dvdy


def laplacian(field, dx, dy):
    """Compute Laplacian using central differences."""
    d2fdx2 = (jnp.roll(field, -1, axis=1) - 2 * field + jnp.roll(field, 1, axis=1)) / (
        dx**2
    )
    d2fdy2 = (jnp.roll(field, -1, axis=0) - 2 * field + jnp.roll(field, 1, axis=0)) / (
        dy**2
    )
    return d2fdx2 + d2fdy2


def pressure_poisson(p, div_velocity, n_iterations=50):
    """Solve pressure Poisson equation using Jacobi iteration."""
    rhs = div_velocity / DT

    def jacobi_step(p, _):
        p_new = (
            (jnp.roll(p, 1, axis=1) + jnp.roll(p, -1, axis=1)) / DX**2
            + (jnp.roll(p, 1, axis=0) + jnp.roll(p, -1, axis=0)) / DY**2
            - rhs
        ) / (2 / DX**2 + 2 / DY**2)

        # Neumann boundary conditions for pressure
        p_new = p_new.at[0, :].set(p_new[1, :])
        p_new = p_new.at[-1, :].set(p_new[-2, :])
        p_new = p_new.at[:, 0].set(p_new[:, 1])
        p_new = p_new.at[:, -1].set(p_new[:, -2])

        return p_new, None

    p, _ = jax.lax.scan(jacobi_step, p, None, length=n_iterations)
    return p


def advection_term(field, u, v):
    """Compute advection using upwind scheme."""
    # Upwind differences based on velocity direction
    dfdx_pos = (field - jnp.roll(field, 1, axis=1)) / DX
    dfdx_neg = (jnp.roll(field, -1, axis=1) - field) / DX
    dfdy_pos = (field - jnp.roll(field, 1, axis=0)) / DY
    dfdy_neg = (jnp.roll(field, -1, axis=0) - field) / DY

    # Upwind selection
    dfdx = jnp.where(u > 0, dfdx_pos, dfdx_neg)
    dfdy = jnp.where(v > 0, dfdy_pos, dfdy_neg)

    return u * dfdx + v * dfdy


@jax.jit
def simulation_step(state):
    """One timestep using projection method with thermal coupling."""
    u, v, p, T = state
    u, v, T = apply_boundary_conditions(u, v, T)

    # Predictor: advection + diffusion (no pressure)
    u_star = u + DT * (-advection_term(u, u, v) + NU * laplacian(u, DX, DY))
    v_star = v + DT * (-advection_term(v, u, v) + NU * laplacian(v, DX, DY))

    # Pressure correction: enforce incompressibility
    p = pressure_poisson(p, compute_divergence(u_star, v_star))
    dpdx = (jnp.roll(p, -1, axis=1) - jnp.roll(p, 1, axis=1)) / (2 * DX)
    dpdy = (jnp.roll(p, -1, axis=0) - jnp.roll(p, 1, axis=0)) / (2 * DY)

    # Corrector: project to divergence-free field
    u_new = u_star - DT * dpdx
    v_new = v_star - DT * dpdy

    # Temperature: passive scalar advection-diffusion
    T_new = T + DT * (-advection_term(T, u, v) + ALPHA * laplacian(T, DX, DY))

    # Final boundary conditions
    u_new, v_new, T_new = apply_boundary_conditions(u_new, v_new, T_new)

    return (u_new, v_new, p, T_new)


# =============================================================================
# Visualization
# =============================================================================


def create_visualization():
    """Create animated visualization of the cooling simulation."""
    print("Initializing simulation...")

    # Initialize fields
    state = create_initial_conditions()

    # Create figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "Air Conditioner Room Cooling Simulation", fontsize=14, fontweight="bold"
    )

    # Create coordinate grids for plotting
    x = np.linspace(0, ROOM_WIDTH, NX)
    y = np.linspace(0, ROOM_HEIGHT, NY)
    X, Y = np.meshgrid(x, y)

    # Temperature plot
    ax1 = axes[0]
    T_plot = ax1.imshow(
        np.array(state[3]),
        extent=[0, ROOM_WIDTH, 0, ROOM_HEIGHT],
        origin="lower",
        cmap="coolwarm",
        vmin=T_AC_OUTLET,
        vmax=T_INITIAL,
        aspect="equal",
    )
    cbar1 = plt.colorbar(T_plot, ax=ax1, label="Temperature (°C)")
    ax1.set_xlabel("Width (m)")
    ax1.set_ylabel("Height (m)")
    ax1.set_title("Temperature Distribution")

    # Draw AC unit
    ac_x = AC_X_START * DX
    ac_width = (AC_X_END - AC_X_START) * DX
    ac_y = AC_Y_POS * DY
    ax1.add_patch(
        plt.Rectangle(
            (ac_x, ac_y),
            ac_width,
            ROOM_HEIGHT - ac_y,
            facecolor="gray",
            edgecolor="black",
            linewidth=2,
            label="AC Unit",
        )
    )
    ax1.legend(loc="upper right")

    # Velocity field plot (streamlines + magnitude)
    ax2 = axes[1]
    u_np = np.array(state[0])
    v_np = np.array(state[1])
    speed = np.sqrt(u_np**2 + v_np**2)

    speed_plot = ax2.imshow(
        speed,
        extent=[0, ROOM_WIDTH, 0, ROOM_HEIGHT],
        origin="lower",
        cmap="viridis",
        vmin=0,
        vmax=abs(AC_VELOCITY),
        aspect="equal",
    )
    cbar2 = plt.colorbar(speed_plot, ax=ax2, label="Velocity magnitude (m/s)")

    # Add quiver plot for velocity direction
    skip = 4
    quiver = ax2.quiver(
        X[::skip, ::skip],
        Y[::skip, ::skip],
        u_np[::skip, ::skip],
        v_np[::skip, ::skip],
        color="white",
        alpha=0.7,
        scale=5,
    )

    ax2.set_xlabel("Width (m)")
    ax2.set_ylabel("Height (m)")
    ax2.set_title("Velocity Field")

    # Draw AC unit on velocity plot too
    ax2.add_patch(
        plt.Rectangle(
            (ac_x, ac_y),
            ac_width,
            ROOM_HEIGHT - ac_y,
            facecolor="gray",
            edgecolor="black",
            linewidth=2,
        )
    )

    # Time and temperature display
    time_text = ax1.text(
        0.02,
        0.98,
        "",
        transform=ax1.transAxes,
        verticalalignment="top",
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    plt.tight_layout()

    # Storage for state between frames
    state_holder = {"state": state, "step": 0}

    def update(frame):
        """Update function for animation."""
        # --- MODIFICATION START ---
        # Increased steps per frame to speed up simulation time relative to real time
        # Old: 10 steps * 0.005s = 0.05s sim time per frame
        # New: 40 steps * 0.005s = 0.20s sim time per frame
        steps_per_frame = 40
        # --- MODIFICATION END ---

        for _ in range(steps_per_frame):
            state_holder["state"] = simulation_step(state_holder["state"])
            state_holder["step"] += 1

        u, v, p, T = state_holder["state"]

        # Update temperature plot
        T_np = np.array(T)
        T_plot.set_array(T_np)

        # Update velocity plot
        u_np = np.array(u)
        v_np = np.array(v)
        speed = np.sqrt(u_np**2 + v_np**2)
        speed_plot.set_array(speed)

        # Update quiver arrows
        quiver.set_UVC(u_np[::skip, ::skip], v_np[::skip, ::skip])

        # Update time and average temperature display
        sim_time = state_holder["step"] * DT
        avg_temp = float(jnp.mean(T))
        time_text.set_text(
            f"Time: {sim_time:.1f}s\n"
            f"Avg Temp: {avg_temp:.1f}°C\n"
            f"AC Outlet: {T_AC_OUTLET}°C"
        )

        return T_plot, speed_plot, quiver, time_text

    print("Starting animation...")
    print(f"Room: {ROOM_WIDTH}m x {ROOM_HEIGHT}m")
    print(f"Initial temperature: {T_INITIAL}°C")
    print(f"AC outlet temperature: {T_AC_OUTLET}°C")
    print("Generating frames...")

    # --- MODIFICATION START ---
    # Increased total frames
    # 300 frames * 0.2s sim time/frame = 60.0 seconds total simulated time
    ani = animation.FuncAnimation(fig, update, frames=300, interval=50, blit=False)
    # --- MODIFICATION END ---

    return fig, ani


def run_simulation_and_save():
    """Run simulation and save snapshots."""
    print("=" * 60)
    print("JAX-CFD Air Conditioner Cooling Simulation")
    print("=" * 60)

    # Check JAX backend
    print(f"\nJAX backend: {jax.default_backend()}")
    print(f"Grid size: {NX} x {NY}")
    print(f"Time step: {DT}s")

    # Initialize
    state = create_initial_conditions()

    # Create figure for snapshots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle("Room Cooling Progression Over Time", fontsize=14, fontweight="bold")

    # Simulation parameters
    total_time = 60.0  # seconds
    snapshot_times = [0, 10, 20, 30, 45, 60]  # seconds
    steps_per_second = int(1.0 / DT)

    # Coordinate grids
    x = np.linspace(0, ROOM_WIDTH, NX)
    y = np.linspace(0, ROOM_HEIGHT, NY)

    snapshot_idx = 0
    current_time = 0.0
    step = 0

    print("\nRunning simulation...")

    while current_time <= total_time and snapshot_idx < len(snapshot_times):
        # Check if we should save a snapshot
        if current_time >= snapshot_times[snapshot_idx]:
            u, v, p, T = state
            T_np = np.array(T)
            avg_temp = float(jnp.mean(T))

            # Plot snapshot
            row = snapshot_idx // 3
            col = snapshot_idx % 3
            ax = axes[row, col]

            im = ax.imshow(
                T_np,
                extent=[0, ROOM_WIDTH, 0, ROOM_HEIGHT],
                origin="lower",
                cmap="coolwarm",
                vmin=T_AC_OUTLET,
                vmax=T_INITIAL,
                aspect="equal",
            )

            # Add velocity vectors
            u_np = np.array(u)
            v_np = np.array(v)
            skip = 6
            X, Y = np.meshgrid(x[::skip], y[::skip])
            ax.quiver(
                X,
                Y,
                u_np[::skip, ::skip],
                v_np[::skip, ::skip],
                color="black",
                alpha=0.5,
                scale=8,
            )

            # Draw AC unit
            ac_x = AC_X_START * DX
            ac_width = (AC_X_END - AC_X_START) * DX
            ac_y = AC_Y_POS * DY
            ax.add_patch(
                plt.Rectangle(
                    (ac_x, ac_y),
                    ac_width,
                    ROOM_HEIGHT - ac_y,
                    facecolor="gray",
                    edgecolor="black",
                    linewidth=1,
                )
            )

            ax.set_title(f"t = {snapshot_times[snapshot_idx]}s\nAvg: {avg_temp:.1f}°C")
            ax.set_xlabel("Width (m)")
            ax.set_ylabel("Height (m)")

            if snapshot_idx == 0:
                plt.colorbar(im, ax=ax, label="°C")

            print(f"  t={current_time:.1f}s: Avg temp = {avg_temp:.1f}°C")
            snapshot_idx += 1

        # Advance simulation
        state = simulation_step(state)
        step += 1
        current_time = step * DT

    plt.tight_layout()

    # Save figure
    output_path = "ac_cooling_snapshots.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"\nSnapshots saved to: {output_path}")

    # Also create the animation
    print("\nCreating animation...")
    fig_anim, ani = create_visualization()

    # Save animation as GIF
    gif_path = "ac_cooling_animation.gif"
    ani.save(gif_path, writer="pillow", fps=20)
    print(f"Animation saved to: {gif_path}")

    plt.close("all")

    return output_path, gif_path


if __name__ == "__main__":
    # Run and save outputs
    snapshot_path, gif_path = run_simulation_and_save()

    print("\n" + "=" * 60)
    print("Simulation complete!")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - Snapshots: {snapshot_path}")
    print(f"  - Animation: {gif_path}")
