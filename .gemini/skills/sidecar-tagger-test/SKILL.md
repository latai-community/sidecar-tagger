---
name: sidecar-tagger-test
description: >
  Defines the testing strategy and evaluation criteria for Sidecar-tagger.
  Covers unit testing for parsers, CLI integration tests, and LLM output validation (evals).
  Trigger: When creating test cases, running benchmarks, or validating SDK/CLI outputs.
metadata:
  version: "1.0"
  author: latai-community
  scope: [sidecar-tagger/tests, evals/]
---

## Overview

The testing skill ensures that every component (CLI/SDK) meets the quality standards. It focuses on functional correctness and metadata accuracy.

| Test Level | Tool / Framework | Target |
|------------|------------------|--------|
| **Unit** | `pytest`         | Individual parsers (PDF, XLSX, IMG) |
| **Integration**| `pytest`     | CLI flag handling and end-to-end flow |
| **Evals** | `eval-viewer`    | LLM metadata quality and JSON schema |

---

## Critical Rules

### Test Case Design

- **ALWAYS**: Use mock files or small samples for PDF/XLSX/IMG to avoid heavy dependencies in tests.
- **ALWAYS**: Assert that the output file follows the naming convention `<file>.<ext>.json`.
- **NEVER**: Run tests that require real LLM API keys without a "mock" or "dry-run" option.

### Metadata Validation (Evals)

- **ALWAYS**: Verify that the `confidence` field is a float between 0.0 and 1.0.
- **ALWAYS**: Check that `tags` is a non-empty list of strings.
- **ALWAYS**: Validate the `language` field against ISO 639-1 expected values.
- **NEVER**: Pass a test if the JSON output is malformed or missing mandatory fields.

---

## QA Checklist (Testing)

- [ ] Every new CLI flag has a corresponding test case.
- [ ] Edge cases (empty files, corrupted PDFs) are handled and tested.
- [ ] The `evals/evals.json` includes at least one test for each supported format.
- [ ] Exit codes (0 for success, 1 for error) are verified in CLI tests.