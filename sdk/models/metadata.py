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

    doc_type: str = Field(..., description="Document classification (e.g., invoice, report, screenshot)")
    language: str = Field(..., description="Primary language of the document")
    domain: str = Field(..., description="Industry or functional domain (e.g., finance, legal, tech)")
    category: str = Field(..., description="Sub-classification or department")
    context: str = Field(..., description="Brief summary or contextual description of the file content")
    tags: List[str] = Field(default_factory=list, description="Extracted keywords or classification tags")
    content_date: Optional[datetime] = Field(None, description="ISO-8601 date extracted from the document content (e.g., invoice date)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score for the LLM extraction")
