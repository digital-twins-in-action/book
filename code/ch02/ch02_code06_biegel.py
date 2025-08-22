from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import webbrowser


def main():
    # Extract GPS data from EXIF
    exif = Image.open("./images/rockPaintings.jpg")._getexif()
    gps = next(
        (
            dict((GPSTAGS.get(k, k), v) for k, v in val.items())
            for tag, val in exif.items()
            if TAGS.get(tag) == "GPSInfo"
        ),
        {},
    )

    # Convert GPS coordinates (handles both fraction and float formats)
    def convert_to_degrees(value):
        """Convert GPS coordinates to degrees in float format"""
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    lat = convert_to_degrees(gps["GPSLatitude"])
    lat *= -1 if gps["GPSLatitudeRef"] == "S" else 1

    lon = convert_to_degrees(gps["GPSLongitude"])
    lon *= -1 if gps["GPSLongitudeRef"] == "W" else 1

    print(lat, lon)
    webbrowser.open(f"https://www.google.com/maps?q={lat},{lon}")


if __name__ == "__main__":
    main()
