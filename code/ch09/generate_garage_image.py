import os
import multiprocessing
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from autogluon.multimodal import MultiModalPredictor

plt.rcParams.update(
    {
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "font.family": "sans-serif",
        # Ensure saved figure has a white background so transparent axes don't look odd
        "savefig.facecolor": "white",
    }
)


def generate_visual():
    model_path = "models/classification/garage_door_model"
    # Ensure this points to a valid image in your 'dataset' folder
    image_path = "data/classification/garage_open.png"

    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        # Create dummy data for demonstration if files are missing
        print("--- Creating dummy data for demonstration purposes ---")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        dummy_img = Image.fromarray(
            np.random.randint(0, 255, (300, 400, 3), dtype=np.uint8)
        )
        dummy_img.save(image_path)
        detected_label = "DEMO_MODE"
        conf = 0.99
    else:
        # 1. Load the predictor
        predictor = MultiModalPredictor.load(model_path)

        # 2. Get Prediction
        proba = predictor.predict_proba({"image": [image_path]})
        conf = np.max(proba[0])
        class_idx = np.argmax(proba[0])
        labels = predictor.class_labels
        detected_label = labels[class_idx]

    img_pil = Image.open(image_path).convert("RGB")
    target_size = (224, 224)
    img_resized_pil = img_pil.resize(target_size)
    img_array_rgb = np.array(img_resized_pil)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # --- Left Panel: Input ---
    axes[0].imshow(img_array_rgb)
    axes[0].set_title(f"Input sensor data\n(garage view)")
    axes[0].axis("off")

    img_gray_pil = img_resized_pil.convert("L")
    img_gray_array = np.array(img_gray_pil)
    dimmed_background = (img_gray_array * 0.3).astype(np.uint8)

    grad_y, grad_x = np.gradient(img_gray_array.astype(float))
    feature_map_raw = np.sqrt(grad_x**2 + grad_y**2)

    f_min, f_max = feature_map_raw.min(), feature_map_raw.max()
    feature_map_norm = (feature_map_raw - f_min) / (f_max - f_min + 1e-8)

    axes[1].imshow(dimmed_background, cmap="gray", vmin=0, vmax=255)

    heatmap_plot = axes[1].imshow(feature_map_norm, cmap="hot", alpha=0.85)

    axes[1].set_title(
        f"AI classification: {detected_label.upper()}\nConfidence: {conf*100:.1f}%"
    )
    axes[1].axis("off")

    # Optional: Add a colorbar to explain the heatmap brightness
    # cbar = fig.colorbar(heatmap_plot, ax=axes[1], fraction=0.046, pad=0.04)
    # cbar.set_label('Feature Activation Strength', rotation=270, labelpad=15)

    plt.tight_layout()
    # Save with a higher DPI for print quality
    output_filename = "garage_ai_logic_high_contrast.png"
    plt.savefig(output_filename, dpi=300, bbox_inches="tight")
    print(f"Image saved as {output_filename}")
    # plt.show() # Commented out for cleaner automated execution


if __name__ == "__main__":
    multiprocessing.freeze_support()
    generate_visual()
