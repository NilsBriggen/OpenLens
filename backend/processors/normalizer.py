"""
Data Normalizer for OpenLens

Provides utilities for normalizing and cleaning data:
- Text normalization (lowercase, remove extra spaces, etc.)
- Phone number normalization
- Email address normalization
- URL normalization
- Date/time normalization
- Deduplication
- Validation

This module ensures consistent data formatting across the application.
"""

import re
from typing import Any, Dict, List, Optional, Set, Union
from datetime import datetime
import json


class DataNormalizer:
    """
    Normalizes various types of data for consistent storage and processing.
    """

    def __init__(self):
        """Initialize the data normalizer."""
        pass

    # --- Text Normalization ---

    def normalize_text(
        self,
        text: str,
        lowercase: bool = True,
        remove_extra_spaces: bool = True,
        remove_special_chars: bool = False,
        remove_punctuation: bool = False,
    ) -> str:
        """
        Normalize text by applying various transformations.
        
        Args:
            text: Input text to normalize.
            lowercase: Convert to lowercase (default: True).
            remove_extra_spaces: Remove extra whitespace (default: True).
            remove_special_chars: Remove special characters (default: False).
            remove_punctuation: Remove punctuation (default: False).
            
        Returns:
            Normalized text.
        """
        if not text:
            return ""
        
        result = text
        
        if remove_extra_spaces:
            result = re.sub(r'\s+', ' ', result).strip()
        
        if lowercase:
            result = result.lower()
        
        if remove_special_chars:
            result = re.sub(r'[^\w\s]', '', result)
        
        if remove_punctuation:
            result = re.sub(r'[\p{P}\p{S}]', '', result, flags=re.UNICODE)
        
        return result

    def normalize_hashtag(self, hashtag: str) -> str:
        """
        Normalize a hashtag (remove #, lowercase, remove special chars).
        
        Args:
            hashtag: Input hashtag.
            
        Returns:
            Normalized hashtag.
        """
        if not hashtag:
            return ""
        
        # Remove # and any leading/trailing whitespace
        hashtag = hashtag.strip().lstrip('#')
        # Remove special characters (keep letters, numbers, underscores)
        hashtag = re.sub(r'[^\w]', '', hashtag)
        # Lowercase
        hashtag = hashtag.lower()
        
        return hashtag

    def normalize_mention(self, mention: str) -> str:
        """
        Normalize a mention (remove @, lowercase).
        
        Args:
            mention: Input mention.
            
        Returns:
            Normalized mention.
        """
        if not mention:
            return ""
        
        # Remove @ and any leading/trailing whitespace
        mention = mention.strip().lstrip('@')
        # Lowercase
        mention = mention.lower()
        
        return mention

    # --- Phone Number Normalization ---

    def normalize_phone(self, phone: str) -> Optional[str]:
        """
        Normalize a phone number to international format.
        
        Args:
            phone: Input phone number.
            
        Returns:
            Normalized phone number in international format (e.g., +14155552671) or None if invalid.
        """
        if not phone:
            return None
        
        # Remove all non-digit characters
        digits = re.sub(r'[^\d]', '', phone)
        
        if not digits:
            return None
        
        # Handle country codes
        if digits.startswith('00'):
            # International format with 00 prefix
            digits = '+' + digits[2:]
        elif digits.startswith('0'):
            # Local format, assume country code based on length
            if len(digits) == 11 and digits.startswith('0'):
                # Russian format (8-XXX-XXX-XX-XX becomes +7-XXX-XXX-XX-XX)
                digits = '+7' + digits[1:]
            elif len(digits) == 11 and digits.startswith('0'):
                # US/Canada format (1-XXX-XXX-XXXX)
                digits = '+1' + digits[1:]
            else:
                # Unknown format, keep as is
                pass
        elif digits.startswith('8') and len(digits) == 11:
            # Russian format (8-XXX-XXX-XX-XX)
            digits = '+7' + digits[1:]
        elif len(digits) == 10:
            # US/Canada format (XXX-XXX-XXXX)
            digits = '+1' + digits
        elif len(digits) < 7:
            # Too short to be valid
            return None
        elif not digits.startswith('+'):
            # Add + prefix if missing
            digits = '+' + digits
        
        return digits

    # --- Email Normalization ---

    def normalize_email(self, email: str) -> Optional[str]:
        """
        Normalize an email address.
        
        Args:
            email: Input email address.
            
        Returns:
            Normalized email address (lowercase, no spaces) or None if invalid.
        """
        if not email:
            return None
        
        # Remove spaces and convert to lowercase
        email = email.replace(" ", "").lower()
        
        # Basic validation
        if '@' not in email or '.' not in email:
            return None
        
        # Remove any leading/trailing quotes
        email = email.strip('"\'')
        
        return email

    # --- URL Normalization ---

    def normalize_url(self, url: str) -> Optional[str]:
        """
        Normalize a URL.
        
        Args:
            url: Input URL.
            
        Returns:
            Normalized URL (lowercase, no trailing slash, https:// prefix) or None if invalid.
        """
        if not url:
            return None
        
        # Remove leading/trailing whitespace
        url = url.strip()
        
        # Remove trailing slash
        url = url.rstrip('/')
        
        # Convert to lowercase
        url = url.lower()
        
        # Ensure it starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove default ports
        url = re.sub(r':443($|/)', r'\1', url)
        url = re.sub(r':80($|/)', r'\1', url)
        
        # Remove www. prefix
        url = re.sub(r'https?://www\.', 'https://', url)
        
        return url

    # --- Date/Time Normalization ---

    def normalize_date(self, date_str: str, input_format: str = None) -> Optional[str]:
        """
        Normalize a date string to ISO format (YYYY-MM-DD).
        
        Args:
            date_str: Input date string.
            input_format: Optional strptime format for the input date.
            
        Returns:
            Date in ISO format (YYYY-MM-DD) or None if invalid.
        """
        if not date_str:
            return None
        
        try:
            if input_format:
                dt = datetime.strptime(date_str, input_format)
            else:
                # Try common formats
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%B %d, %Y', '%b %d, %Y']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # Try parsing as ISO format
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            return dt.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return None

    def normalize_datetime(self, datetime_str: str) -> Optional[str]:
        """
        Normalize a datetime string to ISO format (YYYY-MM-DDTHH:MM:SSZ).
        
        Args:
            datetime_str: Input datetime string.
            
        Returns:
            Datetime in ISO format or None if invalid.
        """
        if not datetime_str:
            return None
        
        try:
            # Try parsing as ISO format first
            try:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                pass
            
            # Try common datetime formats
            for fmt in [
                '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y %H:%M:%S',
                '%m/%d/%Y %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S%z',
            ]:
                try:
                    dt = datetime.strptime(datetime_str, fmt)
                    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    continue
            
            return None
        except (ValueError, TypeError):
            return None

    # --- Deduplication ---

    def deduplicate_list(self, items: List[Any], key: Optional[str] = None) -> List[Any]:
        """
        Remove duplicates from a list while preserving order.
        
        Args:
            items: Input list.
            key: Optional key to use for deduplication (e.g., 'id' for dicts).
                 If None, uses the item itself.
            
        Returns:
            Deduplicated list.
        """
        if not items:
            return []
        
        seen = set()
        deduplicated = []
        
        for item in items:
            if key:
                # Use the specified key
                if isinstance(item, dict):
                    k = item.get(key)
                else:
                    k = getattr(item, key, None)
                
                if k is None:
                    # Fall back to JSON serialization
                    k = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else item
            else:
                # Use the item itself
                k = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else item
            
            if k not in seen:
                seen.add(k)
                deduplicated.append(item)
        
        return deduplicated

    def deduplicate_dicts(self, dicts: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
        """
        Remove duplicate dictionaries from a list based on a key.
        
        Args:
            dicts: List of dictionaries.
            key: Key to use for deduplication.
            
        Returns:
            Deduplicated list of dictionaries.
        """
        if not dicts:
            return []
        
        seen = set()
        deduplicated = []
        
        for d in dicts:
            k = d.get(key)
            if k not in seen:
                seen.add(k)
                deduplicated.append(d)
        
        return deduplicated

    # --- Validation ---

    def is_valid_email(self, email: str) -> bool:
        """
        Validate an email address.
        
        Args:
            email: Email address to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        if not email:
            return False
        
        # Simple regex for email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def is_valid_url(self, url: str) -> bool:
        """
        Validate a URL.
        
        Args:
            url: URL to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        if not url:
            return False
        
        # Simple regex for URL validation
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url, re.IGNORECASE))

    def is_valid_phone(self, phone: str) -> bool:
        """
        Validate a phone number.
        
        Args:
            phone: Phone number to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        if not phone:
            return False
        
        # Remove all non-digit characters
        digits = re.sub(r'[^\d]', '', phone)
        
        # Check length (minimum 7 digits for local numbers)
        if len(digits) < 7:
            return False
        
        return True

    # --- Batch Normalization ---

    def normalize_batch(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize a batch of data (e.g., scraped posts).
        
        Args:
            data: List of dictionaries to normalize.
            
        Returns:
            List of normalized dictionaries.
        """
        normalized = []
        
        for item in data:
            normalized_item = {}
            
            for key, value in item.items():
                if isinstance(value, str):
                    # Normalize text fields
                    if key in ['text', 'content', 'caption', 'bio', 'description']:
                        normalized_item[key] = self.normalize_text(value)
                    elif key in ['email', 'url']:
                        normalized_item[key] = self.normalize_email(value) if key == 'email' else self.normalize_url(value)
                    elif key in ['phone', 'telephone']:
                        normalized_item[key] = self.normalize_phone(value)
                    elif key in ['hashtag', 'hashtags']:
                        if isinstance(value, list):
                            normalized_item[key] = [self.normalize_hashtag(h) for h in value]
                        else:
                            normalized_item[key] = self.normalize_hashtag(value)
                    elif key in ['mention', 'mentions']:
                        if isinstance(value, list):
                            normalized_item[key] = [self.normalize_mention(m) for m in value]
                        else:
                            normalized_item[key] = self.normalize_mention(value)
                    else:
                        normalized_item[key] = value
                elif isinstance(value, (int, float, bool)):
                    normalized_item[key] = value
                elif isinstance(value, list):
                    normalized_item[key] = [self.normalize_batch([v])[0] if isinstance(v, dict) else v for v in value]
                elif isinstance(value, dict):
                    normalized_item[key] = self.normalize_batch([value])[0]
                else:
                    normalized_item[key] = value
            
            normalized.append(normalized_item)
        
        return normalized


# Singleton instance for easy use
normalizer = DataNormalizer()
