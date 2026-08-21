"""
Tests for the Metadata Extractor module.
"""

import os
import io
import tempfile
from PIL import Image
from PIL.ExifTags import TAGS
import pytest
from processors.metadata_extractor import MetadataExtractor


class TestMetadataExtractor:
    """Test cases for MetadataExtractor."""

    @staticmethod
    def create_sample_image_with_exif():
        """Create a sample image with embedded EXIF data for testing."""
        # Create a blank image
        img = Image.new('RGB', (100, 100), color='red')

        # Save to a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_file.name, format='JPEG')
        return temp_file.name

    def test_extract_exif_from_image(self):
        """Test extracting EXIF data from an image file."""
        # Create a sample image
        image_path = self.create_sample_image_with_exif()
        try:
            metadata = MetadataExtractor.extract_exif_from_image(image_path)
            assert isinstance(metadata, dict)
            # Basic validation (no error key)
            assert "error" not in metadata or metadata.get("error") is None
        finally:
            os.unlink(image_path)

    def test_extract_exif_from_bytes(self):
        """Test extracting EXIF data from image bytes."""
        # Create a sample image
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        metadata = MetadataExtractor.extract_exif_from_bytes(img_bytes.read())
        assert isinstance(metadata, dict)

    def test_extract_text_metadata(self):
        """Test extracting metadata from text."""
        text = "Check out this #OSINT tool! @[55.75,37.61] #Moscow @user123"
        metadata = MetadataExtractor.extract_text_metadata(text)

        assert "hashtags" in metadata
        assert "#OSINT" in metadata["hashtags"] or "OSINT" in metadata["hashtags"]
        assert "#Moscow" in metadata["hashtags"] or "Moscow" in metadata["hashtags"]
        assert "geotags" in metadata
        assert len(metadata["geotags"]) == 1
        assert metadata["geotags"][0]["latitude"] == 55.75
        assert metadata["geotags"][0]["longitude"] == 37.61
        assert "mentions" in metadata
        assert "user123" in metadata["mentions"]

    def test_extract_text_metadata_with_urls(self):
        """Test extracting URLs from text."""
        text = "Visit https://example.com for more info."
        metadata = MetadataExtractor.extract_text_metadata(text)

        assert "urls" in metadata
        assert "https://example.com" in metadata["urls"]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
