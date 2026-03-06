import os
import json
import pytest
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

def test_extract_metadata(mock_file):
    """Test that metadata is extracted and matches the schema."""
    processor = MetadataProcessor()
    metadata = processor.extract_metadata(mock_file)
    
    assert "doc_type" in metadata
    assert "language" in metadata
    assert "confidence" in metadata
    assert metadata["confidence"] == 0.9

def test_process_files(mock_file, temp_sidecar):
    """Test the full processing flow and file output."""
    processor = MetadataProcessor(output_path=temp_sidecar)
    processor.process_files([mock_file])
    
    assert os.path.exists(temp_sidecar)
    
    with open(temp_sidecar, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert mock_file in data
    assert data[mock_file]["doc_type"] == "document"

def test_process_missing_file(temp_sidecar):
    """Test that a missing file is handled (warning printed, not in sidecar)."""
    processor = MetadataProcessor(output_path=temp_sidecar)
    processor.process_files(["non_existent_file.txt"])
    
    assert os.path.exists(temp_sidecar)
    with open(temp_sidecar, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert len(data) == 0
