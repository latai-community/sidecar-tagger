# Sidecar-tagger

Sidecar-tagger is an automated metadata generation system that follows the "sidecar pattern." It analyzes source files (PDFs, spreadsheets, images) and generates a consolidated `sidecar.json` file containing LLM-derived insights, such as document type, language, tags, and confidence scores.

<p align="center">
  <img src=".gemini/skills/sidecar-tagger/assets/sidecar-tagger-logo.png" alt="Sidecar-tagger Logo" width="150">
</p>

## Key Features

- **Multi-format Support**: Designed to handle PDF, XLSX, and Image files.
- **Consolidated Metadata**: Aggregates insights from multiple files into a single `sidecar.json` manifest.
- **LLM-Powered Insights**: (Planned) Uses Large Language Models to extract deep contextual metadata.
- **CLI Interface**: Robust command-line tool for batch processing and configuration.
- **Strict Validation**: Metadata is validated against a structured schema to ensure consistency.

---

## Tech Stack

- **Language**: Python 3.9+
- **CLI Framework**: `argparse` (Standard Library)
- **Metadata Format**: JSON (Structured via SDK Processor)
- **Version Control**: Git

---

## Prerequisites

- **Python 3.9+** installed on your system.
- (Optional) A virtual environment manager like `venv` or `conda`.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/latai-community/sidecar-tagger.git
cd sidecar-tagger
```

### 2. Environment Setup (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Run the CLI

Process files to generate the consolidated metadata:

```bash
python3 cli/main.py path/to/file1.pdf path/to/file2.png --verbose
```

---

## Usage Guide

### Command Line Arguments

| Argument | Description |
| --- | --- |
| `files` | Positional: One or more files to process. |
| `--output-dir`, `-o` | Custom directory for `sidecar.json` (Default: `.`). |
| `--min-confidence`, `-m` | Float: Filter metadata by confidence score. |
| `--verbose`, `-v` | Enable detailed process logging. |
| `--overwrite` | Force replacement of existing `sidecar.json`. |

### Example

```bash
python3 cli/main.py tests/mocks/sample1.pdf tests/mocks/sample2.xlsx --verbose --overwrite
```

---

## Architecture

### Directory Structure

```text
sidecar-tagger/
├── cli/                # Entry point and argument logic
│   └── main.py         # CLI Runner
├── sdk/                # Core processing engine
│   ├── processor.py    # Metadata aggregation logic
│   ├── parsers/        # (Planned) Format-specific extraction
│   └── models/         # (Planned) Schema definitions
├── tests/              # Test suite
│   └── mocks/          # Sample files for testing
├── .gemini/            # AI Agent skills and configuration
└── .gitignore          # Version control exclusions
```

### Data Flow

1. **Input**: User provides file paths via the CLI.
2. **Validation**: CLI verifies file existence and output permissions.
3. **Processing**: `MetadataProcessor` (SDK) iterates through files.
4. **Extraction**: (Mocked) Metadata is generated based on file attributes.
5. **Consolidation**: Metadata for all files is mapped into a single dictionary.
6. **Output**: The dictionary is serialized to `sidecar.json`.

### Metadata Schema

The generated JSON follows this structure:

```json
{
  "filename.ext": {
    "doc_type": "string",
    "language": "string",
    "domain": "string",
    "category": "string",
    "context": "string",
    "tags": ["array", "of", "strings"],
    "content_date": "ISO-8601",
    "confidence": 0.0
  }
}
```

---

## Troubleshooting

### `sidecar.json` already exists
If the output file exists, the CLI will error out to prevent data loss. Use the `--overwrite` flag to replace it.

### File not found
The tool will skip missing files and print a warning in the console. Use `--verbose` to see which files were skipped.

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
