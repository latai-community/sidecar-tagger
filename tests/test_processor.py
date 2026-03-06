import os
import json
import pytest
from unittest.mock import patch, MagicMock
from sdk.processor import MetadataProcessor
from sdk.models.metadata import FileMetadata

@pytest.fixture
def mock_llm_response():
    """Returns a mock FileMetadata object."""
    return FileMetadata(
        doc_type="pdf_document",
        language="en",
        domain="tech",
        category="test",
        context="Mocked context",
        tags=["pdf", "test"],
        confidence=0.9
    )

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

def test_extract_metadata_pdf(mock_file, mock_llm_response):
    """Test that PDF metadata is extracted correctly."""
    processor = MetadataProcessor()
    
    with patch("sdk.processor.LLMClient.generate_metadata", return_value=mock_llm_response):
        with patch("sdk.processor.extract_pdf_content", return_value="Real PDF Content"):
            metadata = processor.extract_metadata(mock_file)
            assert metadata["doc_type"] == "pdf_document"
            assert "pdf" in metadata["tags"]

def test_extract_metadata_xlsx(tmp_path, mock_llm_response):
    """Test that XLSX metadata is extracted correctly."""
    xlsx_file = tmp_path / "test.xlsx"
    xlsx_file.write_text("dummy")
    
    # Modify mock for XLSX
    mock_llm_response.doc_type = "spreadsheet"
    mock_llm_response.tags = ["xlsx", "test"]
    
    processor = MetadataProcessor()
    with patch("sdk.processor.LLMClient.generate_metadata", return_value=mock_llm_response):
        with patch("sdk.processor.extract_xlsx_content", return_value="Real Excel Data"):
            metadata = processor.extract_metadata(str(xlsx_file))
            assert metadata["doc_type"] == "spreadsheet"
            assert "xlsx" in metadata["tags"]

def test_process_files(mock_file, temp_sidecar, mock_llm_response):
    """Test the full processing flow and file output."""
    processor = MetadataProcessor(output_path=temp_sidecar)
    
    with patch("sdk.processor.LLMClient.generate_metadata", return_value=mock_llm_response):
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
