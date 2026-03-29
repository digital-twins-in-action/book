import matplotlib.pyplot as plt
import numpy as np


def create_rendering_comparison_chart():
    # We use a logarithmic scale for the X-axis (10 objects to 1,000,000 objects)
    x = np.logspace(1, 6, 500)

    # Define conceptual performance curves (Normalized 0-100 score)
    # These heuristics model how performance degrades for each tech

    # SVG: Excellent for low counts, but crashes fast due to DOM overhead (~1k-5k limit)
    # Formula: Sigmoid dropoff centered early
    svg_perf = 100 / (1 + (x / 2000) ** 2)

    # Canvas: Immediate mode, faster, CPU bound (~10k-50k limit)
    # Formula: Sigmoid dropoff centered later
    canvas_perf = 100 / (1 + (x / 20000) ** 1.5)

    # WebGL: GPU accelerated, handles massive counts (>100k)
    # Formula: Stays high, drops off only at massive scale
    webgl_perf = 100 / (1 + (x / 500000) ** 1.5)

    plt.figure(figsize=(16, 10))

    plt.plot(x, svg_perf, label="SVG (DOM)", color="#d31518", linewidth=5)
    plt.plot(x, canvas_perf, label="HTML5 Canvas", color="#e6cb00", linewidth=5)
    plt.plot(x, webgl_perf, label="WebGL (GPU)", color="#0060b1", linewidth=5)

    plt.xscale("log")  # Logarithmic X axis is crucial for this magnitude of difference
    plt.ylim(0, 115)
    plt.xlim(10, 1000000)

    plt.xlabel("Number of visual elements (log scale)", fontsize=20, fontweight="bold")
    plt.ylabel("Rendering performance / FPS", fontsize=20, fontweight="bold")
    plt.title("Rendering technology selection", fontsize=24, fontweight="bold", pad=20)

    plt.yticks([])

    plt.tick_params(axis="x", labelsize=16)

    # SVG Zone
    plt.text(
        40,
        93,
        "Best for interactivity\n(Floorplans, schematics)",
        color="#d31518",
        fontsize=16,
        ha="left",
        va="center",
        fontweight="bold",
    )

    # Canvas Zone
    plt.text(
        13000,
        75,
        "Best for dynamic 2D\n(Live charts, 10k points)",
        color="#e6cb00",
        fontsize=16,
        ha="left",
        va="center",
        fontweight="bold",
    )

    # WebGL Zone
    plt.text(
        65000,
        100,
        "Best for massive data\n(3D scenes, 100k+ points)",
        color="#0060b1",
        fontsize=16,
        ha="left",
        va="center",
        fontweight="bold",
    )

    # "Crash" Threshold Line
    plt.axhline(y=40, color="gray", linestyle="--", alpha=0.5, linewidth=2)
    plt.text(
        12,
        43,
        "Minimum acceptable frame rate (30 FPS)",
        color="gray",
        fontsize=16,
        style="italic",
        fontweight="bold",
    )

    plt.legend(loc="lower left", fontsize=16, frameon=True, framealpha=0.9)
    plt.grid(True, which="both", ls="-", alpha=0.15)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    create_rendering_comparison_chart()
