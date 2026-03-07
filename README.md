# Sidecar-tagger (v2)

Sidecar-tagger is a **Context-Aware Metadata Engine** designed to serve as the high-performance core for semantic search UIs and OS-level file management systems. It leverages a proprietary 5-Layer pipeline to transform raw files into semantically-enriched, structured manifests with zero redundant processing.

<p align="center">
  <img src=".gemini/skills/sidecar-tagger/assets/sidecar-tagger-logo.png" alt="Sidecar-tagger Logo" width="150">
</p>

## Core Philosophy: The Contextual Motor
Unlike traditional taggers, Sidecar-tagger v2 doesn't just read content; it understands **environment**. By combining OS-level facts, neighborhood patterns, and multimodal AI, it generates high-precision metadata while minimizing API costs.

## The 5-Layer Engine Architecture

The system processes each file through five sequential filters to maximize efficiency:

1.  **LAYER 0: Binary Identity (Hash Gate)**: Uses SHA-256 to detect exact duplicates. If a file has been processed before, metadata is cloned instantly ($0 cost).
2.  **LAYER 1: Context Enrichment**: Algorithmic extraction of OS facts (parent folders, file owner, timestamps) and internal properties (Office/PDF headers).
3.  **LAYER 2: Collective Intelligence (Clustering)**: Analyzes "Neighborhood Wisdom" using fuzzy string matching to group similar files and inherit tags from cluster leaders.
4.  **LAYER 3: Semantic Identity (Embeddings)**: Uses local **ONNX vectors** (FastEmbed) to detect content reuse and semantic near-matches.
5.  **LAYER 4: Cognitive Analysis (Gemini 3)**: High-precision LLM analysis injected with all previous context facts to eliminate hallucinations and reduce token usage.

---

## Key Features

- **Semantic Cache (Embedding First)**: Identifies similar documents to reuse metadata, drastically reducing latency.
- **Multimodal Vision**: Automatically uploads PDFs or Images to Gemini for visual analysis when text is insufficient.
- **Findings Reporter**: Generates a `findings.md` report highlighting duplicate savings, semantic anomalies, and top themes.
- **Strict Engineering Standards**: Built with Java-grade rigor (Strict typing, Interface-driven parsers, Semantic exceptions).
- **Extensive Format Support**: Robust handling for PDF, XLSX, Image, and TXT/MD/LOG files.

---

## Tech Stack

- **Language**: Python 3.11+ (Strictly Typed)
- **AI Models**: Google Gemini 1.5 Flash / Pro
- **Local Embeddings**: FastEmbed (ONNX)
- **Metadata Format**: Pydantic-validated JSON
- **Execution**: Recursive, Context-Aware Pipeline

---

## Getting Started

### 1. Setup Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file from `.env.example`:
```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Run the Engine
```bash
python cli/main.py path/to/data --verbose --overwrite
```

---

## Project Structure

```text
sidecar-tagger/
├── cli/                # Context-aware entry point
├── sdk/                # Core 5-Layer Engine
│   ├── context/        # Layer 1 & 2 (OS Facts & Clustering)
│   ├── parsers/        # Layer-agnostic extractors (PDF, XLSX, etc.)
│   ├── models/         # Pydantic schema definitions
│   └── utils/          # Layer 0 (Hashing) & Helpers
├── tests/              # Robust validation suite
└── .gemini/            # AI Agent skills and standards
```

## Maintenance & Standards
This project follows the **`sidecar-engine-standards`**. All contributions must include type hints, custom exceptions, and comprehensive tests. Refer to `planning.md` for the technical roadmap.

---

## License
Apache License 2.0. Developed by the Latai Community.
