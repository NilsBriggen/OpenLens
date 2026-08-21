"""
Celery Tasks for Processing

Asynchronous tasks for metadata extraction, text processing, and data normalization.
"""

from celery import shared_task
from processors.metadata_extractor import metadata_extractor
import os
import tempfile
from typing import Dict, Any


@shared_task(bind=True, max_retries=3)
def extract_metadata_task(self, file_path: str) -> Dict[str, Any]:
    """
    Celery task to extract EXIF metadata from an image file.
    
    Args:
        file_path: Path to the image file.
        
    Returns:
        Dictionary with extracted metadata or error message.
    """
    try:
        metadata = metadata_extractor.extract_exif_from_image(file_path)
        return {"success": True, "metadata": metadata}
    except Exception as e:
        self.retry(exc=e, countdown=60)
        return {"success": False, "error": str(e)}


@shared_task(bind=True, max_retries=3)
def extract_metadata_from_bytes_task(self, image_bytes: bytes) -> Dict[str, Any]:
    """
    Celery task to extract EXIF metadata from image bytes.
    
    Args:
        image_bytes: Raw bytes of the image.
        
    Returns:
        Dictionary with extracted metadata or error message.
    """
    try:
        metadata = metadata_extractor.extract_exif_from_bytes(image_bytes)
        return {"success": True, "metadata": metadata}
    except Exception as e:
        self.retry(exc=e, countdown=60)
        return {"success": False, "error": str(e)}


@shared_task(bind=True, max_retries=3)
def extract_text_metadata_task(self, text: str) -> Dict[str, Any]:
    """
    Celery task to extract metadata from text (hashtags, geotags, etc.).
    
    Args:
        text: Input text.
        
    Returns:
        Dictionary with extracted metadata or error message.
    """
    try:
        metadata = metadata_extractor.extract_text_metadata(text)
        return {"success": True, "metadata": metadata}
    except Exception as e:
        self.retry(exc=e, countdown=60)
        return {"success": False, "error": str(e)}


@shared_task(bind=True, max_retries=3)
def process_image_task(self, file_path: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Celery task to process an image (extract metadata, save to output dir).
    
    Args:
        file_path: Path to the input image.
        output_dir: Optional directory to save processed data.
        
    Returns:
        Dictionary with processing results or error message.
    """
    try:
        # Extract metadata
        metadata = metadata_extractor.extract_exif_from_image(file_path)
        
        # Save metadata to JSON file if output_dir is provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            import json
            output_path = os.path.join(output_dir, f"{os.path.basename(file_path)}.json")
            with open(output_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "file_path": file_path,
            "metadata": metadata,
            "output_path": output_path if output_dir else None,
        }
    except Exception as e:
        self.retry(exc=e, countdown=60)
        return {"success": False, "error": str(e)}


@shared_task(bind=True, max_retries=3)
def normalize_data_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task to normalize data (e.g., phone numbers, addresses).
    
    Args:
        data: Input data dictionary.
        
    Returns:
        Dictionary with normalized data or error message.
    """
    try:
        normalized = {}
        
        # Normalize phone numbers (remove non-digits, add country code if missing)
        if "phone" in data:
            phone = str(data["phone"])
            phone_digits = re.sub(r"[^\d]", "", phone)
            if phone_digits.startswith("8"):
                phone_digits = "7" + phone_digits[1:]  # Convert Russian 8 to +7
            normalized["phone"] = f"+{phone_digits}"
        
        # Normalize addresses (uppercase, remove extra spaces)
        if "address" in data:
            address = str(data["address"])
            address = " ".join(address.split()).title()
            normalized["address"] = address
        
        # Normalize names (title case)
        if "first_name" in data:
            normalized["first_name"] = str(data["first_name"]).title()
        if "last_name" in data:
            normalized["last_name"] = str(data["last_name"]).title()
        
        # Copy other fields as-is
        for key, value in data.items():
            if key not in normalized:
                normalized[key] = value
        
        return {"success": True, "normalized_data": normalized}
    except Exception as e:
        self.retry(exc=e, countdown=60)
        return {"success": False, "error": str(e)}


# Helper for phone normalization
import re
