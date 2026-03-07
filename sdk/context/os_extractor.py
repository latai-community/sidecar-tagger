"""
Title: OS Context Extractor (Layer 1)
Abstract: Extracts factual metadata from the operating system (dates, owner, path).
Why: Grounding AI analysis in objective facts reduces hallucinations.
Dependencies: os, datetime, platform, pathlib
"""
import os
import datetime
import platform
import re
from pathlib import Path
from typing import List, Optional, Dict
from sdk.models.metadata import LocalContext

class OSContextExtractor:
    """
    Algorithmic extractor for Layer 1 context.
    Does not use AI, only OS system calls.
    """
    
    def extract(self, file_path: str) -> LocalContext:
        """
        Builds a LocalContext object from the file's system properties.
        """
        path_obj = Path(file_path).resolve()
        stat = path_obj.stat()
        
        # 1. Dates
        creation_ts = stat.st_ctime
        mod_ts = stat.st_mtime
        
        # 2. Owner (Platform dependent)
        owner = self._get_file_owner(path_obj)
        
        # 3. Path Analysis
        parent_folder = path_obj.parent.name
        keywords = self._extract_path_keywords(path_obj)
        
        return LocalContext(
            filename=path_obj.name,
            file_extension=path_obj.suffix.lower(),
            file_size_bytes=stat.st_size,
            creation_date=datetime.datetime.fromtimestamp(creation_ts).isoformat(),
            modification_date=datetime.datetime.fromtimestamp(mod_ts).isoformat(),
            owner=owner,
            parent_folder=parent_folder,
            path_keywords=keywords,
            internal_props={} # Placeholder for future deep property extraction
        )

    def _get_file_owner(self, path: Path) -> str:
        """Robust owner extraction working on both Windows and Linux."""
        try:
            if platform.system() == 'Windows':
                # On Windows, owner extraction is complex/slow via standard libs
                # We return a generic placeholder or try win32 APIs if available
                # For simplicity in this v2 MVP, we skip deep ACL inspection
                return "system_user" 
            else:
                import pwd
                return pwd.getpwuid(path.stat().st_uid).pw_name
        except Exception:
            return "unknown"

    def _extract_path_keywords(self, path: Path) -> List[str]:
        """
        Extracts significant tokens from the full file path.
        Example: /Projects/2023/Covid/Vaccine.pdf -> ['Projects', '2023', 'Covid']
        """
        parts = list(path.parent.parts)
        # Filter out root drive (C:\) or root (/) and generic 'Users' folders if possible
        keywords = [p for p in parts if len(p) > 2 and p not in ["Users", "Documents", "Desktop"]]
        
        # Limit to last 3 levels to avoid noise from deep hierarchies
        return keywords[-3:]

if __name__ == "__main__":
    # Test on self
    extractor = OSContextExtractor()
    context = extractor.extract(__file__)
    print(context.model_dump_json(indent=2))
