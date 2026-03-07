# Sidecar-tagger: Implementation Roadmap

This document tracks the development lifecycle of the Sidecar-tagger project. It serves as the source of truth for project progress and task prioritization.

## Project Status Overview
- **Current Phase:** Phase 4: Optimization & Scale
- **Last Updated:** 2026-03-06
- **Overall Completion:** 90%

---

## Phase 1: Foundation (COMPLETED)
Focus: Establishing core parsing capabilities and data schemas.
- [x] **SDK: Pydantic Models**: Define robust schemas in `sdk/models/metadata.py` for PDF, XLSX, and Images.
- [x] **SDK: PDF Parser**: Implement text and metadata extraction using `pdfplumber`.
- [x] **SDK: XLSX Parser**: Implement data extraction and sheet analysis using `openpyxl`.
- [x] **SDK: Image Parser**: Implement vision-based analysis for image files (JPG/PNG).

## Phase 2: LLM & Orchestration (COMPLETED)
Focus: Integrating AI intelligence and output validation.
- [x] **SDK: LLM Integration**: Service to manage API keys (.env) and provider routing (Gemini).
- [x] **SDK: Prompt Engineering**: Design specialized system prompts to enforce strict JSON schema output.
- [x] **SDK: Validation**: Implement a validation layer to check LLM output against Pydantic models.

## Phase 3: Hybrid Tagging & Robustness (Current Priority)
Focus: Local classification, distributed sampling, and error handling.
- [x] **SDK: Local Embeddings**: Integrate a lightweight library (FastEmbed ONNX) for $0 cost vector generation.
- [x] **SDK: Distributed Sampling**: Implement "Start-Middle-End" chunking for large files.
- [x] **SDK: Conditional LLM**: Logic to trigger Gemini only when local confidence is < 0.9 or a summary is required (Semantic Cache).
- [x] **Schema: Vector Support**: Update `sidecar.json` to include the `embedding_vector` for local similarity searches.
- [x] **CLI: Error Handling**: Added retries and 429 backoff logic.
- [x] **Robustness: Multimodal Fallback**: Implemented native PDF upload and vision analysis for scanned or difficult documents.
- [x] **Schema: Review Flag**: Added `needs_review` field to mark unreadable or ambiguous files.

## Phase 4: Performance & Integration (Atomic Motor)
Focus: Transforming the tagger into a high-performance engine for search UIs and OS-level integration.
- [ ] **Performance: Multiprocessing**: Implement parallel file processing to index entire drives at maximum CPU speed.
- [ ] **Storage: SQLite Export**: Add support for exporting metadata to a local SQLite database for instant querying by UIs.
- [ ] **Integration: Watch Mode**: Implement a background observer (e.g., via `watchdog`) to auto-tag new files in real-time.
- [ ] **Optimization: Token Budgeting**: Smart chunking and sampling to minimize LLM costs while maintaining high accuracy.
- [ ] **CLI: Progress Dashboard**: Advanced TUI (Rich) to show real-time indexing progress, throughput, and cache hit rates.

---

## Instructions for AI Agents
1. **Consult** this roadmap before suggesting any code changes.
2. **Update** the status of tasks by marking them with `[x]` as soon as the implementation is verified.
3. **Log** significant changes in the "Last Updated" field.