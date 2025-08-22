import pytesseract
import numpy as np
from PIL import Image, ImageOps


def extract_meter_reading(image_path):
    # 1. Open the image
    img = Image.open(image_path)
    print(f"Opened image: {image_path}")

    # 2. The meter reading is roughly in this area.
    crop_box = (
        1000,
        890,
        1700,
        1030,
    )  # Estimated coordinates (left, upper, right, lower)

    # 3. Crop the image to focus on the meter digits
    cropped_img = img.crop(crop_box)
    print(f"Cropped image to bounding box: {crop_box}")

    # 4. Convert cropped image to grayscale
    gray_img = ImageOps.grayscale(cropped_img)
    print("Converted cropped image to grayscale.")

    # 5. Invert the grayscale image
    # This often helps OCR for dark digits on a light background (like the meter reading)
    inverted_img = ImageOps.invert(gray_img)
    print("Inverted grayscale image.")

    # Optional: Save intermediate images for debugging
    cropped_img.save("meter_cropped.jpg")
    gray_img.save("meter_grayscale.jpg")
    inverted_img.save("meter_inverted.jpg")
    print(
        "Saved intermediate images (meter_cropped.jpg, meter_grayscale.jpg, meter_inverted.jpg) for review."
    )

    # 6. Use OCR to extract text
    # 'config' options can be crucial for accuracy:
    # --psm 7: Treat the image as a single line of text (often good for meter readings).
    # -c tessedit_char_whitelist=0123456789: Restrict OCR to only digits.
    # This helps in preventing misinterpretations of characters.
    meter_reading = pytesseract.image_to_string(
        inverted_img, config="--psm 7 -c tessedit_char_whitelist=0123456789"
    )

    # Clean up the extracted text (remove whitespace, newlines)
    meter_reading = meter_reading.strip()
    return meter_reading


def main():
    # Extract the reading
    reading = extract_meter_reading("./images/waterMeter.jpg")

    if reading:
        print(f"Water Meter Reading: {reading}")
    else:
        print("Could not extract a valid reading from the image.")


if __name__ == "__main__":
    main()
