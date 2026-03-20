import sys
import multiprocessing
from unittest.mock import MagicMock
import os

# --- 1. NUCLEAR MOCK (Keep this to prevent NVML errors) ---
# We apply this globally so even worker processes see the fake driver
mock_gpu = MagicMock()
sys.modules["pynvml"] = mock_gpu
sys.modules["nvidia_smi"] = mock_gpu
sys.modules["nvml"] = mock_gpu

# --- 2. IMPORTS (Must come after mocks) ---
import pandas as pd
from autogluon.multimodal import MultiModalPredictor


def run_training():
    # --- 3. PREPARE DATA ---
    data = []
    dataset_path = "data/classification/dataset"

    if not os.path.exists(dataset_path):
        print(f"Error: '{dataset_path}' directory not found.")
        return

    for label in ["open", "closed"]:
        folder_path = os.path.join(dataset_path, label)
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.lower().endswith((".jpg", ".png", ".jpeg")):
                    data.append(
                        {"image": os.path.join(folder_path, file), "label": label}
                    )

    if not data:
        print("No images found. Check folder structure.")
        return

    train_data = pd.DataFrame(data)
    print(f"Found {len(train_data)} images. Starting training...")

    # --- 4. TRAIN MODEL ---
    predictor = MultiModalPredictor(label="label", problem_type="binary")

    predictor.fit(
        train_data=train_data,
        time_limit=60 * 5,  # 5 minutes
        hyperparameters={"env.num_gpus": 0},  # Force CPU config as backup
    )

    predictor.save("models/classification/garage_door_model")
    print("Training complete. Model saved.")


if __name__ == "__main__":
    # This line is required for some macOS configurations
    multiprocessing.freeze_support()
    run_training()
