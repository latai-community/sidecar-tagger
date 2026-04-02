"""
Title: Tag Mapper
Abstract: Maps ExifTool raw tags to internal metadata format.
Why: Normalizes metadata across different file formats.
"""
from typing import Dict, Any, Optional

TAG_MAPPING: Dict[str, Dict[str, str]] = {
    ".pdf": {
        "Title": "title",
        "Author": "author",
        "Subject": "subject",
        "Keywords": "keywords",
        "Creator": "creator",
        "Producer": "producer",
        "CreateDate": "create_date",
        "ModDate": "mod_date",
    },
    ".docx": {
        "Title": "title",
        "Author": "author",
        "Subject": "subject",
        "Keywords": "keywords",
        "Creator": "creator",
        "LastModifiedBy": "last_modified_by",
    },
    ".xlsx": {
        "Title": "title",
        "Author": "author",
        "Subject": "subject",
        "Comments": "comments",
        "Creator": "creator",
        "LastAuthor": "last_author",
    },
    ".png": {
        "DateTimeOriginal": "date",
        "Make": "camera_make",
        "Model": "camera_model",
        "GPSLatitude": "gps_lat",
        "GPSLongitude": "gps_lon",
        "ImageWidth": "width",
        "ImageHeight": "height",
    },
    ".jpg": {
        "DateTimeOriginal": "date",
        "Make": "camera_make",
        "Model": "camera_model",
        "GPSLatitude": "gps_lat",
        "GPSLongitude": "gps_lon",
        "ImageWidth": "width",
        "ImageHeight": "height",
    },
    ".jpeg": {
        "DateTimeOriginal": "date",
        "Make": "camera_make",
        "Model": "camera_model",
        "GPSLatitude": "gps_lat",
        "GPSLongitude": "gps_lon",
    },
    ".txt": {
        "Title": "title",
    },
    ".md": {
        "Title": "title",
    },
    ".json": {
        "title": "title",
        "author": "author",
        "description": "description",
    },
}

GROUPS_TO_TRY = ["", "EXIF", "IPTC", "XMP", "PDF", "PNG", "JFIF"]


def map_tags(raw_metadata: Dict[str, Any], extension: str) -> Dict[str, Any]:
    """
    Map raw ExifTool tags to internal format.
    
    Args:
        raw_metadata: Raw metadata from ExifTool
        extension: File extension (e.g., ".pdf")
        
    Returns:
        Mapped metadata dictionary
    """
    if not raw_metadata:
        return {}
    
    extension = extension.lower()
    mapping = TAG_MAPPING.get(extension, {})
    
    result = {}
    for exif_key, internal_key in mapping.items():
        value = _find_tag(raw_metadata, exif_key)
        if value is not None:
            result[internal_key] = _normalize_value(value)
    
    return result


def _normalize_value(value: Any) -> Any:
    """Convert lists to comma-separated strings."""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return value


def _find_tag(metadata: Dict[str, Any], tag_name: str) -> Optional[Any]:
    """
    Find a tag across different EXIF groups.
    
    ExifTool returns tags with group prefixes like "EXIF:DateTimeOriginal"
    or just "DateTimeOriginal".
    """
    for group in GROUPS_TO_TRY:
        if group:
            full_key = f"{group}:{tag_name}"
        else:
            full_key = tag_name
        
        if full_key in metadata and metadata[full_key]:
            return metadata[full_key]
    
    return None


def get_supported_extensions() -> set:
    """Return set of supported file extensions."""
    return set(TAG_MAPPING.keys())


if __name__ == "__main__":
    test_raw = {
        "Title": "Test Document",
        "Author": "John Doe",
        "PDF:Keywords": "test,document,pdf",
        "EXIF:DateTimeOriginal": "2024:01:15 10:30:00",
    }
    
    result = map_tags(test_raw, ".pdf")
    print(f"Mapped: {result}")
