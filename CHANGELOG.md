# Changelog: Sidecar-tagger

All notable changes to this project will be documented in this file.

## [Unreleased]

### Architectural Decisions (ADR)
- **ADR-003 (The 5-Layer Engine)**: Adopted a comprehensive "Contextual Engine" architecture to replace the linear processing flow.
    - **Rationale**: To minimize AI costs and maximize precision by leveraging local CPU (Hash/OS Metadata) before invoking the LLM.
    - **Impact**: processing will now follow a 5-step pipeline: Hash -> Context -> Cluster -> Embedding -> AI.
- **ADR-002 (Engine Standards)**: Enforced strict "Java-Grade" engineering standards for the Python SDK.
    - **Mandates**: Strict Typing, Interface-Driven Parsers, Semantic Exceptions, Structured Logging.
    - **Skill**: Created `.gemini/skills/sidecar-engine-standards` to automate enforcement.

### Added
- **Planning Documentation**: Created `planning.md` as the master reference for the v2 architecture.
- **Text Parsing Engine**: Implemented `txt_parser.py` with memory-safe streaming, encoding detection (UTF-8/Latin-1), and truncation logic for large files.
- **Robustness**: Added comprehensive test suite for text parsing covering edge cases (binary files, empty files, legacy encodings).
- **Native PDF Multimodal Analysis**: Updated `LLMClient` to upload PDF files directly to Gemini 3. This allows the AI to "see" scanned documents and images within PDFs when text extraction fails.
- **Multimodal Prompting**: Enhanced system prompts to guide Gemini in analyzing visual elements and hidden layers in complex documents.
- **Robust Metadata Schema**: Updated `FileMetadata` to handle partial dates and null fields, ensuring the system doesn't crash on incomplete AI responses.
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
- **Refactoring (Engine Standards)**: Complete rewrite of `sdk/processor.py`, `sdk/parsers/*.py`, and `cli/main.py` to adhere to strict typing and exception handling.
- **Project Vision (ADR)**: Redefined Sidecar-tagger as an **Atomic Metadata Engine**. The project will focus exclusively on high-performance index generation (JSON/SQLite) to serve as a backend for search UIs and OS integrations, rather than implementing search logic itself.
- **Environment Handling**: Updated `load_dotenv(override=True)` to ensure .env changes are applied immediately.
- **Dependencies**: Upgraded to `pydantic>=2.9.2`, `google-generativeai`, and added `fastembed`.
- **Roadmap**: Progress updated to 80%.
- **Skill Structure**: Interconnected all AI skills using "Related Skills" sections.
- **Parser Optimization**: PDF extraction now targets specific pages (Start/Mid/End) instead of a simple linear truncation.

### Why?
- The **5-Layer Engine** allows us to inject "Ground Truth" (OS facts) into the AI, reducing hallucinations and costs.
- **Engine Standards** ensure the codebase remains maintainable and robust as we scale to complex multi-layer logic.
- The **Semantic Cache** was implemented to drastically reduce costs and latency. By using the "Embedding First" approach suggested by the user, the system avoids redundant API calls for similar documents.
- Upgrading to **Gemini 3** ensures better performance and accuracy for complex document types identified in recent tests (e.g., academic textbooks).
- **FastEmbed (ONNX)** was chosen for being CPU-optimized and lightweight, maintaining the "low resource" goal of the project.
