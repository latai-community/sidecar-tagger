import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
from sdk.models.metadata import FileMetadata

load_dotenv(override=True)

class LLMClient:
    """Handles communication with the LLM provider."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in environment.")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)

    def generate_metadata(self, content: str, image_path: str = None, pdf_path: str = None, retries=3) -> FileMetadata:
        """Sends content (and optionally an image or PDF) to the LLM and returns validated FileMetadata."""
        if not self.api_key:
            return self._get_fallback_metadata("API Key missing")

        prompt = f"""
        Analyze the following document content and extract structured metadata.
        If an image or PDF file is provided, use it as the primary source of truth (especially for scanned or visual documents).
        Focus on extracting tags based on the actual content, topics, and visual elements.
        
        You MUST return a valid JSON object matching this schema:
        {{
            "doc_type": "string (e.g., invoice, report, contract, manual, cookbook, textbook)",
            "language": "string (ISO 639-1 code, e.g., 'en', 'es')",
            "domain": "string (e.g., Finance, Tech, Legal, Health, Gastronomy)",
            "category": "string (e.g., business_document, technical_spec, internal_memo, recipes)",
            "context": "string (one-sentence summary of what the document is about)",
            "tags": ["array", "of", "keywords"],
            "content_date": "ISO-8601 string (if found, otherwise null)",
            "confidence": 0.0 (float between 0 and 1)
        }}

        Extracted textual content (may be empty if scanned):
        {content[:3000]}
        """

        # Prepare multimodal parts
        parts = [prompt]
        
        # Handle PDF upload (Native Gemini PDF support)
        if pdf_path and os.path.exists(pdf_path):
            try:
                print(f"Uploading PDF to Gemini for visual analysis: {os.path.basename(pdf_path)}...")
                uploaded_file = genai.upload_file(path=pdf_path, display_name=os.path.basename(pdf_path))
                parts.append(uploaded_file)
            except Exception as e:
                print(f"Warning: Could not upload PDF to Gemini: {e}")
        
        # Handle Image fallback/standalone
        elif image_path and os.path.exists(image_path):
            try:
                from PIL import Image
                img = Image.open(image_path)
                parts.append(img)
            except Exception as e:
                print(f"Warning: Could not load image for LLM: {e}")

        for attempt in range(retries):
            try:
                response = self.model.generate_content(
                    parts,
                    generation_config={"response_mime_type": "application/json"}
                )

                # Parse and Validate
                data = json.loads(response.text)
                return FileMetadata(**data)

            except Exception as e:
                if "429" in str(e) and attempt < retries - 1:
                    wait_time = (attempt + 1) * 15
                    print(f"Rate limit reached. Waiting {wait_time}s... (Attempt {attempt + 1}/{retries})")
                    time.sleep(wait_time)
                    continue

                print(f"Error calling LLM on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    return self._get_fallback_metadata(str(e))

        return self._get_fallback_metadata("Max retries reached")


    def _get_fallback_metadata(self, error_msg: str) -> FileMetadata:
        """Returns a default metadata object when LLM fails."""
        from datetime import datetime
        return FileMetadata(
            doc_type="unknown",
            language="unknown",
            domain="unknown",
            category="unknown",
            context=f"Error: {error_msg}",
            tags=["error"],
            content_date=None,
            confidence=0.0
        )
