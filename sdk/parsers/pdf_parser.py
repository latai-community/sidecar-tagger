"""
Title: PDF Parser
Abstract: Extracts text and thumbnails from PDF documents.
Why: Enables processing of complex document layouts by providing both text and visual context (thumbnails).
Dependencies: pdfplumber, PIL, os, tempfile, logging, sdk.parsers.base_parser, sdk.exceptions
"""

import os
import tempfile
import logging
from typing import Dict, Any, List, Set
import pdfplumber
from sdk.parsers.base_parser import BaseParser
from sdk.exceptions import ParserError

logger = logging.getLogger(__name__)

class PdfParser(BaseParser):
    """
    Parser for PDF files.
    Follows Pillar 1 (Strict Typing) and Pillar 2 (Interface-Driven).
    """

    def extract(self, file_path: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Extracts content from a PDF file.
        
        Args:
            file_path: Path to the .pdf file.
            **kwargs: resolution (default 150).
            
        Returns:
            Dict[str, Any]: {'text': str, 'thumbnail_path': Optional[str]}
            
        Raises:
            ParserError: If extraction fails.
        """
        self._validate_file(file_path)
        resolution = kwargs.get("resolution", 150)

        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                thumbnail_path = self._generate_thumbnail(pdf, file_path, resolution)
                text = self._extract_text_samples(pdf, total_pages)
                
                return {
                    "text": text,
                    "thumbnail_path": thumbnail_path
                }
        except Exception as e:
            logger.error(f"Failed to extract PDF from {file_path}: {e}")
            raise ParserError(f"Error parsing PDF: {e}") from e

    def _validate_file(self, file_path: str) -> None:
        """Validates file existence."""
        if not os.path.exists(file_path):
            raise ParserError(f"PDF file not found: {file_path}")

    def _generate_thumbnail(self, pdf: pdfplumber.PDF, file_path: str, resolution: int) -> str:
        """Generates a representative thumbnail from the PDF."""
        temp_dir = tempfile.gettempdir()
        pages_to_check = [0, 1, 2, 4, 9]
        total_pages = len(pdf.pages)
        
        for p_idx in pages_to_check:
            if p_idx < total_pages:
                page = pdf.pages[p_idx]
                img = page.to_image(resolution=72).original
                if img.convert("L").getextrema() != (255, 255):
                    return self._save_thumbnail(page, p_idx, file_path, resolution, temp_dir)
        
        if total_pages > 0:
            return self._save_thumbnail(pdf.pages[0], 0, file_path, resolution, temp_dir, fallback=True)
        return ""

    def _save_thumbnail(self, page: Any, p_idx: int, file_path: str, res: int, temp_dir: str, fallback: bool = False) -> str:
        """Saves the page as an image file."""
        prefix = "thumb_0_fallback" if fallback else f"thumb_{p_idx}"
        thumb_path = os.path.join(temp_dir, f"{prefix}_{os.path.basename(file_path)}.png")
        page.to_image(resolution=res).original.save(thumb_path)
        return thumb_path

    def _extract_text_samples(self, pdf: pdfplumber.PDF, total_pages: int) -> str:
        """Extracts text from a sample of pages to stay within token limits."""
        pages_to_read = self._get_sample_page_indices(total_pages)
        full_text: List[str] = []
        
        for page_idx in sorted(list(pages_to_read)):
            page = pdf.pages[page_idx]
            text = page.extract_text()
            if text:
                full_text.append(f"--- Page {page_idx + 1} ---\n{text}")
        
        return "\n\n".join(full_text)

    def _get_sample_page_indices(self, total_pages: int) -> Set[int]:
        """Calculates which pages to sample (start, middle, end)."""
        indices: Set[int] = set()
        for i in range(min(3, total_pages)): indices.add(i)
        mid = total_pages // 2
        for i in range(max(0, mid - 1), min(total_pages, mid + 2)): indices.add(i)
        for i in range(max(0, total_pages - 3), total_pages): indices.add(i)
        return indices

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    parser = PdfParser()
    # Note: Requires a real PDF to test effectively
    print("PdfParser initialized. Call extract(file_path) to use.")
