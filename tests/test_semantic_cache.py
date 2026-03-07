import os
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

def test_semantic_cache_skips_llm(tmp_path, mock_llm_response):
    """Verifies that the LLM is not called for semantically identical content."""
    sidecar_file = tmp_path / "sidecar.json"
    processor = MetadataProcessor(output_path=str(sidecar_file))
    
    # Create two different file names with identical content
    file1 = tmp_path / "file1.txt"
    file1.write_text("This is identical semantic content for testing cache.")
    
    file2 = tmp_path / "file2.txt"
    file2.write_text("This is identical semantic content for testing cache.")

    # Patch LLM generate_metadata to track calls
    with patch("sdk.processor.LLMClient.generate_metadata", return_value=mock_llm_response) as mock_llm:
        # Step 1: Process file1 (Cache Miss)
        processor.process_files([str(file1)])
        assert mock_llm.call_count == 1
        
        # Step 2: Process file2 with same content (Cache Hit)
        # It should find the vector of file1 in the store and skip LLM
        processor.process_files([str(file2)])
        
        # Should still be 1!
        assert mock_llm.call_count == 1

def test_semantic_cache_persistence(tmp_path, mock_llm_response):
    """Verifies that the cache persists between processor instances using the sidecar file."""
    sidecar_file = tmp_path / "sidecar.json"
    
    file1 = tmp_path / "persistent_test.txt"
    file1.write_text("Persistence test content.")

    # Instance 1: Initial extraction (Cache Miss)
    processor1 = MetadataProcessor(output_path=str(sidecar_file))
    with patch("sdk.processor.LLMClient.generate_metadata", return_value=mock_llm_response):
        processor1.process_files([str(file1)])
    
    # Instance 2: Should load the sidecar and hit the cache
    processor2 = MetadataProcessor(output_path=str(sidecar_file))
    
    with patch("sdk.processor.LLMClient.generate_metadata") as mock_llm_instance2:
        processor2.extract_metadata(str(file1))
        # Should not call LLM because it loaded from the sidecar file
        mock_llm_instance2.assert_not_called()
