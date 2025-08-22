from PIL import Image
import pytesseract, re

def extract_meter_reading(text):
    pattern = r"Current Meter Reading:\s*(\d+)"
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None

def extract_date(text):
    # Look for date pattern in format DD/MM/YYYY or similar
    pattern = r"(\d{1,2}/\d{1,2}/\d{4})"
    matches = re.findall(pattern, text)
    return matches[-1] if matches else None  # Return the last date found

def read_bill():
    image = Image.open(r"./images/gasBill.png")
    text = pytesseract.image_to_string(image)

    meter_reading = extract_meter_reading(text)
    date = extract_date(text)

    print(f"Current meter reading: {meter_reading}")
    print(f"Date: {date}")

read_bill()
