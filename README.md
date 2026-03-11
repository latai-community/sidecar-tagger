# Sidecar-tagger (v2)

Sidecar-tagger is a **Context-Aware Metadata Engine** designed to serve as the high-performance core for semantic search UIs and OS-level file management systems. It leverages a proprietary 5-Layer pipeline to transform raw files into semantically-enriched, structured manifests with zero redundant processing.

<p align="center">
  <img src=".gemini/skills/sidecar-tagger/assets/sidecar-tagger-logo.png" alt="Sidecar-tagger Logo" width="150">
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
  - [4. Available Model Discovery](#4-available-model-discovery)
  - [5. Install Dependencies](#5-install-dependencies)
- [Running the Engine](#running-the-engine)
- [Development & Testing](#development--testing)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [License](#license)

---

## Core Philosophy: The Contextual Motor
Unlike traditional taggers, Sidecar-tagger v2 doesn't just read content; it understands **environment**. By combining OS-level facts, neighborhood patterns, and multimodal AI, it generates high-precision metadata while minimizing API costs.

## The 5-Layer Engine Architecture
The system processes each file through five sequential filters to maximize efficiency and reduce costs (it focuses on **LOCAL processing** before Cloud or AI consumption):

1. **LAYER 0: Binary Identity (Hash Gate)**: SHA-256 deduplication. metadata is cloned instantly if the file is known ($0 cost).
2. **LAYER 1: Context Enrichment**: Extraction of OS facts (parent folders, owner, timestamps) and internal headers.
3. **LAYER 2: Collective Intelligence (Clustering)**: Analyzes "Neighborhood Wisdom" to group similar files.
4. **LAYER 3: Semantic Identity (Embeddings)**: Local **ONNX vectors** (FastEmbed) detect content reuse.
5. **LAYER 4: Cognitive Analysis (Gemini 1.5)**: High-precision LLM analysis injected with previous context to eliminate hallucinations.

---

## Tech Stack
- **Language**: Python 3.11+ (Strictly Typed)
- **AI Models**: Google Gemini 1.5 Flash / Pro / 2.0
- **Local Embeddings**: FastEmbed (ONNX)
- **Metadata Format**: Pydantic-validated JSON
- **Execution**: Recursive, Context-Aware Pipeline

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

### 4. Available Model Discovery
If you receive a `404: model not found` error, your API key might not have access to the default model in your region. You can use the included discovery script to find models you **can** use.

**Run the discovery script:**
```powershell
# Windows
.\.venv\Scripts\python.exe list_models.py

# Linux / macOS
python3 list_models.py
```

**Update your .env:**
Find a model name in the output (e.g., `models/gemini-1.5-flash-8b`) and update your `.env` file:
```env
GEMINI_MODEL=gemini-1.5-flash-8b
```

### 5. Install Dependencies
Ensure your virtual environment is activated, then run:
```bash
pip install -r requirements.txt
```

---

## Running the Engine
You can run the engine against a single file or a directory.

```bash
# Basic run on a directory
python cli/main.py path/to/your/files

# Verbose mode with overwrite enabled
python cli/main.py path/to/data --verbose --overwrite
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
├── sdk/                # Core 5-Layer Engine logic
│   ├── context/        # Layer 1 & 2 (OS Facts & Clustering)
│   ├── parsers/        # Layer-agnostic extractors (PDF, XLSX, etc.)
│   ├── models/         # Pydantic schema definitions
│   └── utils/          # Layer 0 (Hashing) & Helpers
├── tests/              # Comprehensive test suite
├── .gemini/            # AI Agent skills and standards
└── list_models.py      # Model discovery utility
```

---

## License
Apache License 2.0. Developed by the Latai Community.
