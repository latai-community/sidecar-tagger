from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class FileMetadata(BaseModel):
    """
    Core metadata schema for all source files (PDF, XLSX, Images).
    This structure is serialized into the consolidated sidecar.json.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "doc_type": "invoice",
                "language": "es",
                "domain": "finance",
                "category": "accounts_payable",
                "context": "Invoice from Supplier X for cloud services",
                "tags": ["cloud", "azure", "billing"],
                "content_date": "2024-05-22T10:00:00Z",
                "confidence": 0.95
            }
        }
    )

    doc_type: Optional[str] = Field("unknown", description="Document classification (e.g., invoice, report, screenshot)")
    language: Optional[str] = Field("unknown", description="Primary language of the document")
    domain: Optional[str] = Field("unknown", description="Industry or functional domain (e.g., finance, legal, tech)")
    category: Optional[str] = Field("unknown", description="Sub-classification or department")
    context: Optional[str] = Field("Unknown content", description="Brief summary of the file content")
    tags: List[str] = Field(default_factory=list, description="Extracted keywords or classification tags")
    content_date: Optional[str] = Field(None, description="Date extracted from the document content (may be partial)")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Overall confidence score for the LLM extraction")
    needs_review: bool = Field(False, description="Flagged for manual review if content is unreadable or extraction failed")
    embedding_vector: Optional[List[float]] = Field(None, description="Local vector representation for similarity search")
