import os
import json
import pytest
from unittest.mock import patch
from sdk.processor import MetadataProcessor

@pytest.fixture
def temp_sidecar(tmp_path):
    """Fixture to provide a temporary sidecar output path."""
    return str(tmp_path / "sidecar.json")

@pytest.fixture
def mock_file(tmp_path):
    """Fixture to create a temporary mock file."""
    p = tmp_path / "test_file.pdf"
    p.write_text("fake pdf content")
    return str(p)

def test_extract_metadata_pdf(mock_file):
    """Test that PDF metadata is extracted correctly."""
    processor = MetadataProcessor()
    # mock_file is .pdf from the fixture
    with patch("sdk.processor.extract_pdf_content", return_value="Real PDF Content"):
        metadata = processor.extract_metadata(mock_file)
        assert metadata["doc_type"] == "pdf_document"
        assert "pdf" in metadata["tags"]
        assert "Real PDF Content" in metadata["context"]

def test_extract_metadata_xlsx(tmp_path):
    """Test that XLSX metadata is extracted correctly."""
    xlsx_file = tmp_path / "test.xlsx"
    xlsx_file.write_text("dummy")
    processor = MetadataProcessor()
    with patch("sdk.processor.extract_xlsx_content", return_value="Real Excel Data"):
        metadata = processor.extract_metadata(str(xlsx_file))
        assert metadata["doc_type"] == "spreadsheet"
        assert "xlsx" in metadata["tags"]
        assert "Real Excel Data" in metadata["context"]

def test_process_files(mock_file, temp_sidecar):
    """Test the full processing flow and file output."""
    processor = MetadataProcessor(output_path=temp_sidecar)
    with patch("sdk.processor.extract_pdf_content", return_value="Mocked PDF Content"):
        processor.process_files([mock_file])
    
    assert os.path.exists(temp_sidecar)
    
    with open(temp_sidecar, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert mock_file in data
    assert data[mock_file]["doc_type"] == "pdf_document"

def test_process_missing_file(temp_sidecar):
    """Test that a missing file is handled (warning printed, not in sidecar)."""
    processor = MetadataProcessor(output_path=temp_sidecar)
    processor.process_files(["non_existent_file.txt"])
    
    assert os.path.exists(temp_sidecar)
    with open(temp_sidecar, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert len(data) == 0
