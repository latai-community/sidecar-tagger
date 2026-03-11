import pytest
from unittest.mock import MagicMock, patch
from sdk.parsers.pdf_parser import PdfParser
from sdk.parsers.xlsx_parser import XlsxParser
from sdk.parsers.image_parser import ImageParser
import os

# --- PDF Parser Tests ---
@patch("pdfplumber.open")
def test_extract_pdf_content(mock_open):
    # Mocking pdfplumber structure
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample PDF Text"
    
    # Mocking thumbnail generation calls
    mock_img = MagicMock()
    mock_page.to_image.return_value.original = mock_img
    mock_img.convert.return_value.getextrema.return_value = (0, 255) # Not white
    
    mock_pdf.pages = [mock_page]
    mock_pdf.metadata = {"Author": "Test"}
    mock_open.return_value.__enter__.return_value = mock_pdf
    
    # We need a file that "exists" for the os.path.exists check
    with patch("os.path.exists", return_value=True):
        parser = PdfParser()
        result = parser.extract("dummy.pdf")
        content = result["text"]
        assert "Sample PDF Text" in content
        mock_open.assert_called_once_with("dummy.pdf")

# --- XLSX Parser Tests ---
@patch("openpyxl.load_workbook")
def test_extract_xlsx_content(mock_load):
    # Mocking openpyxl structure
    mock_wb = MagicMock()
    mock_wb.sheetnames = ["Sheet1"]
    mock_sheet = MagicMock()
    mock_sheet.max_row = 10
    mock_sheet.max_column = 5
    # iter_rows mock
    mock_sheet.iter_rows.return_value = [("Cell1", "Cell2", None)]
    mock_wb.__getitem__.return_value = mock_sheet
    mock_load.return_value = mock_wb
    
    with patch("os.path.exists", return_value=True):
        parser = XlsxParser()
        result = parser.extract("dummy.xlsx")
        content = result["text"]
        assert "Sheet1" in content
        assert "10 rows" in content
        assert "Cell1 | Cell2" in content

# --- Image Parser Tests ---
@patch("PIL.Image.open")
def test_extract_image_metadata(mock_img_open):
    # Mocking PIL Image
    mock_img = MagicMock()
    mock_img.format = "PNG"
    mock_img.mode = "RGB"
    mock_img.width = 100
    mock_img.height = 200
    mock_img.getexif.return_value = {} # Empty EXIF
    mock_img_open.return_value.__enter__.return_value = mock_img
    
    with patch("os.path.exists", return_value=True):
        parser = ImageParser()
        result = parser.extract("dummy.png")
        content = result["text"]
        assert "PNG" in content
        assert "100x200" in content
