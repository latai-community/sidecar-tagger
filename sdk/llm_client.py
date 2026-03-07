"""
Title: LLM Client
Abstract: Handles communication with the LLM provider (Gemini).
Why: Manages prompts, context injection, and API/multimodal communication.
Dependencies: google.generativeai, json, logging, sdk.models.metadata
"""

import os
import json
import time
import logging
import google.generativeai as genai
from typing import Optional, List, Dict
from dotenv import load_dotenv

from sdk.models.metadata import FileMetadata, LocalContext, ClusterHint
from sdk.exceptions import LLMClientError

load_dotenv(override=True)
logger = logging.getLogger("LLMClient")

class LLMClient:
    """Handles communication with the LLM provider."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment.")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)

    def generate_metadata(
        self, 
        content: str, 
        image_path: Optional[str] = None, 
        pdf_path: Optional[str] = None,
        local_context: Optional[LocalContext] = None,
        cluster_hint: Optional[ClusterHint] = None,
        retries: int = 3
    ) -> FileMetadata:
        """
        Layer 4: Cognitive Analysis with Context Injection.
        """
        if not self.api_key:
            return self._get_fallback_metadata("API Key missing")

        # --- Construct the Super Prompt (Context Injection) ---
        context_block = ""
        if local_context:
            context_block += f"""
            SYSTEM CONTEXT (Objective Facts):
            - Filename: {local_context.filename}
            - Path Keywords: {', '.join(local_context.path_keywords)}
            - Creation Year: {local_context.creation_date[:4] if local_context.creation_date else 'Unknown'}
            - Owner: {local_context.owner}
            """
        
        hint_block = ""
        if cluster_hint and cluster_hint.similarity_score > 0.7:
             hint_block += f"""
            NEIGHBORHOOD HINTS (Collective Intelligence):
            - This file is similar to others in the same folder.
            - Suggested Category: {cluster_hint.suggested_category}
            - Suggested Tags: {', '.join(cluster_hint.suggested_tags)}
            - Anomaly Status: {'Likely Anomaly' if cluster_hint.is_anomaly else 'Consistent with group'}
            """

        prompt = f"""
        Analyze the following document content and extract structured metadata.
        
        {context_block}
        {hint_block}

        CRITICAL INSTRUCTIONS:
        1. Use the 'SYSTEM CONTEXT' to ground your analysis (e.g., if path says 'Invoices', bias towards financial documents).
        2. Use 'NEIGHBORHOOD HINTS' as a strong suggestion, but override if the content clearly contradicts them.
        3. Extract domain, category, context, and tags.
        
        You MUST return a valid JSON object matching the FileMetadata schema.
        
        Extracted Content:
        {content[:4000]}
        """

        # Prepare multimodal parts
        parts = [prompt]
        
        if pdf_path and os.path.exists(pdf_path):
            try:
                logger.info(f"Uploading PDF for visual analysis: {os.path.basename(pdf_path)}...")
                uploaded_file = genai.upload_file(path=pdf_path, display_name=os.path.basename(pdf_path))
                parts.append(uploaded_file)
            except Exception as e:
                logger.warning(f"Could not upload PDF to Gemini: {e}")
        
        elif image_path and os.path.exists(image_path):
            try:
                from PIL import Image
                img = Image.open(image_path)
                parts.append(img)
            except Exception as e:
                logger.warning(f"Could not load image for LLM: {e}")

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
                    wait_time = (attempt + 1) * 10
                    logger.warning(f"Rate limit. Waiting {wait_time}s... (Attempt {attempt + 1}/{retries})")
                    time.sleep(wait_time)
                    continue

                logger.error(f"LLM Error on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    return self._get_fallback_metadata(str(e))

        return self._get_fallback_metadata("Max retries reached")

    def _get_fallback_metadata(self, error_msg: str) -> FileMetadata:
        """Returns a default metadata object when LLM fails."""
        return FileMetadata(
            doc_type="unknown",
            context=f"Metadata extraction failed: {error_msg}",
            tags=["error"],
            confidence=0.0,
            needs_review=True
        )
