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

To connect this middleware to your official Work API:

1.  Open `azure_client_template.py`.
2.  Paste your **API Key** and **Endpoint** in the `if __name__ == "__main__":` block (or import the class into your own script).
3.  The `demo_app.py` shows how to use this client in the "Azure Integration" tab.

## 📁 Project Structure

*   `local_extraction_runner.py`: The core engine. Runs headless.
*   `demo_app.py`: The visual UI for demos.
*   `data/`: Where scraped markdown files are saved.
*   `config/`: Contains your prompt assets (e.g., `synthesis-prompt.md`).
