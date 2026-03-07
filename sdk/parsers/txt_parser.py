"""
Title: TXT Parser
Abstract: Extracts text from plain text files with encoding resilience.
Why: Provides a memory-safe way to read large or legacy text files for LLM processing.
Dependencies: os, logging, sdk.parsers.base_parser, sdk.exceptions
"""

import os
import logging
from typing import Dict, Any
from sdk.parsers.base_parser import BaseParser
from sdk.exceptions import ParserError

logger = logging.getLogger(__name__)

class TxtParser(BaseParser):
    """
    Parser for plain text files.
    Follows Pillar 1 (Strict Typing) and Pillar 2 (Interface-Driven).
    """

    def extract(self, file_path: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Extracts content from a text file.
        
        Args:
            file_path: Path to the .txt file.
            **kwargs: max_chars (default 50000).
            
        Returns:
            Dict[str, Any]: {'text': str}
            
        Raises:
            ParserError: If file is missing, empty, or unreadable.
        """
        max_chars = kwargs.get("max_chars", 50000)
        self._validate_file(file_path)

        try:
            content = self._read_with_encodings(file_path, max_chars)
            return {"text": content}
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            raise ParserError(f"Failed to read text file: {e}") from e

    def _validate_file(self, file_path: str) -> None:
        """Validates file existence and size."""
        if not os.path.exists(file_path):
            raise ParserError(f"File not found: {file_path}")
        if os.path.getsize(file_path) == 0:
            raise ParserError(f"File is empty: {file_path}")

    def _read_with_encodings(self, file_path: str, max_chars: int) -> str:
        """Attempts to read file with UTF-8 then Latin-1 fallback."""
        file_size = os.path.getsize(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read(max_chars)
                return self._format_result(content, file_size, max_chars)
        except UnicodeDecodeError:
            logger.debug(f"UTF-8 failed for {file_path}, falling back to Latin-1")
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read(max_chars)
                return self._format_result(content, file_size, max_chars)

    def _format_result(self, content: str, original_size: int, limit: int) -> str:
        """Adds truncation notes if necessary."""
        content = content.strip()
        if original_size > limit:
            content += f"\n\n[NOTE: Content truncated. Original size: {original_size} bytes.]"
        return content

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    parser = TxtParser()
    try:
        # Create a dummy file for the example
        with open("example.txt", "w") as f:
            f.write("Hello Sidecar-tagger!")
        print(parser.extract("example.txt"))
        os.remove("example.txt")
    except Exception as e:
        print(f"Error: {e}")
