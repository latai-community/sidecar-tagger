import os
import json
from datetime import datetime

from sdk.models.metadata import FileMetadata

class MetadataProcessor:
    """Core SDK processor for metadata extraction."""

    def __init__(self, output_path="sidecar.json"):
        self.output_path = output_path
        self.metadata_store = {}

    def extract_metadata(self, file_path: str) -> dict:
        """Mock extraction logic to fulfill the prompt."""
        # In a real scenario, this would call format-specific parsers and an LLM.
        filename = os.path.basename(file_path)
        
        # Creating a FileMetadata instance for validation
        metadata = FileMetadata(
            doc_type="document",
            language="en",
            domain="unknown",
            category="general",
            context=f"Content extracted from {filename}",
            tags=["tag1", "tag2"],
            content_date=datetime.now(), # Mocked as today for now
            confidence=0.9
        )
        
        # We use mode='json' to ensure that datetime and other types are serialized to strings
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
