"""
Title: ExifTool Client
Abstract: Wrapper for ExifTool command-line interface to extract native metadata.
Why: ExifTool is the industry standard for extracting metadata from 25k+ file formats.
Dependencies: subprocess, json, logging, platform
License: Artistic License 2.0 (see LICENSE-EXIFTOOL)
"""
import subprocess
import json
import logging
import os
import platform
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger("ExifToolClient")

EXIFTOOL_CMD = "exiftool"

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg", ".json", ".txt", ".md"}


def _get_install_hint() -> str:
    """Return OS-specific install command for ExifTool."""
    system = platform.system()
    if system == "Windows":
        return "Install with: winget install exiftool"
    elif system == "Darwin":
        return "Install with: brew install exiftool"
    else:
        return "Install with: sudo apt-get install -y libimage-exiftool-perl"


class ExifToolClient:
    """
    Client for ExifTool CLI.
    Extracts native metadata (author, title, keywords, etc.) from files.
    """
    
    def __init__(self):
        self._available = self._verify_exiftool()
    
    def _verify_exiftool(self) -> bool:
        """Check if exiftool is installed."""
        try:
            result = subprocess.run(
                [EXIFTOOL_CMD, "-ver"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"ExifTool available: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            logger.warning(f"ExifTool not found in PATH. {_get_install_hint()}")
        except Exception as e:
            logger.warning(f"ExifTool verification failed: {e}")
        return False
    
    def is_available(self) -> bool:
        """Check if exiftool is available."""
        return self._available
    
    def extract(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract all metadata as a dictionary.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary of metadata or None if extraction failed
        """
        if not self._available:
            return None
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return None
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            logger.debug(f"Unsupported extension: {ext}")
            return None
        
        try:
            cmd = [
                EXIFTOOL_CMD,
                "-j",  # JSON output
                "-G",  # Group names
                file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.debug(f"ExifTool returned non-zero: {result.stderr}")
                return None
            
            try:
                data = json.loads(result.stdout)
                if data and len(data) > 0:
                    return data[0]
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse ExifTool JSON: {e}")
            
            return None
            
        except subprocess.TimeoutExpired:
            logger.warning(f"ExifTool timed out for: {file_path}")
            return None
        except Exception as e:
            logger.warning(f"ExifTool extraction failed: {e}")
            return None
    
    def extract_tags(self, file_path: str, tags: List[str]) -> Optional[Dict[str, Any]]:
        """
        Extract only specific tags.
        
        Args:
            file_path: Path to the file
            tags: List of tag names to extract
            
        Returns:
            Dictionary of requested tags or None if extraction failed
        """
        if not self._available:
            return None
        
        try:
            cmd = [
                EXIFTOOL_CMD,
                "-j",
                "-G",
                *[f"-{tag}" for tag in tags],
                file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            try:
                data = json.loads(result.stdout)
                if data and len(data) > 0:
                    return data[0]
            except json.JSONDecodeError:
                pass
            
            return None
            
        except Exception:
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    client = ExifToolClient()
    if client.is_available():
        print("ExifTool is available!")
        
        test_file = "test-files/test-doc.pdf"
        if os.path.exists(test_file):
            metadata = client.extract(test_file)
            if metadata:
                print(f"Metadata keys: {list(metadata.keys())[:10]}")
    else:
        print("ExifTool is NOT available. " + _get_install_hint())
