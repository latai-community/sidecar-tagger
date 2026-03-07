"""
Title: Metadata Models
Abstract: Defines the core Pydantic schemas for the Sidecar-tagger project (v2).
Why: Ensures consistent, type-safe metadata extraction and serialization across SDK and CLI.
Dependencies: pydantic, typing, datetime
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict

class LocalContext(BaseModel):
    """
    Layer 1: Contextual facts extracted from the OS and file headers (Algorithmic).
    Used to ground the AI and reduce hallucinations.
    """
    filename: str = Field(..., description="Original filename")
    file_extension: str = Field(..., description="File extension (e.g., .pdf)")
    file_size_bytes: int = Field(0, description="Size in bytes")
    creation_date: Optional[str] = Field(None, description="File creation timestamp (ISO 8601)")
    modification_date: Optional[str] = Field(None, description="Last modification timestamp (ISO 8601)")
    owner: Optional[str] = Field(None, description="System owner of the file")
    parent_folder: Optional[str] = Field(None, description="Immediate parent directory name")
    path_keywords: List[str] = Field(default_factory=list, description="Keywords extracted from full path")
    internal_props: Dict[str, str] = Field(default_factory=dict, description="Internal metadata (Author, Title) from Office/PDF props")

class ClusterHint(BaseModel):
    """
    Layer 2: Suggestions derived from neighboring files (Collective Intelligence).
    Used to guide the AI with high-confidence patterns found in the same folder.
    """
    cluster_id: Optional[str] = Field(None, description="Unique ID for the file cluster")
    similarity_score: float = Field(0.0, description="Similarity to cluster leader (0.0 - 1.0)")
    suggested_category: Optional[str] = Field(None, description="Category inherited from cluster leader")
    suggested_tags: List[str] = Field(default_factory=list, description="Tags inherited from cluster leader")
    is_anomaly: bool = Field(False, description="True if file is semantically distant from neighbors")

class FileMetadata(BaseModel):
    """
    Core metadata schema for all source files (PDF, XLSX, Images).
    This structure is serialized into the consolidated sidecar.json.
    Integrates Layer 0, 1, 2, 3, and 4 outputs.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_hash": "sha256_hash_string...",
                "doc_type": "invoice",
                "language": "es",
                "domain": "finance",
                "category": "accounts_payable",
                "context": "Invoice from Supplier X for cloud services",
                "tags": ["cloud", "azure", "billing"],
                "content_date": "2024-05-22T10:00:00Z",
                "confidence": 0.95,
                "local_context": {...},
                "cluster_hint": {...}
            }
        }
    )

    # Layer 0: Binary Identity
    file_hash: Optional[str] = Field(None, description="SHA-256 hash for exact deduplication")
    duplicate_of: Optional[str] = Field(None, description="Path to the original file if this is a duplicate")

    # Layer 1 & 2: Contextual Inputs
    local_context: Optional[LocalContext] = Field(None, description="OS and Header facts")
    cluster_hint: Optional[ClusterHint] = Field(None, description="Neighborhood context suggestions")

    # Layer 3 & 4: Semantic Analysis
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

if __name__ == "__main__":
    # Example usage for verification
    metadata = FileMetadata(
        file_hash="abc123hash",
        doc_type="test_report",
        language="en",
        domain="tech",
        category="qa",
        context="Automated test report for sidecar-tagger",
        tags=["refactor", "pydantic"],
        confidence=1.0,
        local_context=LocalContext(filename="test.pdf", file_extension=".pdf"),
        cluster_hint=ClusterHint(is_anomaly=False)
    )
    print(metadata.model_dump_json(indent=2))
