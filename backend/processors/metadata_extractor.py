"""
Metadata Extractor Module for OpenLens

Extracts EXIF metadata from images (GPS, timestamps, device info) and parses
geotags/hashtags from text.

Dependencies:
- Pillow: For basic image metadata
- exifread: For detailed EXIF data
- geopy: For GPS coordinate conversion
"""

import re
import io
from typing import Dict, Any, Optional, Tuple
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import exifread


class MetadataExtractor:
    """Extracts metadata from images and text."""

    # Map exifread GPS tag names to GPSTAGS numeric keys
    _EXIFREAD_GPS_MAP = {
        "GPSLatitude": 2,
        "GPSLatitudeRef": 1,
        "GPSLongitude": 4,
        "GPSLongitudeRef": 3,
        "GPSAltitude": 6,
        "GPSAltitudeRef": 5,
        "GPSTimeStamp": 7,
        "GPSDateStamp": 29,
    }

    @staticmethod
    def extract_exif_from_image(image_path: str) -> Dict[str, Any]:
        """
        Extract EXIF metadata from an image file.

        Args:
            image_path: Path to the image file.

        Returns:
            Dictionary containing EXIF metadata (e.g., GPS, timestamp, device info).
        """
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                return MetadataExtractor._parse_exif_tags(tags)
        except Exception as e:
            return {"error": f"Failed to extract EXIF: {str(e)}"}

    @staticmethod
    def extract_exif_from_bytes(image_bytes: bytes) -> Dict[str, Any]:
        """
        Extract EXIF metadata from image bytes.

        Args:
            image_bytes: Raw bytes of the image.

        Returns:
            Dictionary containing EXIF metadata.
        """
        try:
            tags = exifread.process_file(io.BytesIO(image_bytes), details=False)
            return MetadataExtractor._parse_exif_tags(tags)
        except Exception as e:
            return {"error": f"Failed to extract EXIF: {str(e)}"}

    @staticmethod
    def _parse_exif_tags(tags: Dict) -> Dict[str, Any]:
        """
        Parse EXIF tags into a structured dictionary.

        Args:
            tags: Raw EXIF tags from exifread.

        Returns:
            Parsed metadata dictionary.
        """
        metadata = {}

        # Extract GPS coordinates
        gps_data = MetadataExtractor._extract_gps(tags)
        if gps_data:
            metadata["gps"] = gps_data

        # Extract timestamp
        timestamp = MetadataExtractor._extract_timestamp(tags)
        if timestamp:
            metadata["timestamp"] = timestamp

        # Extract device info
        device_info = MetadataExtractor._extract_device_info(tags)
        if device_info:
            metadata.update(device_info)

        # Extract other common fields
        for tag, value in tags.items():
            tag_name = str(tag)
            if tag_name in TAGS:
                metadata[TAGS[tag_name]] = str(value)

        return metadata

    @staticmethod
    def _extract_gps(tags: Dict) -> Optional[Dict[str, float]]:
        """
        Extract GPS coordinates from EXIF tags.

        Args:
            tags: Raw EXIF tags.

        Returns:
            Dictionary with latitude, longitude, and altitude (if available).
        """
        # GPS tags in exifread are prefixed with "GPS " (e.g., "GPS GPSLatitude")
        gps_tags = {}
        for tag in tags:
            tag_str = str(tag)
            if tag_str.startswith("GPS "):
                # Remove "GPS " prefix (e.g., "GPS GPSLatitude" -> "GPSLatitude")
                gps_key = tag_str[4:]
                if gps_key in MetadataExtractor._EXIFREAD_GPS_MAP:
                    # Map to GPSTAGS numeric key
                    gps_numeric_key = MetadataExtractor._EXIFREAD_GPS_MAP[gps_key]
                    if gps_numeric_key in GPSTAGS:
                        gps_tags[GPSTAGS[gps_numeric_key]] = tags[tag]

        if not gps_tags:
            return None

        try:
            lat = MetadataExtractor._convert_gps_coordinate(
                gps_tags.get("GPSLatitude"),
                gps_tags.get("GPSLatitudeRef")
            )
            lon = MetadataExtractor._convert_gps_coordinate(
                gps_tags.get("GPSLongitude"),
                gps_tags.get("GPSLongitudeRef")
            )
            alt = MetadataExtractor._extract_altitude(
                gps_tags.get("GPSAltitude"),
                gps_tags.get("GPSAltitudeRef")
            )

            result = {"latitude": lat, "longitude": lon}
            if alt is not None:
                result["altitude"] = alt
            return result
        except Exception:
            return None

    @staticmethod
    def _convert_gps_coordinate(coord: Any, ref: Any) -> Optional[float]:
        """
        Convert GPS coordinate from EXIF format to decimal degrees.

        Args:
            coord: GPS coordinate value (e.g., [37, 46, 741/25] or exifread.Ratio).
            ref: Reference (N/S/E/W).

        Returns:
            Decimal degrees (e.g., 37.7749).
        """
        if not coord or not ref:
            return None

        try:
            # Handle list format (e.g., [37, 46, 741/25])
            if isinstance(coord, list) and len(coord) == 3:
                degrees = coord[0]
                minutes = coord[1]
                seconds = coord[2]
                if isinstance(seconds, tuple):
                    seconds = seconds[0] / seconds[1]
                decimal = degrees + (minutes / 60) + (seconds / 3600)
            # Handle exifread.Ratio format
            elif hasattr(coord, 'values'):
                degrees = coord.values[0].num / coord.values[0].den
                minutes = coord.values[1].num / coord.values[1].den
                seconds = coord.values[2].num / coord.values[2].den
                decimal = degrees + (minutes / 60) + (seconds / 3600)
            else:
                return None

            if ref in ["S", "W"]:
                decimal *= -1
            return decimal
        except Exception:
            return None

    @staticmethod
    def _extract_altitude(altitude: Any, altitude_ref: Any = None) -> Optional[float]:
        """
        Extract altitude from EXIF GPS altitude tag.

        Args:
            altitude: GPS altitude value.
            altitude_ref: Altitude reference (0 = above sea level, 1 = below).

        Returns:
            Altitude in meters.
        """
        if not altitude:
            return None
        try:
            if hasattr(altitude, 'values'):
                alt_value = altitude.values[0].num / altitude.values[0].den
            else:
                alt_value = float(altitude)
            
            # If altitude_ref is 1 (below sea level), make negative
            if altitude_ref and altitude_ref == 1:
                alt_value *= -1
            return alt_value
        except Exception:
            return None

    @staticmethod
    def _extract_timestamp(tags: Dict) -> Optional[str]:
        """
        Extract timestamp from EXIF tags.

        Args:
            tags: Raw EXIF tags.

        Returns:
            Timestamp string (e.g., "2023:10:15 12:34:56").
        """
        for tag in ["Image DateTime", "EXIF DateTimeOriginal", "EXIF DateTimeDigitized"]:
            if tag in tags:
                return str(tags[tag])
        return None

    @staticmethod
    def _extract_device_info(tags: Dict) -> Dict[str, str]:
        """
        Extract device information (make, model, software) from EXIF tags.

        Args:
            tags: Raw EXIF tags.

        Returns:
            Dictionary with device info.
        """
        device_info = {}
        if "Image Make" in tags:
            device_info["make"] = str(tags["Image Make"])
        if "Image Model" in tags:
            device_info["model"] = str(tags["Image Model"])
        if "Image Software" in tags:
            device_info["software"] = str(tags["Image Software"])
        return device_info

    @staticmethod
    def extract_text_metadata(text: str) -> Dict[str, Any]:
        """
        Extract geotags, hashtags, and other metadata from text.

        Args:
            text: Input text (e.g., social media post).

        Returns:
            Dictionary with extracted metadata.
        """
        metadata = {}

        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        if hashtags:
            metadata["hashtags"] = hashtags

        # Extract geotags (e.g., @[latitude,longitude])
        geotags = re.findall(r'@\[([-+]?\d+\.?\d*,\s*[-+]?\d+\.?\d*)\]', text)
        if geotags:
            metadata["geotags"] = [
                {"latitude": float(coord.split(",")[0].strip()),
                 "longitude": float(coord.split(",")[1].strip())}
                for coord in geotags
            ]

        # Extract mentions (e.g., @username)
        mentions = re.findall(r'@(\w+)', text)
        if mentions:
            metadata["mentions"] = mentions

        # Extract URLs
        urls = re.findall(r'https?://[^\s]+', text)
        if urls:
            metadata["urls"] = urls

        return metadata


# Singleton instance for easy use
metadata_extractor = MetadataExtractor()
