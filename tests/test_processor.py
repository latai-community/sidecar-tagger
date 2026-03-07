import os
import json
import pytest
import logging
from unittest.mock import patch, MagicMock
from sdk.processor import MetadataProcessor
from sdk.models.metadata import FileMetadata
from sdk.exceptions import ParserError, LLMClientError

# Disable logging during tests to keep output clean
logging.disable(logging.CRITICAL)

@pytest.fixture
def mock_llm_response():
    """Returns a mock FileMetadata object with Pydantic descriptions (Pillar 6)."""
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
    return str(tmp_path / "sidecar_test.json")

@pytest.fixture
def mock_pdf(tmp_path):
    """Fixture to create a temporary mock PDF file."""
    p = tmp_path / "test_doc.pdf"
    p.write_text("fake pdf content")
    return str(p)

@pytest.fixture
def mock_txt(tmp_path):
    """Fixture to create a temporary mock TXT file."""
    p = tmp_path / "test_notes.txt"
    p.write_text("Hello World Notes")
    return str(p)

def test_extract_metadata_pdf_flow(mock_pdf, mock_llm_response):
    """
    Test that PDF metadata is extracted correctly using the new class-based parser.
    Validates Pillar 2 (Interface-Driven) integration.
    """
    processor = MetadataProcessor()
    
    # Mocking the Parser and LLM Client
    with patch("sdk.parsers.PdfParser.extract", return_value={"text": "Real PDF Content", "thumbnail_path": None}):
        with patch("sdk.llm_client.LLMClient.generate_metadata", return_value=mock_llm_response):
            metadata = processor.extract_metadata(mock_pdf)
            assert metadata["doc_type"] == "pdf_document"
            assert "pdf" in metadata["tags"]
            assert "embedding_vector" in metadata

def test_extract_metadata_txt_flow(mock_txt, mock_llm_response):
    """Test the TXT extraction flow with the new engine standards."""
    processor = MetadataProcessor()
    
    mock_llm_response.doc_type = "text_file"
    mock_llm_response.tags = ["txt", "test"]
    
    with patch("sdk.parsers.TxtParser.extract", return_value={"text": "Hello World Notes"}):
        with patch("sdk.llm_client.LLMClient.generate_metadata", return_value=mock_llm_response):
            metadata = processor.extract_metadata(mock_txt)
            assert metadata["doc_type"] == "text_file"
            assert "txt" in metadata["tags"]

def test_processor_error_handling(mock_pdf):
    """
    Validates Pillar 3 (Semantic Error Handling).
    When a parser fails, the processor should return a structured error metadata object.
    """
    processor = MetadataProcessor()
    
    # Simulate a ParserError being raised
    with patch("sdk.parsers.PdfParser.extract", side_effect=ParserError("Corrupt PDF")):
        metadata = processor.extract_metadata(mock_pdf)
        assert metadata["doc_type"] == "error"
        assert "Corrupt PDF" in metadata["context"]
        assert metadata["needs_review"] is True

def test_full_process_files_io(mock_pdf, temp_sidecar, mock_llm_response):
    """Test the full processing flow and file output with the new manifest format."""
    processor = MetadataProcessor(output_path=temp_sidecar)
    
    with patch("sdk.parsers.PdfParser.extract", return_value={"text": "Mock Content", "thumbnail_path": None}):
        with patch("sdk.llm_client.LLMClient.generate_metadata", return_value=mock_llm_response):
            processor.process_files([mock_pdf])
    
    assert os.path.exists(temp_sidecar)
    
    with open(temp_sidecar, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert mock_pdf in data
    assert data[mock_pdf]["doc_type"] == "pdf_document"
    assert "embedding_vector" in data[mock_pdf]

def test_cache_hit_logic(mock_pdf, mock_llm_response):
    """
    Validates the Semantic Cache logic.
    If a similar vector is found, the LLM should NOT be called.
    """
    processor = MetadataProcessor()
    
    # Seed the processor memory with an existing vector
    fake_vector = [0.1] * 384
    processor.metadata_store[mock_pdf] = {
        "doc_type": "cached_doc",
        "embedding_vector": fake_vector,
        "confidence": 1.0,
        "tags": ["cached"]
    }
    
    with patch("sdk.parsers.PdfParser.extract", return_value={"text": "Same Content"}):
        with patch("sdk.embeddings_client.LocalEmbeddings.generate_vector", return_value=fake_vector):
            with patch("sdk.llm_client.LLMClient.generate_metadata") as mock_llm:
                metadata = processor.extract_metadata(mock_pdf)
                # Ensure LLM was NEVER called due to cache hit
                mock_llm.assert_not_called()
                assert metadata["doc_type"] == "cached_doc"
                assert "cached" in metadata["tags"]
