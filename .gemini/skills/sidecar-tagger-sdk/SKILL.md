---
name: sidecar-tagger-sdk
description: >
  Specifies the SDK behavior and architecture for the Sidecar-tagger metadata extraction. 
  Covers file parsing (PDF, XLSX, Images), LLM prompting, and metadata structured output.
  Trigger: When working on sidecar-tagger/sdk/ or implementing extraction logic for specific file types.
metadata:
  version: "1.0"
  author: latai-community
  scope: [sidecar-tagger/sdk]
---

## Overview

The Sidecar-tagger SDK is the core engine responsible for reading file content and using LLMs to generate structured metadata. It must handle multi-modal inputs and return a strictly validated JSON object.

| Format | Parsing Strategy | Target Data |
|--------|------------------|-------------|
| **PDF** | Text & Layout Extraction | Reports, whitepapers, contracts |
| **XLSX**| Tabular Data Mapping | Sales data, logs, spreadsheets |
| **Images**| Vision-to-Text / OCR | Infographics, screenshots, photos |

---

## Critical Rules

### Content Extraction

- **ALWAYS**: Use format-specific parsers (e.g., `PyPDF2`/`pdfplumber` for PDF, `openpyxl` for XLSX).
- **ALWAYS**: Truncate or chunk content if it exceeds the LLM context window, prioritizing headers and summaries.
- **NEVER**: Send raw binary data to a text-only LLM; use OCR or Vision models for images.

### Metadata Generation (The "JSON Schema")

- **ALWAYS**: Force the LLM to return the exact JSON structure defined in the business logic.
- **ALWAYS**: Include a `confidence` score based on the clarity of the source material.
- **ALWAYS**: Detect `language` using ISO 639-1 codes.
- **NEVER**: Allow the LLM to invent fields outside the specified schema.

### Error Handling & Reliability

- **ALWAYS**: Implement a fallback mechanism if a file is corrupted or unreadable.
- **ALWAYS**: Validate the JSON output against the schema before returning it to the CLI.
- **NEVER**: Return an empty metadata file; provide at least `doc_type` as "unknown" and an error context.

---

## Core Schema Reference

```json
{
  "doc_type": "string",
  "language": "string",
  "domain": "string",
  "category": "string",
  "context": "string",
  "tags": ["array", "of", "strings"],
  "content_date": "ISO-8601",
  "confidence": 0.0
}
```

---

## QA Checklist (SDK)
- [ ] PDF parser handles multi-column layouts correctly.
- [ ] XLSX extraction captures sheet names as part of the context.
- [ ] Image processing uses a Vision-capable model for tag generation.
- [ ] Token usage is optimized to avoid unnecessary costs.
- [ ] content_date is extracted from the document content when available.

---

## Related Skills
- **[sidecar-tagger](../sidecar-tagger/SKILL.md)**: Global project orchestrator and roadmap.
- **[sidecar-tagger-cli](../sidecar-tagger-cli/SKILL.md)**: CLI interface that consumes this SDK.
- **[sidecar-tagger-test](../sidecar-tagger-test/SKILL.md)**: Testing suite for parser validation and LLM output quality.
