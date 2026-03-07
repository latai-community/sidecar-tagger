"""
Title: Base Parser Interface
Abstract: Defines the Abstract Base Class (ABC) for all Sidecar-tagger content extractors.
Why: Enforces a consistent contract for all file parsers, ensuring the Processor can handle them uniformly.
Dependencies: abc, typing, sdk.exceptions
LLM-Hints: All new parsers must inherit from this class and implement the extract method.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from sdk.exceptions import ParserError

class BaseParser(ABC):
    """
    Abstract interface for file content extraction.
    Follows Pillar 2 (Interface-Driven) and Pillar 1 (Strict Typing).
    """

    @abstractmethod
    def extract(self, file_path: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Extracts content from a file and returns a structured dictionary.
        
        Args:
            file_path: Absolute or relative path to the file.
            **kwargs: Implementation-specific options (e.g., max_chars, resolution).
            
        Returns:
            Dict[str, Any]: A dictionary containing at least 'text' and optionally 'thumbnail_path'.
            
        Raises:
            ParserError: If extraction fails due to I/O, corruption, or unsupported format.
        """
        pass

if __name__ == "__main__":
    # Example showing a mock implementation of BaseParser
    class MockParser(BaseParser):
        def extract(self, file_path: str, **kwargs: Any) -> Dict[str, Any]:
            return {"text": f"Mock content from {file_path}"}
    
    parser = MockParser()
    print(parser.extract("test.txt"))
