import os
import json
from datetime import datetime

class MetadataProcessor:
    """Core SDK processor for metadata extraction."""

    def __init__(self, output_path="sidecar.json"):
        self.output_path = output_path
        self.metadata_store = {}

    def extract_metadata(self, file_path):
        """Mock extraction logic to fulfill the prompt."""
        # In a real scenario, this would call format-specific parsers and an LLM.
        filename = os.path.basename(file_path)
        
        # Mocking the SDK schema
        metadata = {
            "doc_type": "document",
            "language": "en",
            "domain": "unknown",
            "category": "general",
            "context": f"Content extracted from {filename}",
            "tags": ["tag1", "tag2"],
            "date_detected": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.9
        }
        
        return metadata

    def process_files(self, file_paths):
        """Processes multiple files and saves them into a consolidated sidecar.json."""
        for path in file_paths:
            if os.path.isfile(path):
                self.metadata_store[path] = self.extract_metadata(path)
            else:
                print(f"Warning: File {path} not found.")

        self.save_sidecar()

    def save_sidecar(self):
        """Writes the consolidated metadata store to disk."""
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata_store, f, indent=4)
        print(f"Successfully generated {self.output_path}")
