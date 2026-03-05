---
name: sidecar-tagger
description: >
  Overall orchestrator for the Sidecar-tagger project. High-level vision, 
  project structure, and integration between SDK and CLI components.
  Trigger: General project overview, architecture decisions, or cross-component workflows.
metadata:
  version: "1.0"
  author: latai-community
  scope: [root]
---

## Overview

Sidecar-tagger is an automated metadata generation system. It follows a "sidecar pattern" where every source file gets a corresponding `.json` file containing LLM-derived insights.

| Project Layer | Responsibility | Reference Skill |
|---------------|----------------|-----------------|
| **CLI** | User interface, flags, and batch input | `sidecar-tagger-cli` |
| **SDK** | Multi-format parsing and LLM orchestration | `sidecar-tagger-sdk` |
| **Schema** | Truth source for the metadata JSON structure | `sidecar-tagger-sdk` |

---

## Critical Rules (Global)

### Project Architecture

- **ALWAYS**: Keep a strict separation between CLI logic (argparse) and SDK logic (processing).
- **ALWAYS**: Generate a consolidated `sidecar.json` containing metadata for all input files in the batch.
- **NEVER**: Modify the original source files; the tool is strictly read-only for inputs.

### Workflow Orchestration

- **ALWAYS**: Initialize the SDK from the CLI with the user-provided configurations (confidence, output-dir).
- **ALWAYS**: Log the start and end of the global process in the console.
- **NEVER**: Commit generated `.json` sidecars to the core repository; they should be ignored via `.gitignore` in test folders.

---
## Directory Structure

```text
sidecar-tagger/
├── cli/                # Entry point and argument logic
├── sdk/                # Core processing engine
│   ├── parsers/        # PDF, XLSX, Image specialized logic
│   └── models/         # Pydantic/JSON schemas
├── tests/              # Integration and unit tests
└── SKILL.md            # This orchestrator
```

---

## Media Assets
For more information on media assets, logos and screenshots, see the [Asset directory](./assets/).

- **ALWAYS**: Use the provided assets for the project.
- **NEVER**: Use assets from other projects.
- **ALWAYS**: Reference the image assets using markdown syntax.
- **NEVER**: Copy the image assets to the project to avoid duplication.
---

## QA Checklist (Global)
- [ ] End-to-end flow: CLI -> SDK -> LLM -> JSON File works without manual intervention.
- [ ] Error in one file does not stop the entire batch process (robustness).
- [ ] Metadata structure matches the business logic defined in the SDK skill.
- [ ] Performance: Batch processing of 5+ files is handled efficiently.