import pytest
from datetime import datetime
from pydantic import ValidationError
from sdk.models.metadata import FileMetadata

def test_valid_metadata():
    """Test that a valid FileMetadata instance can be created."""
    data = {
        "doc_type": "invoice",
        "language": "en",
        "domain": "finance",
        "category": "accounts_payable",
        "context": "Cloud service invoice",
        "tags": ["cloud", "azure"],
        "content_date": "2024-05-22T10:00:00Z",
        "confidence": 0.95
    }
    metadata = FileMetadata(**data)
    assert metadata.doc_type == "invoice"
    assert metadata.confidence == 0.95
    assert isinstance(metadata.content_date, str)

def test_optional_date():
    """Test that content_date is optional."""
    data = {
        "doc_type": "invoice",
        "language": "en",
        "domain": "finance",
        "category": "accounts_payable",
        "context": "context",
        "confidence": 0.9
    }
    metadata = FileMetadata(**data)
    assert metadata.content_date is None

def test_invalid_confidence():
    """Test that an invalid confidence score (out of range) raises a ValidationError."""
    with pytest.raises(ValidationError):
        FileMetadata(
            doc_type="invoice",
            language="en",
            domain="finance",
            category="accounts_payable",
            context="context",
            confidence=1.5  # Invalid, must be <= 1.0
        )

def test_default_values():
    """Test that missing fields get default values instead of raising ValidationError."""
    metadata = FileMetadata(
        # doc_type is missing, should default to "unknown"
        language="en",
        domain="finance",
        category="accounts_payable",
        context="context",
        confidence=0.9
    )
    assert metadata.doc_type == "unknown"

def test_json_serialization():
    """Test that model_dump(mode='json') correctly serializes data."""
    metadata = FileMetadata(
        doc_type="invoice",
        language="en",
        domain="finance",
        category="accounts_payable",
        context="context",
        content_date="2024-05-22T10:00:00Z",
        confidence=0.9
    )
    json_data = metadata.model_dump(mode='json')
    assert isinstance(json_data["content_date"], str)
    assert json_data["content_date"] == "2024-05-22T10:00:00Z"
