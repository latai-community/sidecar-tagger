---
name: sidecar-tagger-cli
description: >
  Specifies the CLI behavior and architecture for the Sidecar-tagger tool. 
  Covers argument parsing logic, flag standards, and execution flow.
  Trigger: When working on sidecar-tagger/cli/ or defining new CLI commands/flags.
metadata:
  version: "1.0"
  author: latai-community
  scope: [sidecar-tagger/cli]
---

## Overview

The Sidecar-tagger CLI is the primary entry point for automated metadata extraction. It must handle file inputs and configuration flags with zero ambiguity.

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| Parser    | Argument/Flag Parsing | Python `argparse` (StdLib) |
| Validator | Path/File verification | `os.path` or `pathlib` |
| Runner    | Orchestration | Main execution loop |

---

## Critical Rules

### Argument Handling

- **ALWAYS**: Accept 1 to N files as positional arguments (`nargs='+'`).
- **ALWAYS**: Use `argparse.FileType` or manual `pathlib.Path` validation.
- **NEVER**: Hardcode file paths or input names.

### Flag Standards (The "Big Four")

- **ALWAYS**: Implement `--output-dir` (`-o`) for custom JSON destination.
- **ALWAYS**: Implement `--min-confidence` (`-m`) as a `float` (default: 0.0).
- **ALWAYS**: Implement `--verbose` (`-v`) for process logging.
- **ALWAYS**: Implement `--overwrite` as a boolean flag to replace existing `.json` files.

### Execution Flow

- **ALWAYS**: Return Exit Code `0` on success and `1` on any runtime error.
- **ALWAYS**: Print a summary of "Files Processed" vs "Files Skipped" at the end.
- **NEVER**: Silently fail if an input file is missing.

---

## Quick Reference: CLI Template

1. Initialize `ArgumentParser(description="Sidecar Tagger CLI")`.
2. Define positional `files` argument.
3. Define optional flags with short and long versions.
4. Parse and pass `Namespace` object to the core logic.

---

## QA Checklist

- [ ] Every flag has a clear, English help description.
- [ ] Positional arguments support multiple files (batch processing).
- [ ] `--verbose` mode actually outputs internal logic steps.
- [ ] Output filenames follow the pattern: `<original_name>.<ext>.json`.
- [ ] The `--help` command displays all options correctly.