# Sidecar-tagger: Implementation Roadmap

This document tracks the development lifecycle of the Sidecar-tagger project. It serves as the source of truth for project progress and task prioritization.

## Project Status Overview
- **Current Phase:** Phase 1: Foundation
- **Last Updated:** 2026-03-05
- **Overall Completion:** 20%

---

## Phase 1: Foundation (Current Priority)
Focus: Establishing core parsing capabilities and data schemas.
- [x] **SDK: Pydantic Models**: Define robust schemas in `sdk/models/metadata.py` for PDF, XLSX, and Images.
- [ ] **SDK: PDF Parser**: Implement text and metadata extraction using `pdfplumber`.
- [ ] **SDK: XLSX Parser**: Implement data extraction and sheet analysis using `openpyxl`.
- [ ] **SDK: Image Parser**: Implement vision-based analysis for image files (JPG/PNG).

## Phase 2: LLM & Orchestration
Focus: Integrating AI intelligence and output validation.
- [ ] **SDK: LLM Integration**: Service to manage API keys (.env) and provider routing (Gemini/OpenAI).
- [ ] **SDK: Prompt Engineering**: Design specialized system prompts to enforce strict JSON schema output.
- [ ] **SDK: Validation**: Implement a validation layer to check LLM output against Pydantic models.

## Phase 3: Robustness & Testing
Focus: Stability, error handling, and CLI verification.
- [ ] **CLI: Error Handling**: Implement graceful degradation for missing files or API timeouts.
- [ ] **Tests: Unit Tests**: Achieve >80% coverage for individual parsers.
- [ ] **Tests: Integration Tests**: Validate the full E2E flow from CLI command to JSON output.

## Phase 4: Optimization & Scale
Focus: Performance tuning and cost management.
- [ ] **SDK: Performance**: Implement `asyncio` or multiprocessing for batch processing.
- [ ] **SDK: Token Optimization**: Implement smart chunking to reduce LLM costs on large documents.
- [ ] **CLI: Progress UI**: Add a progress bar (Rich/Tqdm) for better user feedback during batch runs.

---

## Instructions for AI Agents
1. **Consult** this roadmap before suggesting any code changes.
2. **Update** the status of tasks by marking them with `[x]` as soon as the implementation is verified.
3. **Log** significant changes in the "Last Updated" field.