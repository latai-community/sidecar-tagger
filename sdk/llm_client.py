import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from sdk.models.metadata import FileMetadata

load_dotenv()

class LLMClient:
    """Handles communication with the LLM provider."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in environment.")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)

    def generate_metadata(self, content: str) -> FileMetadata:
        """Sends content to the LLM and returns validated FileMetadata."""
        if not self.api_key:
            return self._get_fallback_metadata("API Key missing")

        prompt = f"""
        Analyze the following document content and extract structured metadata.
        You MUST return a valid JSON object matching this schema:
        {{
            "doc_type": "string (e.g., invoice, report, contract, manual)",
            "language": "string (ISO 639-1 code, e.g., 'en', 'es')",
            "domain": "string (e.g., Finance, Tech, Legal, Health)",
            "category": "string (e.g., business_document, technical_spec, internal_memo)",
            "context": "string (one-sentence summary of what the document is about)",
            "tags": ["array", "of", "keywords"],
            "content_date": "ISO-8601 string (if found, otherwise null)",
            "confidence": 0.0 (float between 0 and 1)
        }}

        Content to analyze:
        {content[:5000]}  # Truncate to avoid context window issues
        """

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Parse the JSON response
            data = json.loads(response.text)
            
            # Validate with Pydantic
            return FileMetadata(**data)
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return self._get_fallback_metadata(str(e))

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
