# Changelog: Sidecar-tagger

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Hybrid Tagging Architecture**: New strategy using distributed sampling (Start-Middle-End) and local embeddings for efficient document classification.
- **LLM Integration**: Added `LLMClient` with support for Google Gemini and strict JSON output.
- **Distributed Sampling**: Implemented in `pdf_parser.py` (3-3-3 pages) and `xlsx_parser.py` (Start-Mid-End sheets).
- **Retry Logic**: Added exponential backoff for LLM Rate Limit errors (429).
- **Metadata Support**: Added `embedding_vector` to the `FileMetadata` Pydantic model.
- **Workflow Standards**: New reference defining mandatory steps for changelog updates and test verification.
- **Test Robustness**: Implemented LLM mocking in `tests/test_processor.py` to ensure unit and integration tests run independently of API keys or network status.

### Changed
- **Dependencies**: Upgraded to `pydantic>=2.9.2` and added `google-generativeai`.
- **Roadmap**: Progress updated to 50%.
- **Skill Structure**: Interconnected all AI skills using "Related Skills" sections.
- **Parser Optimization**: PDF extraction now targets specific pages (Start/Mid/End) instead of a simple linear truncation.

### Why?
- The switch to **Hybrid Tagging** was made to reduce token costs and improve accuracy on large documents (like 500+ page books) that previously would lose context due to simple truncation.
- **Retry logic** was implemented to handle the Free Tier quota limits of the Gemini API gracefully.
