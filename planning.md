# Sidecar-Core v2: The 5-Layer Contextual Engine

> **Status:** PLANNING / APPROVED
> **Date:** 2026-03-07
> **Trigger:** Activate this context when the user mentions "brainstorming", "roadmap planning", "v2 architecture", or "optimization strategy".

## Executive Summary
This document outlines the architectural transformation of Sidecar-tagger from a linear "File-to-AI" processor into a **5-Layer Contextual Engine**. The goal is to maximize local computational efficiency (CPU), minimize AI token usage (Cost), and drastically increase semantic precision through "Context Injection".

---

## The 5-Layer Architecture

Data flows sequentially through these layers. Each layer acts as a filter or enhancer.

### LAYER 0: Binary Identity (The "Hash Gate")
*   **Objective:** Zero-cost deduplication.
*   **Mechanism:** SHA-256 Checksum.
*   **Logic:**
    1.  Calculate file hash.
    2.  Check global index for existence.
    3.  **IF MATCH:** Mark as `duplicate_of: {original_id}`. Copy metadata 1:1. **STOP.**
    4.  **IF NEW:** Proceed to Layer 1.
*   **Value:** Eliminates redundant processing for exact file copies (backups, usb copies).

### LAYER 1: Context Enrichment (The "Local Fact Builder")
*   **Objective:** Extract objective facts from the OS and file headers without AI.
*   **Mechanism:** Algorithmic Extraction (Regex, OS Stat, Header Parsers).
*   **Captured Data:**
    *   **OS Context:** `filename`, `parent_folder` (e.g., "Covid", "Invoices"), `owner` (e.g., "David"), `creation_date` (e.g., "2020-03").
    *   **Internal Props:** `docProps/core.xml` (Office), `/Info` (PDF). Extracts "Author", "Title", "Company".
*   **Output:** `LocalContext` object (e.g., `{"author": "David", "year": "2020", "topic_hint": "Pandemia"}`).

### LAYER 2: Collective Intelligence (The "Cluster Manager")
*   **Objective:** Leverage "Neighborhood Wisdom". If neighbors are "Vaccine Reports", this file likely is too.
*   **Mechanism:** Dynamic Clustering (Levenshtein Distance / Token Jaccard Similarity).
*   **Logic:**
    1.  Compare filename/path with recently processed files.
    2.  **IF Similarity > 80%:** Inherit `category` and `tags` from neighbors as "Strong Hints".
    3.  **IF Similarity < 40%:** Treat as "Orphan" (Potential Anomaly).
*   **Output:** `ClusterHint` object.

### LAYER 3: Semantic Identity (The "Embedding Check")
*   **Objective:** Detect content reuse (e.g., same contract, different signature).
*   **Mechanism:** ONNX Vector Generation (Content + LocalContext + ClusterHint).
*   **Logic:**
    1.  Generate Vector.
    2.  Search Vector DB (`sidecar.json`).
    3.  **IF Cosine Similarity > 0.98:** Reuse metadata with `confidence: 0.99`. **STOP.**
    4.  **IF NEW:** Proceed to Layer 4.

### LAYER 4: Cognitive Analysis (The "AI Final Boss")
*   **Objective:** High-precision classification using all accumulated context.
*   **Mechanism:** LLM (Gemini 3 Flash).
*   **Prompt Strategy:** "Context Injection".
    > "Analyze this file.
    > **Facts:** Created by 'David' in 2020 (Pandemia era).
    > **Hints:** Neighbors are 'Vaccine Reports'.
    > **Content:** [Extract]..."
*   **Value:** Reduces hallucinations by grounding the AI in OS-level facts.

---

## Cross-Cutting Concerns

### The "Findings & Suggestions" Reporter
A post-processing routine that generates a value-added report (`findings.md`) for the human user.

**Report Sections:**
1.  **Duplicate Savings:** List of files skipped due to Layer 0 (Hash).
2.  **Cluster Insights:** "95% of files in `/Admin` relate to 'Invoices'".
3.  **Anomalies:** "File `party.jpg` found in `/Contracts` (Semantic Outlier)".
4.  **Context timeline:** "Most documents date from March 2020".

---

## Implementation Roadmap

1.  **Phase 1 (The Foundation):** Implement Layer 0 (Hash) and Layer 1 (OS Metadata).
2.  **Phase 2 (The Intelligence):** Implement Layer 2 (Clustering) and Layer 3 (Embeddings Integration).
3.  **Phase 3 (The Brain):** Update Layer 4 to accept the "Super-Prompt" with injected context.
4.  **Phase 4 (The Reporter):** Implement the `FindingsGenerator`.
