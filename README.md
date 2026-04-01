# Sidecar-tagger (v2)

<p align="center">
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=fff" alt="Python 3.11+">
  </a>
  <a href="https://github.com/latai-community/sidecar-tagger/stargazers">
    <img src="https://img.shields.io/github/stars/latai-community/sidecar-tagger?style=social" alt="GitHub stars">
  </a>
  <a href="https://github.com/latai-community/sidecar-tagger/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-Apache%202.0-green" alt="License">
  </a>
  <a href="https://github.com/latai-community/sidecar-tagger/commits/main/">
    <img src="https://img.shields.io/github/last-commit/latai-community/sidecar-tagger" alt="Last commit">
  </a>
  <a href="https://github.com/latai-community/sidecar-tagger/issues">
    <img src="https://img.shields.io/github/issues/latai-community/sidecar-tagger" alt="Issues">
  </a>
  <a href="https://github.com/latai-community/sidecar-tagger/pulls">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome">
  </a>
</p>

<p align="center">
  <a href="https://ai.google.dev/gemini-api/docs">
    <img src="https://img.shields.io/badge/Google%20Gemini-886FBF?logo=googlegemini&logoColor=fff" alt="Google Gemini">
  </a>
  <a href="https://docs.pydantic.dev/">
    <img src="https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=fff" alt="Pydantic">
  </a>
  <a href="https://www.pytest.org/">
    <img src="https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=fff" alt="pytest">
  </a>
  <a href="https://github.com/embedchain/fastembed">
    <img src="https://img.shields.io/badge/FastEmbed-ONNX-orange" alt="FastEmbed">
  </a>
  <img src="https://img.shields.io/badge/CLI-Click-5ba24a" alt="CLI">
</p>

<p align="center">
  <em>Context-Aware Metadata Engine for semantic search UIs and OS-level file management systems.</em>
</p>

---

Sidecar-tagger leverages a proprietary **4-Layer Pipeline (MVP)** to transform raw files into semantically-enriched, structured manifests with zero redundant processing.

## Table of Contents
- [Core Philosophy](#core-philosophy-the-contextual-motor)
- [The 4-Layer Engine Architecture](#the-4-layer-pipeline-architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Running the Engine](#running-the-engine)
- [Development & Testing](#development--testing)
- [Project Structure](#project-structure)
- [License](#license)

---

## Core Philosophy: The Contextual Motor
Unlike traditional taggers, Sidecar-tagger v2 doesn't just read content; it understands **environment**. By combining OS-level facts, neighborhood patterns, and multimodal AI, it generates high-precision metadata while minimizing API costs.

## The 4-Layer Pipeline Architecture
The system processes each file through four sequential filters to maximize efficiency and reduce costs (it focuses on **LOCAL processing** before Cloud or AI consumption):

1. **LAYER 0: Hash Gate**: SHA-256 deduplication. Metadata is cloned instantly if the file is known ($0 cost).
2. **LAYER 1: Native + OS Metadata**: Extracts EXIFTOOL metadata (author, title, keywords) and OS facts (filename, path, size, timestamps). If confidence ≥ 0.8 → shortcut (no AI needed).
3. **LAYER 2: Embeddings (Semantic Cache)**: Local **ONNX vectors** (FastEmbed) detect content reuse. If similarity ≥ 0.9 → return cached metadata.
4. **LAYER 3: LLM + Clustering Hint**: High-precision LLM analysis (Gemini) injected with clustering context to eliminate hallucinations.

---

## Analysis Levels (Configurable)

You can choose how deep the analysis goes based on your cost/precision needs:

| Level | Layers | Cost | Precision | Use Case |
|-------|--------|------|-----------|----------|
| **minimal** | L0 | $0 | Low | Fast dedup only |
| **fast** | L0 + L1 | $0 | Medium | Quick scan with OS metadata |
| **standard** | L0 + L1 + L2 | $0 | High | Default - uses semantic cache |
| **deep** | L0 + L1 + L2 + L3 | $ | Very High | Maximum precision with AI |

---

## Tech Stack
- **Language**: Python 3.11+ (Strictly Typed)
- **AI Models**: Google Gemini 2.0 Flash
- **Local Embeddings**: FastEmbed (ONNX)
- **Metadata Format**: Pydantic-validated JSON
- **Execution**: 4-Layer Pipeline (configurable Analysis Levels)

---

## Getting Started

See the [Setup Guide](docs/01-setup.md) for complete installation instructions, including:
- Prerequisites (Python 3.11+, Git, ExifTool)
- Virtual environment setup (Windows, macOS, Linux)
- API key configuration
- Model discovery
- Troubleshooting

**Quick start:**
```bash
git clone https://github.com/latai-community/sidecar-tagger.git
cd sidecar-tagger
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Running the Engine
You can run the engine against a single file or a directory.

### Basic Commands

```bash
# Basic run on a directory (default: standard level)
python cli/main.py path/to/your/files

# Verbose mode with overwrite enabled
python cli/main.py path/to/data --verbose --overwrite
```

### Analysis Levels

Use the `--level` or `-l` flag to control analysis depth:

```bash
# minimal: Hash dedup only ($0 cost, fastest)
python cli/main.py path/to/files --level minimal

# fast: Hash + OS metadata ($0 cost, ~100ms/file)
python cli/main.py path/to/files --level fast

# standard: Hash + OS + Semantic Cache (default, $0 cost)
python cli/main.py path/to/files --level standard

# deep: Full pipeline with LLM (uses API, highest precision)
python cli/main.py path/to/files --level deep
```

### Other Options

```bash
# Custom output directory
python cli/main.py path/to/files --output-dir ./output

# Overwrite existing sidecar.json
python cli/main.py path/to/files --overwrite

# Combine options
python cli/main.py path/to/files --level deep --verbose --overwrite
```

### Granular Layer Control (for testing)

Use `--layers` to enable specific layers (overrides `--level`):

```bash
# Layer 0 only (hash dedup)
python cli/main.py path/to/files --layers 0

# Layers 0 + 1 (hash + OS metadata, no embeddings, no LLM)
python cli/main.py path/to/files --layers 0,1

# Layers 0 + 1 + 2 (hash + OS + embeddings, no LLM)
python cli/main.py path/to/files --layers 0,1,2

# Only Layer 3 (LLM only - requires file in cache)
python cli/main.py path/to/files --layers 3
```

### Custom Thresholds

```bash
# Lower confidence threshold for Layer 1 shortcut
python cli/main.py path/to/files --confidence-threshold 0.5

# Lower similarity threshold for Layer 2 cache
python cli/main.py path/to/files --similarity-threshold 0.7

# Combine with granular layers
python cli/main.py path/to/files --layers 0,1,2 --confidence-threshold 0.6
```

### Layer Reference

| Layer | Name | Description | Cost |
|-------|------|-------------|------|
| 0 | Hash Gate | SHA-256 deduplication | $0 |
| 1 | Native + OS | EXIFTOOL + file system metadata | $0 |
| 2 | Embeddings | FastEmbed semantic cache | $0 |
| 3 | LLM + Hint | Gemini with clustering context | $ |

> **Note:** Full CLI reference with all flags and examples available in [docs/03-cli-reference.md](docs/03-cli-reference.md)

---

## Development & Testing
This project follows strict engineering standards. All PRs must pass the test suite.

### Running Tests
```bash
# Run all tests using pytest
pytest
```

---

## Project Structure
```text
sidecar-tagger/
├── cli/                # CLI entry point (main.py)
├── sdk/                # Core 4-Layer Pipeline logic
│   ├── context/        # Layer 1 (OS Facts) & Clustering Hint
│   ├── parsers/        # Layer-agnostic extractors (PDF, XLSX, Images, TXT)
│   ├── models/         # Pydantic schema definitions
│   └── utils/          # Layer 0 (Hashing) & Helpers
├── docs/               # Architecture decisions & issues
├── tests/              # Comprehensive test suite
└── list_models.py      # Model discovery utility
```

---

## License
Apache License 2.0. Developed by the Latai Community.
