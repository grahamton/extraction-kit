# Extraction Kit: High-Fidelity RAG Processor

**Solving the "Garbage In, Garbage Out" problem for Enterprise RAG piplelines.**

This toolkit is a specialized ingestion layer designed to transform messy, disjointed web content (CMS pages, PDFs, loose text) into **pristine, synthesized Markdown** optimized for Large Language Models.

## The Problem
Standard scrapers dump raw HTML and isolated PDF text into your vector database. This leads to:
*   **Context Fragmentation**: The chatbot doesn't know the PDF "User Guide" belongs to the "Product Overview" page.
*   **Noise**: Navigation menus, footers, and marketing fluff confuse the model.
*   **Weak Retrieval**: Without accurate metadata (Audience, Intent), the RAG system retrieves irrelevant chunks.

## The Solution
The Extraction Kit acts as an intelligent pre-processing layer that "cleans our own data" before it hits the AI.

### Key Use Cases
1.  **Unified Synthesis**: Automatically merges a Web Page and its attached PDFs into a single, cohesive "Source of Truth" document. No more fragmented answer retrieval.
2.  **Strict Metadata Extraction**: Uses a local AI agent to classify content by **Audience** (e.g., Developer vs. Admin) and **Intent** (Configure vs. Purchase), enabling precise filtering.
3.  **RAG-Ready Output**: Produces clean, structured Markdown with YAML frontmatter, ready for immediate embedding.

## Features
*   **Headless Ingestion**: Built to run as a backend service or API layer.
*   **Local AI Privacy**: Runs entirely on your infrastructure (using Local LLMs like via LM Studio) to sanitize data without external leaks.
*   **Smart Chunking**: preserving semantic context better than naive character-splitting.
*   **Dashboard**: Includes a React UI for easy testing, configuration, and demoing of the extraction quality.

## Quick Start

### 1. Interactive Demo (Dashboard)
Use the UI to visually test the extraction quality on specific URLs.
```bash
start_dashboard.bat
```
*   Open `http://localhost:5173`
*   Enter a URL -> **Run Extraction** -> View the "Clean" output.

### 2. Batch Processing (CLI)
Integrate directly into your data pipelines.
```bash
# Process a single URL
python local_extraction_runner.py --url https://example.com/target-page

# Run from a list of seeds
python local_extraction_runner.py
```

## Output Structure
Data is saved to `data/scrapes/{RunID}/clean/`.
*   **`*_full.md`**: The complete, synthesized document (Best for GPT-4/Context windows).
*   **`*_chunk-XX.md`**: Semantic chunks ready for vector databases.

## Technology
*   **Core**: Python, Playwright (Headless Browser), PyMuPDF
*   **AI Layer**: OpenAI-compatible client (Targeting Local LLMs)
*   **UI**: React, Vite
