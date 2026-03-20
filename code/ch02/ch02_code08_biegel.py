from pyproj import Transformer

# Create a transformer from UTM Zone 36S to WGS84 (lat/lon)
transformer = Transformer.from_crs("EPSG:32736", "EPSG:4326", always_xy=True)

# Transform coordinates: easting, northing -> longitude, latitude
easting, northing = 471519, 7977628
lon, lat = transformer.transform(easting, northing)

print(f"UTM:   {easting}m, {northing}m")
print(f"WGS84: {lon:.6f}°E, {lat:.6f}°S")
