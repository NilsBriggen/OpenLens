"""
Script to create a sample image with embedded EXIF data for testing.
"""

import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif

# Create a sample image
img = Image.new('RGB', (200, 200), color='blue')

# Define EXIF data (GPS coordinates for San Francisco)
latitude = 37.7749  # San Francisco latitude
longitude = -122.4194  # San Francisco longitude

# Convert decimal degrees to EXIF format (degrees, minutes, seconds)
def dec_to_dms(decimal):
    degrees = int(decimal)
    minutes = int((decimal - degrees) * 60)
    seconds = (decimal - degrees - minutes / 60) * 3600
    return (degrees, minutes, seconds)

lat_deg, lat_min, lat_sec = dec_to_dms(abs(latitude))
lon_deg, lon_min, lon_sec = dec_to_dms(abs(longitude))

# Create EXIF GPS data
gps_ifd = {
    piexif.GPSIFD.GPSVersionID: (2, 2, 0, 0),
    piexif.GPSIFD.GPSLatitudeRef: 'N' if latitude >= 0 else 'S',
    piexif.GPSIFD.GPSLatitude: (
        (lat_deg, 1),
        (lat_min, 1),
        (int(lat_sec * 100), 100)
    ),
    piexif.GPSIFD.GPSLongitudeRef: 'E' if longitude >= 0 else 'W',
    piexif.GPSIFD.GPSLongitude: (
        (lon_deg, 1),
        (lon_min, 1),
        (int(lon_sec * 100), 100)
    ),
    piexif.GPSIFD.GPSAltitudeRef: 0,  # Above sea level
    piexif.GPSIFD.GPSAltitude: (10, 1),  # 10 meters
    piexif.GPSIFD.GPSTimeStamp: ((12, 1), (34, 1), (56, 1)),  # 12:34:56
    piexif.GPSIFD.GPSDateStamp: '2023:10:15',
}

# Create EXIF date/time
exif_ifd = {
    piexif.ImageIFD.DateTime: '2023:10:15 12:34:56',
    piexif.ImageIFD.Make: 'OpenLens',
    piexif.ImageIFD.Model: 'Test Camera',
    piexif.ImageIFD.Software: 'OpenLens v0.1',
}

# Combine EXIF data
exif_dict = {
    'GPS': gps_ifd,
    'Exif': exif_ifd,
}

# Convert to bytes
exif_bytes = piexif.dump(exif_dict)

# Save the image with EXIF data
output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sample_with_exif.jpg')
img.save(output_path, 'JPEG', exif=exif_bytes)

print(f"Sample image with EXIF data created at: {output_path}")
print(f"GPS Coordinates: {latitude}, {longitude}")
print(f"Timestamp: 2023:10:15 12:34:56")
