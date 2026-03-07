# Changelog: Sidecar-tagger

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Gemini 3 Integration**: Upgraded default model to `gemini-3-flash-preview` for smarter metadata extraction.
- **Semantic Cache (Embedding First)**: New logic in `MetadataProcessor` that checks for similar documents locally before calling the LLM.
- **Local Embeddings (ONNX)**: Integrated `FastEmbed` for high-performance 384-dimensional vector generation on CPU ($0 cost).
- **Threshold-based LLM Triggering**: Automatic decision logic; skip LLM if local similarity is > 0.9.
- **Hybrid Tagging Architecture**: New strategy using distributed sampling (Start-Middle-End) and local embeddings for efficient document classification.
- **LLM Integration**: Added `LLMClient` with support for Google Gemini and strict JSON output.
- **Distributed Sampling**: Implemented in `pdf_parser.py` (3-3-3 pages) and `xlsx_parser.py` (Start-Mid-End sheets).
- **Retry Logic**: Added exponential backoff for LLM Rate Limit errors (429).
- **Metadata Support**: Added `embedding_vector` to the `FileMetadata` Pydantic model.
- **Workflow Standards**: New reference defining mandatory steps for changelog updates and test verification.
- **Test Robustness**: Implemented LLM mocking in `tests/test_processor.py` to ensure unit and integration tests run independently of API keys or network status.

### Changed
- **Environment Handling**: Updated `load_dotenv(override=True)` to ensure .env changes are applied immediately.
- **Dependencies**: Upgraded to `pydantic>=2.9.2`, `google-generativeai`, and added `fastembed`.
- **Roadmap**: Progress updated to 80%.
- **Skill Structure**: Interconnected all AI skills using "Related Skills" sections.
- **Parser Optimization**: PDF extraction now targets specific pages (Start/Mid/End) instead of a simple linear truncation.

### Why?
- The **Semantic Cache** was implemented to drastically reduce costs and latency. By using the "Embedding First" approach suggested by the user, the system avoids redundant API calls for similar documents.
- Upgrading to **Gemini 3** ensures better performance and accuracy for complex document types identified in recent tests (e.g., academic textbooks).
- **FastEmbed (ONNX)** was chosen for being CPU-optimized and lightweight, maintaining the "low resource" goal of the project.
