# Sidecar-tagger (v2)

Sidecar-tagger is a **Context-Aware Metadata Engine** designed to serve as the high-performance core for semantic search UIs and OS-level file management systems. It leverages a proprietary **4-Layer Pipeline (MVP)** to transform raw files into semantically-enriched, structured manifests with zero redundant processing.

<p align="center">
  <img src="assets/sidecar-tagger-logo.png" alt="Sidecar-tagger Logo" width="150">
</p>

## Table of Contents
- [Core Philosophy](#core-philosophy-the-contextual-motor)
- [The 5-Layer Engine Architecture](#the-5-layer-engine-architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone and Navigate](#1-clone-and-navigate)
  - [2. Environment Setup (Python)](#2-environment-setup-python)
  - [3. Configure API Keys](#3-configure-api-keys)
  - [4. Install Dependencies](#4-install-dependencies)
  - [5. Available Model Discovery](#5-available-model-discovery)
- [Running the Engine](#running-the-engine)
- [Development & Testing](#development--testing)
- [Troubleshooting](#troubleshooting)
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

## Prerequisites
Before you begin, ensure you have the following installed:
- **Python 3.11 or higher**
- **Git**
- **A Google Gemini API Key** (See [Configure API Keys](#3-configure-api-keys))

---

## Getting Started

### 1. Clone and Navigate
```bash
git clone https://github.com/latai-community/sidecar-tagger.git
cd sidecar-tagger
```

### 2. Environment Setup (Python)
It is highly recommended to use a virtual environment to avoid conflicts with other Python projects.

#### **Windows 11 (PowerShell)**
```powershell
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

#### **Linux / macOS**
```bash
# Create the virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate
```

### 3. Configure API Keys
The engine requires a **Google Gemini API Key** for Layer 4 analysis.

1. **Get your key:** Visit the [Google AI Studio](https://aistudio.google.com/app/apikey) to generate a free or pay-as-you-go API key.
2. **Setup your environment file:**
   - Copy the example file: `cp .env.example .env`
   - Open `.env` and replace `your_api_key_here` with your actual key.

**Example `.env` file:**
```env
# Your actual key looks like this: AIzaSy...
GEMINI_API_KEY=AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6
GEMINI_MODEL=gemini-2.0-flash
LLM_PROVIDER=gemini
```

### 4. Install Dependencies
Ensure your virtual environment is activated, then run:
```bash
pip install -r requirements.txt
```

### 5. Available Model Discovery
If you receive a `404: model not found` error, your API key might not have access to the default model in your region. You can use the included discovery script to find models you **can** use.

**Quick test (recommended - no quota used):**
```powershell
# Windows
.\.venv\Scripts\python.exe list_models.py

# Linux / macOS
python3 list_models.py
```

This uses `count_tokens` to verify model availability without spending your quota.

**Full test (uses quota):**
```powershell
# Windows
.\.venv\Scripts\python.exe list_models.py --mode full

# Linux / macOS
python3 list_models.py --mode full
```

This uses actual `generate_content` requests to confirm models respond correctly. Useful to check if your quota is exhausted.

**Update your .env:**
After running the script, copy the recommended model name from the output and update your `.env` file:
```env
GEMINI_MODEL=gemini-2.5-flash
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

---

## Development & Testing
This project follows strict engineering standards. All PRs must pass the test suite.

### Running Tests
```bash
# Run all tests using pytest
pytest
```

---

## Troubleshooting

### Windows "Execution Policy" Error
If you cannot activate the virtual environment on Windows, run this command in an Administrator PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "ImportError: cannot import name..."
If tests fail with an `ImportError`, ensure you have installed the requirements (`pip install -r requirements.txt`) and that you are running `pytest` from the project root with the virtual environment activated.

### "GEMINI_API_KEY not found"
Ensure your `.env` file is in the root directory and contains the correct variable name: `GEMINI_API_KEY`.

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
