# Extraction Kit Middleware - Demo Guide

This branch (`middleware-mode`) is configured as a lightweight middleware layer suitable for enterprise environments. It strips out local LLM dependencies and focuses on pure data extraction.

## 🚀 Quick Start (Demo Mode)

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Demo UI**
    ```bash
    streamlit run demo_app.py
    ```
    This will open a browser window with a clean interface to test the scraper.

## 🔌 Connecting to Azure OpenAI

**No Coding Required!**
1.  Open the **Sidebar** in the Demo App.
2.  Expand "Amzure OpenAI Settings".
3.  Paste your **API Key** and **Endpoint** (and Deployment Name).
4.  Go to the **"Azure Integration"** tab after a scrape to run the enrichment.

*Alternatively, you can edit `azure_client_template.py` if you want to hardcode them for scripts.*

## 📁 Project Structure

*   `local_extraction_runner.py`: The core engine. Runs headless.
*   `demo_app.py`: The visual UI for demos.
*   `data/`: Where scraped markdown files are saved.
*   `config/`: Contains your prompt assets (e.g., `synthesis-prompt.md`).
