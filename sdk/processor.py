import os
import json
from datetime import datetime

from sdk.models.metadata import FileMetadata
from sdk.parsers.pdf_parser import extract_pdf_content
from sdk.parsers.xlsx_parser import extract_xlsx_content
from sdk.parsers.image_parser import extract_image_metadata
from sdk.llm_client import LLMClient
from sdk.embeddings_client import LocalEmbeddings

class MetadataProcessor:
    """Core SDK processor with Semantic Cache (Embedding First) logic."""

    def __init__(self, output_path="sidecar.json", similarity_threshold=0.9):
        self.output_path = output_path
        self.similarity_threshold = similarity_threshold
        self.metadata_store = self._load_existing_store()
        self.llm_client = LLMClient()
        self.embeddings_client = LocalEmbeddings()

    def _load_existing_store(self) -> dict:
        """Loads the existing metadata store from disk if it exists."""
        if os.path.exists(self.output_path):
            try:
                with open(self.output_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load existing sidecar: {e}")
        return {}

    def _find_similar_metadata(self, current_vector: list) -> dict:
        """Searches the store for a vector with high similarity (> threshold)."""
        for path, metadata in self.metadata_store.items():
            stored_vector = metadata.get("embedding_vector")
            if stored_vector:
                similarity = self.embeddings_client.calculate_similarity(current_vector, stored_vector)
                if similarity >= self.similarity_threshold:
                    # Found a semantic match!
                    print(f" -> Semantic Cache Hit! (Similarity: {similarity:.2f})")
                    # We return a copy but update the confidence to reflect similarity
                    cached_metadata = metadata.copy()
                    cached_metadata["confidence"] = similarity
                    return cached_metadata
        return None

    def extract_metadata(self, file_path: str) -> dict:
        """Calls parsers, generates embedding, and decides whether to use LLM or Cache."""
        filename = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        content = ""
        image_to_send = None
        
        if ext == ".pdf":
            # PDF returns a dict with text and thumbnail_path
            pdf_data = extract_pdf_content(file_path)
            content = pdf_data["text"]
            image_to_send = pdf_data["thumbnail_path"]
        elif ext in [".xlsx", ".xls"]:
            content = extract_xlsx_content(file_path)
        elif ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
            # For standalone images, the image itself is the primary content
            content = extract_image_metadata(file_path) # Get technical info
            image_to_send = file_path # Send the image to Gemini
        else:
            content = f"Generic content for {filename}"
        
        # 1. Generate local vector FIRST (Semantic Cache step)
        # Note: If no text is found, we use a descriptive placeholder to generate a vector
        vector_content = content if content.strip() else f"Image-based document: {filename}"
        print(f"Generating identity vector for {filename}...")
        vector = self.embeddings_client.generate_vector(vector_content)

        # 2. Check for matches in our local memory
        cached_metadata = self._find_similar_metadata(vector)
        if cached_metadata:
            # Clean up temporary thumbnail if it was created
            if image_to_send and ext == ".pdf":
                try: os.remove(image_to_send)
                except: pass
            return cached_metadata

        # 3. Cache miss: Call the LLM
        print(f" -> Cache Miss. Consulting {self.llm_client.model_name} for {filename}...")
        
        # We pass pdf_path if it's a PDF to allow native multimodal analysis
        pdf_to_send = file_path if ext == ".pdf" else None
        metadata = self.llm_client.generate_metadata(content, image_path=image_to_send, pdf_path=pdf_to_send)
        
        # 4. Attach the vector and return
        metadata_dict = metadata.model_dump(mode='json')
        metadata_dict["embedding_vector"] = vector

        # Cleanup temporary PDF thumbnail
        if image_to_send and ext == ".pdf":
            try: os.remove(image_to_send)
            except: pass
        
        return metadata_dict

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
