from PIL import Image
from PIL.ExifTags import TAGS
import os

def extract_image_metadata(file_path: str) -> str:
    """
    Extracts basic image metadata (dimensions, format, mode) 
    and EXIF data if available.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    summary_parts = []
    try:
        with Image.open(file_path) as img:
            summary_parts.append(f"Image Format: {img.format}")
            summary_parts.append(f"Image Mode: {img.mode}")
            summary_parts.append(f"Dimensions: {img.width}x{img.height}")
            
            # Extract EXIF if it exists (for JPEGs)
            exif_data = img.getexif()
            if exif_data:
                exif_summary = []
                for tag_id in exif_data:
                    tag = TAGS.get(tag_id, tag_id)
                    data = exif_data.get(tag_id)
                    # Limit EXIF data to avoid huge output (ignore binary or very long strings)
                    if isinstance(data, (str, int, float)) and len(str(data)) < 100:
                        exif_summary.append(f"{tag}: {data}")
                
                if exif_summary:
                    summary_parts.append("EXIF Data:")
                    summary_parts.extend(exif_summary[:10]) # Top 10 tags
                    
        return "\n".join(summary_parts)
    except Exception as e:
        return f"Error parsing image: {str(e)}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(extract_image_metadata(sys.argv[1]))
    else:
        print("Usage: python image_parser.py <path_to_image>")
