# Sidecar-tagger

Sidecar-tagger is an **atomic metadata engine** designed to serve as the high-performance core for semantic search UIs and OS-level file management systems. It analyzes source files (PDFs, spreadsheets, images) and generates a persistent, semantically-enriched index.

<p align="center">
  <img src=".gemini/skills/sidecar-tagger/assets/sidecar-tagger-logo.png" alt="Sidecar-tagger Logo" width="150">
</p>

## Core Philosophy: The Atomic Motor
Unlike a full search engine, Sidecar-tagger focuses on being a **resilient and efficient data generator**. Its "product" is a consolidated index (JSON or SQLite) containing deep contextual insights and semantic vectors, ready to be consumed by any third-party UI or search interface.

## Key Features

- **Semantic Cache (Embedding First)**: Uses local vectors to identify similar documents and reuse metadata, drastically reducing API costs and latency.
- **Multimodal Analysis**: Automatically uploads PDFs or Images to Gemini 3 for visual analysis when text extraction is insufficient (e.g., scanned documents).
- **Local Embeddings (ONNX)**: Generates 384-dimensional semantic vectors locally ($0 cost) using `FastEmbed` for instant similarity searches.
- **Recursive Indexing**: Process entire directory trees with a single command, unifying results into a structured manifest.
- **Robust Error Handling**: Graceful fallback logic with a `needs_review` flag for unreadable or ambiguous files.
- **LLM-Powered Intelligence**: Deep analysis of document context, domain, and tags using Google Gemini 3.

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
│   ├── parsers/        # Format-specific extraction (PDF, XLSX, Image)
│   └── models/         # Pydantic schema definitions
├── tests/              # Test suite (Unit and Integration)
├── .gemini/            # AI Agent skills and roadmap
└── .gitignore          # Version control exclusions
```

### Data Flow

1. **Input**: User provides file/directory paths via the CLI.
2. **Identification**: `MetadataProcessor` (SDK) identifies file formats and recursively scans directories.
3. **Semantic Cache Check**: Generates a local vector and searches for similar documents in the existing index to avoid redundant LLM calls.
4. **Extraction**:
    - **PDF**: Extracts text via `pdfplumber`. If text is missing, renders page thumbnails for visual analysis.
    - **XLSX**: Extracts sheet data and samples via `openpyxl`.
    - **Image**: Extracts technical metadata via `Pillow`.
5. **Multimodal LLM Analysis**: Sends content (and optionally the full PDF or Image) to Gemini 3 for deep semantic tagging.
6. **Consolidation**: Stores metadata and local vectors into a persistent index.

### Metadata Schema

The generated JSON follows this structure:

```json
{
  "path/to/file.ext": {
    "doc_type": "string",
    "language": "string",
    "domain": "string",
    "category": "string",
    "context": "string",
    "tags": ["array", "of", "strings"],
    "content_date": "string (ISO-8601 or partial)",
    "confidence": 0.0,
    "needs_review": false,
    "embedding_vector": [0.123, -0.456, "..."]
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
