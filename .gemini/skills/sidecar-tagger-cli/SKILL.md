---
name: sidecar-tagger-cli
description: >
  Specifies the CLI behavior and architecture for the Sidecar-tagger v2 tool. 
  Covers argument parsing, Findings generation, and error handling standards.
  Trigger: When working on sidecar-tagger/cli/ or defining new CLI commands/flags.
metadata:
  version: "2.0"
  author: latai-community
  scope: [sidecar-tagger/cli]
---

## Overview

The Sidecar-tagger CLI v2 is the user interface for the **5-Layer Engine**. It manages recursive file scanning, standard flag enforcement, and generates value-added reports.

### Primary Responsibilities

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| Scanner   | Recursive Path Discovery | `os.walk` with extension filtering. |
| Reporter  | Value-added Analysis | `FindingsReporter` (`findings.md`). |
| Runner    | Orchestration | Exception-aware execution loop. |

---

## Critical Rules

### Argument & Flag Standards

- **ALWAYS**: Accept multiple positional inputs (files or directories).
- **ALWAYS**: Implement `--output-dir`, `--min-confidence`, `--verbose`, and `--overwrite`.
- **ALWAYS**: Use `logging` levels mapped to the `--verbose` flag.

### Exception-Aware Flow

- **ALWAYS**: Catch `SidecarException` and return Exit Code `2` for system failures.
- **ALWAYS**: Return Exit Code `0` only if the manifest and findings report are generated.
- **NEVER**: Allow data loss; check for `sidecar.json` existence before processing unless `--overwrite` is set.

### Value-Added Output

- **ALWAYS**: Call the `FindingsReporter` after processing to generate `findings.md`.
- **ALWAYS**: Print the final location of both the `sidecar.json` and the `findings.md` report.

---

## QA Checklist (CLI v2)

- [ ] CLI correctly identifies all supported extensions (`.pdf`, `.xlsx`, `.txt`, `.md`, etc.).
- [ ] Recursive scanning ignores hidden folders and follows links safely.
- [ ] `--verbose` mode shows details of Layer 0 (Hash) and Layer 3 (Embedding) hits.
- [ ] Findings report accurately summarizes duplicate savings.
- [ ] CLI returns Exit Code `3` for unexpected fatal errors.

---

## Related Skills
- **[sidecar-engine-standards](../sidecar-engine-standards/SKILL.md)**: Global quality mandates.
- **[sidecar-tagger-sdk](../sidecar-tagger-sdk/SKILL.md)**: Core engine logic.
- **[sidecar-tagger-test](../sidecar-tagger-test/SKILL.md)**: Verification of CLI behavior.
