# Extraction Kit Workflow Guide

This guide explains the typical workflow for using the Extraction Kit to build a knowledge base.

## 1. Preparation (The "Targeting" Phase)

Before running the tool, you need to decide what to capture.

1.  **Identify Sources:** Find the URLs of the documentation, help articles, or blog posts you want to ingest.
2.  **Configure Seeds:** Open `config/url-seeds.md`. Paste your URLs here, one per line.
    *   *Tip:* Keep scopes small (10-50 URLs) per run for easier management.
3.  **Check Configuration:** Open `config/config.json`.
    *   Ensure `allowed_domains` includes the sites you are scraping.
    *   Add any new patterns to `ignore_patterns` (e.g., if you see a lot of "signup" or "cart" pages).

## 2. Extraction (The "Running" Phase)

Run the automated pipeline.

*   **Batch Mode:** Run `python local_extraction_runner.py` to process everything in your seed file.
*   **Single Page Test:** Run `python local_extraction_runner.py --url <URL>` to test a specific page/PDF immediately without editing the seed file.

**What happens during a run:**
1.  **Crawl:** The tool loads the page (or downloads the PDF).
2.  **Enrich:** The content is sent to your local LLM. The LLM cleans up the text, removes noise, and adds metadata (Audience, Intent).
3.  **Chunk:** The enriched text is split into logical blocks (e.g., by header).
4.  **Save:** Files are saved to `data/scrapes/{RunID}/`.

## 3. Review & Usage (The "RAG" Phase)

After the run completes:

1.  **Check the Logs:** Look at `data/logs/run-log.md` to see if any URLs failed.
2.  **Inspect the Output:** Go to `data/scrapes/{LatestRunID}/clean/`.
    *   These `.md` files are your "Knowledge Chunks".
    *   They contain YAML frontmatter with tags, audience, and source info.
3.  **Ingest:** Copy these files into your RAG database, Vector Store, or Knowledge Base (like Obsidian or Notion).

## 4. Maintenance

*   **Clean Up:** You can safely delete old runs in `data/scrapes/` if you have already imported them into your final system.
*   **Manifest:** The `data/manifest.json` file keeps a history of everything you've ever scraped.
