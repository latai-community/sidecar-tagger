import os
import json
from datetime import datetime

from sdk.models.metadata import FileMetadata
from sdk.parsers.pdf_parser import extract_pdf_content
from sdk.parsers.xlsx_parser import extract_xlsx_content
from sdk.parsers.image_parser import extract_image_metadata
from sdk.llm_client import LLMClient

class MetadataProcessor:
    """Core SDK processor for metadata extraction."""

    def __init__(self, output_path="sidecar.json"):
        self.output_path = output_path
        self.metadata_store = {}
        self.llm_client = LLMClient()

    def extract_metadata(self, file_path: str) -> dict:
        """Calls format-specific parsers and uses an LLM for intelligence."""
        filename = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        content = ""
        
        if ext == ".pdf":
            content = extract_pdf_content(file_path)
        elif ext in [".xlsx", ".xls"]:
            content = extract_xlsx_content(file_path)
        elif ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
            content = str(extract_image_metadata(file_path))
        else:
            content = f"Generic content for {filename}"
        
        # Use LLM to generate intelligent metadata
        metadata = self.llm_client.generate_metadata(content)
        
        return metadata.model_dump(mode='json')

    def process_files(self, file_paths):
        """Processes multiple files and saves them into a consolidated sidecar.json."""
        for path in file_paths:
            if os.path.isfile(path):
                # We store the dictionary representation for JSON serialization
                self.metadata_store[path] = self.extract_metadata(path)
            else:
                print(f"Warning: File {path} not found.")

        self.save_sidecar()

    def save_sidecar(self):
        """Writes the consolidated metadata store to disk."""
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata_store, f, indent=4)
        print(f"Successfully generated {self.output_path}")
