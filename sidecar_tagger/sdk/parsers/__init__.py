"""
Title: Parsers Package
Abstract: Exports all available file parsers for the Sidecar-tagger project.
Why: Simplifies imports for the Processor layer.
Dependencies: sdk.parsers.base_parser, sdk.parsers.pdf_parser, sdk.parsers.xlsx_parser, sdk.parsers.image_parser, sdk.parsers.txt_parser
"""

from sidecar_tagger.sdk.parsers.base_parser import BaseParser
from sidecar_tagger.sdk.parsers.pdf_parser import PdfParser
from sidecar_tagger.sdk.parsers.xlsx_parser import XlsxParser
from sidecar_tagger.sdk.parsers.image_parser import ImageParser
from sidecar_tagger.sdk.parsers.txt_parser import TxtParser

__all__ = ["BaseParser", "PdfParser", "XlsxParser", "ImageParser", "TxtParser"]

if __name__ == "__main__":
    # Example usage
    print(f"Available parsers: {__all__}")
