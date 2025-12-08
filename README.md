# Extraction Kit

A **Local AI + Python** pipeline for turning websites into RAG-ready knowledge chunks. Use this to build high-quality context for chatbots and research assistants. Now with a **React Dashboard** for easy management.

## Features
- **Modern Dashboard:** A sleek React UI to run jobs, view status, and configure settings.
- **Local Control:** Runs strictly on your machine.
- **AI Enrichment:** Uses a local LLM (via LM Studio) to clean and enrich content *before* chunking.
- **Smart Parsing:** Handles PDFs, removes marketing fluff, and structures metadata (Audience, Intent).
- **RAG Ready:** Outputs standalone markdown chunks with YAML frontmatter.
- **Configurable Strategy:** Choose between "Header Split" (for RAG) or "Single File" (for reading).

## Setup

1.  **Install Dependencies:**
    You will need Python 3.9+ and Node.js installed.
    ```bash
    # Python Backend
    pip install playwright crawlee trafilatura openai pymupdf flask flask-cors
    playwright install

    # React Frontend
    cd dashboard_react
    npm install
    cd ..
    ```

2.  **Start LM Studio:**
    - Load a vision-capable model (recommended: `qwen2.5-vl-7b`).
    - Start the Local Server on port `1234`.

## Usage

### 1. Dashboard (Recommended)
The easiest way to run the kit. This starts both the Backend API and the Frontend UI.
```bash
start_dashboard.bat
```
- Open `http://localhost:5173` (or port shown).
- Enter a URL and click **RUN**.
- Use the **Settings Gear** to toggle Chunking or set limits.

### 2. Command Line
Run the pipeline directly without the UI.

**Batch Mode (from config):**
```bash
python local_extraction_runner.py
```

**Single URL:**
```bash
python local_extraction_runner.py --url https://example.com/page
```

## Output Structure

All outputs are saved to the `data/` directory.

- **`data/scrapes/{RunID}/clean/`**:
    - `*_full.md`: The complete enriched document (Always saved).
    - `*_chunk-XX.md`: Individual chunks split by header (if enabled).
- **`data/scrapes/{RunID}/raw/`**: Raw markdown before AI processing.
- **`data/media/{RunID}/`**: Archived PDFs and images.
- **`data/logs/`**: Execution logs.
- **`data/manifest.json`**: Master record of all runs.

## Configuration

You can edit `config/config.json` manually or use the **Settings UI** in the dashboard.

- **`chunking_strategy`**:
    - `"markdown-header"`: Splits by `## ` (Default).
    - `"none"`: Skips splitting, only saves the full file.
- **`allowed_domains`**: Whitelist for crawling.
- **`ignore_patterns`**: URL patterns to skip (e.g., "login", "contact").

## Project Structure

```
extraction-kit/
├── dashboard_react/        # React Frontend Application
├── config/                 # Configuration files
├── data/                   # ALL outputs (scrapes, logs, media)
├── templates/              # Prompt templates
├── local_extraction_runner.py  # Main Python Pipeline
├── server.py               # Flask API wrapper
└── start_dashboard.bat     # Launcher script
```
