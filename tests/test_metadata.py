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
        "content_date": datetime.now(),
        "confidence": 0.95
    }
    metadata = FileMetadata(**data)
    assert metadata.doc_type == "invoice"
    assert metadata.confidence == 0.95
    assert isinstance(metadata.content_date, datetime)

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

def test_missing_field():
    """Test that missing a required field raises a ValidationError."""
    with pytest.raises(ValidationError):
        FileMetadata(
            # doc_type is missing
            language="en",
            domain="finance",
            category="accounts_payable",
            context="context",
            confidence=0.9
        )

def test_json_serialization():
    """Test that model_dump(mode='json') correctly serializes datetime."""
    metadata = FileMetadata(
        doc_type="invoice",
        language="en",
        domain="finance",
        category="accounts_payable",
        context="context",
        content_date=datetime.now(),
        confidence=0.9
    )
    json_data = metadata.model_dump(mode='json')
    assert isinstance(json_data["content_date"], str)
    # Check if it follows ISO 8601 roughly (contains 'T')
    assert 'T' in json_data["content_date"]
