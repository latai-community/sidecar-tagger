---
name: sidecar-tagger-sdk
description: >
  Specifies the SDK behavior and architecture for the Sidecar-tagger v2 metadata extraction. 
  Covers the 5-Layer pipeline (Hash, Context, Cluster, Embedding, AI) and core parsing logic.
  Trigger: When working on sidecar-tagger/sdk/ or implementing extraction logic for specific file types.
metadata:
  version: "2.0"
  author: latai-community
  scope: [sidecar-tagger/sdk]
---

## Overview

The Sidecar-tagger SDK v2 is a **Context-Aware Engine** that implements a 5-Layer pipeline to minimize AI costs and maximize precision. It enforces strict engineering standards inspired by Java (Strict typing, Interface-driven design).

### The 5-Layer Pipeline

| Layer | Component | Objective | Strategy |
|-------|-----------|-----------|----------|
| **0** | **Hash Gate** | Deduplication | SHA-256 binary identity check. |
| **1** | **Context Builder** | Fact Finding | OS stats, parent folders, internal metadata props. |
| **2** | **Cluster Manager** | Neighbor Wisdom | Fuzzy matching of names to group similar files. |
| **3** | **Embedding Check** | Semantic Cache | Local ONNX vectors to detect reused content. |
| **4** | **Cognitive Analysis**| AI Extraction | Gemini analysis injected with Layers 1 & 2 context. |

---

## Critical Rules

### Architecture & Standards

- **ALWAYS**: Adhere to the **`sidecar-engine-standards`** (Strict Typing, ABCs, custom exceptions).
- **ALWAYS**: Inherit all parsers from `BaseParser` and raise `ParserError` for failures.
- **ALWAYS**: Use `logging` instead of `print` for internal SDK operations.

### Content Extraction

- **ALWAYS**: Use `pdfplumber` for PDF, `openpyxl` for XLSX, and `TxtParser` for plain text.
- **ALWAYS**: Include context hints from Layer 1 & 2 in the LLM prompt to reduce hallucinations.
- **NEVER**: Call the LLM (Layer 4) if a match is found in Layer 0 or Layer 3.

### Metadata & Models

- **ALWAYS**: Return a validated `FileMetadata` Pydantic object.
- **ALWAYS**: Ensure Layer 1 & 2 data is populated in `local_context` and `cluster_hint` fields.
- **NEVER**: Return raw strings for errors; use the `_get_error_metadata` helper.

---

## Core Schema Reference (v2)

```json
{
  "file_hash": "string",
  "doc_type": "string",
  "language": "string",
  "domain": "string",
  "category": "string",
  "context": "string",
  "tags": ["array"],
  "confidence": 0.0,
  "local_context": { "filename": "str", "parent_folder": "string" },
  "cluster_hint": { "cluster_id": "str", "is_anomaly": "bool" }
}
```

---

## QA Checklist (SDK v2)
- [ ] Layer 0 SHA-256 calculation uses block streaming for large files.
- [ ] Layer 1 extraction captures the correct file owner and parent folder.
- [ ] Layer 2 grouping logic identifies similar files correctly within folders.
- [ ] LLM prompt explicitly includes injected context facts.
- [ ] Resource management (Context Managers) is enforced for all I/O.

---

## Related Skills
- **[sidecar-engine-standards](../sidecar-engine-standards/SKILL.md)**: Mandatory engineering mandates.
- **[sidecar-tagger-cli](../sidecar-tagger-cli/SKILL.md)**: CLI interface.
- **[sidecar-tagger-test](../sidecar-tagger-test/SKILL.md)**: Testing suite.
