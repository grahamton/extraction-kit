# Extraction Kit

A **Local AI + Python** pipeline for turning websites into RAG-ready knowledge chunks. Use this to build high-quality context for chatbots and research assistants.

## Features
- **Local Control:** Runs strictly on your machine.
- **AI Enrichment:** Uses a local LLM (via LM Studio) to clean and enrich content *before* chunking.
- **Smart Parsing:** Handles PDFs, removes marketing fluff, and structures metadata (Audience, Intent).
- **RAG Ready:** Outputs standalone markdown chunks with YAML frontmatter.

## Setup

1.  **Install Dependencies:**
    You will need Python 3.9+ installed.
    ```bash
    pip install playwright crawlee trafilatura openai pymupdf
    playwright install
    ```

2.  **Start LM Studio:**
    - Load a vision-capable model (recommended: `qwen2.5-vl-7b`).
    - Start the Local Server on port `1234`.

## Usage

### 1. Batch Extraction
Process a list of URLs defined in your config.

1.  **Add Targets:**
    Edit `config/url-seeds.md` and paste the URLs you want to extract (one per line).
2.  **Run the Pipeline:**
    ```bash
    python local_extraction_runner.py
    ```

### 2. Single URL Extraction
Process a single URL directly from the command line.

```bash
python local_extraction_runner.py --url https://example.com/page
```

## Output Structure

All outputs are saved to the `data/` directory.

- **`data/scrapes/{RunID}/raw/`**: Full, enriched markdown files.
- **`data/scrapes/{RunID}/clean/`**: Final, chunked markdown files with metadata (ready for RAG).
- **`data/media/{RunID}/`**: Archived PDFs and images.
- **`data/logs/`**: Execution logs.
- **`data/manifest.json`**: Master record of all runs and processed URLs.

## Configuration

- **`config/config.json`**: Set ignored patterns (e.g., "contact", "login") and allowed domains.
- **`config/multi-url-agent-prompt.md`**: The system prompt used by the Local LLM for enrichment.
- **`templates/`**: Markdown templates (Page, PDF) injected into the prompt to guide the LLM's formatting.

## Project Structure

```
extraction-kit/
├── config/                 # Configuration files (seeds, prompt, json)
├── data/                   # ALL outputs (scrapes, logs, media)
├── docs/                   # Strategies and guides
├── templates/              # Prompt templates
└── local_extraction_runner.py  # Main execution script
```
