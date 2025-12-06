# extraction-kit

A **Local AI + Python** pipeline for turning websites into RAG-ready knowledge chunks. Use this to build high-quality context for chatbots and research assistants.

## Features
- **Local Control:** Runs strictly on your machine.
- **AI Enrichment:** Uses a local LLM (via LM Studio) to clean and enrich content *before* chunking.
- **Smart Parsing:** Handles PDFs, removes marketing fluff, and structures metadata (Audience, Intent).
- **RAG Ready:** Outputs standalone markdown chunks with YAML frontmatter.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install playwright crawlee trafilatura openai pymupdf
    playwright install
    ```
2.  **Start LM Studio:**
    - Load a vision-capable model (e.g., `qwen2.5-vl-7b`).
    - Start the Local Server on port `1234`.

## Usage

1.  **Add Targets:**
    Edit `_01_targets/url-seeds.md` and paste the URLs you want to extract.
    Configure filters in `_01_targets/config.json`.

2.  **Run the Pipeline:**
    ```bash
    python local_extraction_runner.py
    ```

3.  **View Results:**
    Outputs are organized by Timestamped Run ID folders (e.g. `2025-12-06_12-30-00_run`).
    - **Raw Extracts:** `_02_scrapes_raw/{RunID}/`
    - **Final Chunks:** `_03_scrapes_clean/{RunID}/`
    - **Logs:** `_06_logs/run-log.md`

## Folder Guide
- **`_00_system/`**:
    - **Active Prompt:** `multi-url-agent-prompt.md`. This is the brain of the agent.
    - **Archive:** Legacy prompts and instructions.
- **`_01_targets/`**:
    - `url-seeds.md`: List of URLs to start crawling.
    - `config.json`: Configuration for ignoring patterns, allowed domains, etc.
- **`_02_scrapes_raw/`**: Contains the full, unchunked markdown files from each run.
- **`_03_scrapes_clean/`**: Contains the final, chunked, and enriched metadata files ready for RAG.
- **`_04_media/`**: Archival storage for downloaded PDFs and images captured during the crawl.
- **`_05_templates/`**:
    - Markdown templates injected into the prompt to tell the LLM how to format pages and PDFs.
- **`_06_logs/`**:
    - Execution logs tracking success, failure, and run parameters.
- **`docs/specs/`**:
    - Technical reference documents and schemas (not active code).
- **`storage/`**:
    - Internal temporary cache for the crawler. Safe to delete if you want a fresh "clean slate" crawl.
