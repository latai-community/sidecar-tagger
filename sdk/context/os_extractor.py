"""
Title: OS Context Extractor (Layer 1)
Abstract: Extracts factual metadata from the operating system AND native file metadata.
Why: Grounding AI analysis in objective facts reduces hallucinations.
Dependencies: os, datetime, platform, pathlib, sdk.native_metadata
"""
import os
import datetime
import platform
from pathlib import Path
from typing import List, Optional, Dict, Any
from sdk.models.metadata import LocalContext

from sdk.native_metadata.exiftool_client import ExifToolClient
from sdk.native_metadata.tag_mapper import map_tags
from sdk.native_metadata.confidence import calculate_confidence


class OSContextExtractor:
    """
    Layer 1: Native + OS Metadata Extractor.
    
    Combines:
    - OS metadata: filename, path, size, dates, owner
    - Native metadata: author, title, keywords (via ExifTool)
    """
    
    def __init__(self):
        self._exiftool = ExifToolClient()
    
    @property
    def exiftool_available(self) -> bool:
        """Check if ExifTool is available."""
        return self._exiftool.is_available()
    
    def extract(self, file_path: str) -> LocalContext:
        """
        Builds a LocalContext object from OS and native metadata.
        
        Args:
            file_path: Path to the file
            
        Returns:
            LocalContext with OS + native metadata
        """
        path_obj = Path(file_path).resolve()
        stat = path_obj.stat()
        
        creation_ts = stat.st_ctime
        mod_ts = stat.st_mtime
        
        owner = self._get_file_owner(path_obj)
        
        parent_folder = path_obj.name
        keywords = self._extract_path_keywords(path_obj)
        
        native_metadata = self._extract_native_metadata(file_path)
        
        confidence = calculate_confidence(native_metadata)
        
        return LocalContext(
            filename=path_obj.name,
            file_extension=path_obj.suffix.lower(),
            file_size_bytes=stat.st_size,
            creation_date=datetime.datetime.fromtimestamp(creation_ts).isoformat(),
            modification_date=datetime.datetime.fromtimestamp(mod_ts).isoformat(),
            owner=owner,
            parent_folder=parent_folder,
            path_keywords=keywords,
            internal_props=native_metadata
        )
    
    def _extract_native_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract native metadata using ExifTool.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Mapped native metadata or empty dict
        """
        if not self._exiftool.is_available():
            return {}
        
        ext = Path(file_path).suffix.lower()
        raw_metadata = self._exiftool.extract(file_path)
        
        if not raw_metadata:
            return {}
        
        mapped = map_tags(raw_metadata, ext)
        
        return mapped
    
    def get_confidence(self, file_path: str) -> float:
        """
        Get confidence score for a file without full extraction.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Confidence score 0.0 - 1.0
        """
        native_metadata = self._extract_native_metadata(file_path)
        return calculate_confidence(native_metadata)
    
    def _get_file_owner(self, path: Path) -> str:
        """Robust owner extraction working on both Windows and Linux."""
        try:
            if platform.system() == 'Windows':
                return "system_user" 
            else:
                import pwd
                return pwd.getpwuid(path.stat().st_uid).pw_name
        except ImportError:
            return "unknown"
        except Exception:
            return "unknown"
    
    def _extract_path_keywords(self, path: Path) -> List[str]:
        """
        Extracts significant tokens from the full file path.
        Example: /Projects/2023/Covid/Vaccine.pdf -> ['Projects', '2023', 'Covid']
        """
        parts = list(path.parent.parts)
        keywords = [p for p in parts if len(p) > 2 and p not in ["Users", "Documents", "Desktop"]]
        
        return keywords[-3:]


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    extractor = OSContextExtractor()
    
    print(f"ExifTool available: {extractor.exiftool_available}")
    
    test_file = "test-files/test-doc.pdf"
    if os.path.exists(test_file):
        context = extractor.extract(test_file)
        print(context.model_dump_json(indent=2))
