import sys
from unittest.mock import MagicMock
import multiprocessing
import os

# --- 1. NUCLEAR MOCK (Required for Inference too) ---
mock_gpu = MagicMock()
sys.modules["pynvml"] = mock_gpu
sys.modules["nvidia_smi"] = mock_gpu
sys.modules["nvml"] = mock_gpu

from autogluon.multimodal import MultiModalPredictor


def check_garage(image_path):
    if not os.path.exists(image_path):
        print(f"Error: Image '{image_path}' not found.")
        return

    print(f"Loading model to analyze: {image_path}...")

    # 2. LOAD THE MODEL
    predictor = MultiModalPredictor.load("models/classification/garage_door_model")

    # 3. RUN PREDICTION
    prediction = predictor.predict({"image": [image_path]})
    proba = predictor.predict_proba({"image": [image_path]})

    if hasattr(proba, "iloc"):
        # It's a Pandas DataFrame
        confidence = proba.iloc[0].max()
    else:
        # It's a Numpy Array
        confidence = proba.max()

    # Handle prediction format safely (Series vs Array)
    status = prediction[0] if hasattr(prediction, "__getitem__") else prediction

    print("\n" + "=" * 30)
    print(f"GARAGE STATUS: {str(status).upper()}")
    print(f"CONFIDENCE:    {confidence:.1%}")
    print("=" * 30 + "\n")

    return status


if __name__ == "__main__":
    # Guard needed for macOS
    multiprocessing.freeze_support()

    test_image = "data/classification/garage_open.png"

    try:
        check_garage(test_image)
    except Exception as e:
        print(f"Inference failed: {e}")
