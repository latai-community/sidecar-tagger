---
name: sidecar-tagger
description: >
  Overall orchestrator and architect for the Sidecar-tagger project. 
  Make sure to use this skill whenever the user mentions project status, 
  roadmap progress, architectural decisions, or cross-component workflows 
  between CLI and SDK. It is essential for ensuring that every implementation 
  step aligns with the defined Phase-based roadmap.
metadata:
  version: "1.1"
  author: latai-community
  scope: [root]
---

# Sidecar-tagger Orchestrator

## Overview
Sidecar-tagger is an automated metadata generation system. It follows a "sidecar pattern" where every source file gets a corresponding `.json` file containing LLM-derived insights.

| Project Layer | Responsibility | Reference Skill |
|---------------|----------------|-----------------|
| **CLI** | User interface, flags, and batch input | `sidecar-tagger-cli` |
| **SDK** | Multi-format parsing and LLM orchestration | `sidecar-tagger-sdk` |
| **Schema** | Truth source for the metadata JSON structure | `sidecar-tagger-sdk` |

---

## Implementation Tracking (Roadmap)
The project status is maintained in a living document to ensure progressive disclosure and alignment.

- **Reference File**: `references/roadmap.md`
- **Requirement**: ALWAYS read `references/roadmap.md` at the start of a session or when implementing a new feature to understand the current "Priority Phase".
- **Self-Correction**: After completing a task (e.g., finishing a parser or CLI flag), proactively update the roadmap in `references/roadmap.md` by marking tasks as completed `[x]`.

---

## Critical Rules (Global)

### Project Architecture
- **ALWAYS**: Keep a strict separation between CLI logic (argparse) and SDK logic (processing).
- **ALWAYS**: Generate a consolidated `sidecar.json` containing metadata for all input files in the batch.
- **NEVER**: Modify the original source files; the tool is strictly read-only for inputs.

### Workflow Orchestration
- **ALWAYS**: Initialize the SDK from the CLI with the user-provided configurations (confidence, output-dir).
- **ALWAYS**: Log the start and end of the global process in the console.
- **NEVER**: Commit generated `.json` sidecars to the core repository; they should be ignored via `.gitignore`.

---

## Directory Structure
```text
sidecar-tagger/
├── cli/                # Entry point and argument logic
├── sdk/                # Core processing engine
│   ├── parsers/        # PDF, XLSX, Image specialized logic
│   └── models/         # Pydantic/JSON schemas
├── tests/              # Integration and unit tests
├── references/         # Roadmap and technical documentation
└── SKILL.md            # This orchestrator

```

---

## Media Assets

For logos and screenshots, reference the assets directory.

* **ALWAYS**: Use the provided assets in `assets/` for the project documentation.
* **ALWAYS**: Reference the image assets using markdown syntax.
* **NEVER**: Copy image assets to other project locations to avoid duplication.

---

## QA Checklist (Global)

* [x] End-to-end flow: CLI -> SDK -> LLM -> JSON File works (Current: Mocked LLM, validated with Pydantic).
* [x] Error in one file does not stop the entire batch process (Robustness verified in tests).
* [x] Metadata structure matches the business logic defined in the SDK skill (Using FileMetadata model).
* [ ] Performance: Batch processing of 5+ files is handled efficiently.

