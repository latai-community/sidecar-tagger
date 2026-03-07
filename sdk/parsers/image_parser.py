"""
Title: Image Parser
Abstract: Extracts metadata and EXIF data from images (PNG, JPEG, etc.).
Why: Provides technical context about images to the LLM, enabling better classification and tagging.
Dependencies: PIL, os, logging, sdk.parsers.base_parser, sdk.exceptions
"""

import os
import logging
from typing import Dict, Any, List
from PIL import Image
from PIL.ExifTags import TAGS
from sdk.parsers.base_parser import BaseParser
from sdk.exceptions import ParserError

logger = logging.getLogger(__name__)

class ImageParser(BaseParser):
    """
    Parser for Image files.
    Follows Pillar 1 (Strict Typing) and Pillar 2 (Interface-Driven).
    """

    def extract(self, file_path: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Extracts content from an image file.
        
        Args:
            file_path: Path to the image file.
            **kwargs: None currently.
            
        Returns:
            Dict[str, Any]: {'text': str, 'thumbnail_path': str}
            
        Raises:
            ParserError: If extraction fails.
        """
        self._validate_file(file_path)

        try:
            with Image.open(file_path) as img:
                metadata_text = self._extract_metadata(img)
                return {
                    "text": metadata_text,
                    "thumbnail_path": file_path  # The image itself is the thumbnail
                }
        except Exception as e:
            logger.error(f"Failed to extract image from {file_path}: {e}")
            raise ParserError(f"Error parsing image: {e}") from e

    def _validate_file(self, file_path: str) -> None:
        """Validates file existence."""
        if not os.path.exists(file_path):
            raise ParserError(f"Image file not found: {file_path}")

    def _extract_metadata(self, img: Image.Image) -> str:
        """Summarizes image properties and EXIF data."""
        summary = [
            f"Image Format: {img.format}",
            f"Image Mode: {img.mode}",
            f"Dimensions: {img.width}x{img.height}"
        ]
        
        exif = self._get_exif_summary(img)
        if exif:
            summary.append("EXIF Data:")
            summary.extend(exif)
            
        return "\n".join(summary)

    def _get_exif_summary(self, img: Image.Image) -> List[str]:
        """Extracts a subset of readable EXIF tags."""
        exif_data = img.getexif()
        if not exif_data:
            return []
            
        summary = []
        for tag_id in exif_data:
            tag = TAGS.get(tag_id, tag_id)
            data = exif_data.get(tag_id)
            if self._is_readable(data):
                summary.append(f"{tag}: {data}")
                
        return summary[:10]

    def _is_readable(self, data: Any) -> bool:
        """Checks if EXIF data is a short readable string or number."""
        return isinstance(data, (str, int, float)) and len(str(data)) < 100

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    parser = ImageParser()
    print("ImageParser initialized. Call extract(file_path) to use.")
