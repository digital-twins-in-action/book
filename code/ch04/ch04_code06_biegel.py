import requests
from datetime import datetime, timedelta

# Lake Kariba coordinates and image settings
bbox = (26.5, -18.5, 29.0, -16.0)  # (west, south, east, north)
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# GIBS WMS request parameters
params = {
    "SERVICE": "WMS",
    "VERSION": "1.1.1",
    "REQUEST": "GetMap",
    "LAYERS": "VIIRS_SNPP_CorrectedReflectance_TrueColor",
    "SRS": "EPSG:4326",
    "BBOX": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
    "WIDTH": "1024",
    "HEIGHT": "640",
    "FORMAT": "image/png",
    "TIME": yesterday,
    "TRANSPARENT": "true",
}

# Get the image
print(f"Getting Lake Kariba VIIRS imagery for {yesterday}...")
response = requests.get(
    "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi", params=params
)

if "image" in response.headers.get("content-type", ""):
    filename = f"lake_kariba_{yesterday}.png"
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"✓ Saved: {filename}")
else:
    print(f"✗ Error: {response.text[:200]}")
