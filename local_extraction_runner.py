import asyncio
import os
import json
import datetime
import re
import argparse
from typing import List, Dict

# Set shared browser path BEFORE importing crawlee/playwright
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = r"C:\tools\playwright_browsers"

# Third party imports
import requests
import fitz  # PyMuPDF
from crawlee.crawlers._playwright import PlaywrightCrawler
from crawlee.configuration import Configuration
from typing import Any
from trafilatura import extract

# Configuration
# Removed Local LLM Constants
TARGETS_DIR = "config"

# Dynamic Run Configuration
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
RUN_ID = f"{TIMESTAMP}_run"

# New Storage Structure
STORAGE_DIR = "data"
RAW_DIR = os.path.join(STORAGE_DIR, "scrapes", RUN_ID, "raw")
OUTPUT_DIR = os.path.join(STORAGE_DIR, "scrapes", RUN_ID, "clean")
MEDIA_DIR = os.path.join(STORAGE_DIR, "media", RUN_ID)
LOGS_DIR = os.path.join(STORAGE_DIR, "logs")

# Initialize OpenAI Client - REMOVED for Middleware Version

def load_config() -> Dict:
    """Loads configuration from _01_targets/config.json"""
    config_path = os.path.join(TARGETS_DIR, "config.json")
    if not os.path.exists(config_path):
        print(f"Warning: {config_path} not found. Using defaults.")
        return {"allowed_domains": [], "ignore_patterns": [], "depth_limit": 1}

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

async def get_seed_urls() -> List[str]:
    """Reads seed URLs from _01_targets/url-seeds.md"""
    seeds_path = os.path.join(TARGETS_DIR, "url-seeds.md")
    if not os.path.exists(seeds_path):
        print(f"Error: {seeds_path} not found.")
        return []

    with open(seeds_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Simple extraction: find lines starting with http
    urls = [line.strip() for line in content.splitlines() if line.startswith("http")]
    return urls

def extract_text_from_pdf(url: str, slug: str) -> str:
    """Downloads PDF, saves it to _04_media, and extracts text using PyMuPDF"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Save PDF to _04_media (Archival)
        pdf_filename = f"{slug}.pdf"
        pdf_path = os.path.join(MEDIA_DIR, pdf_filename)
        with open(pdf_path, "wb") as f:
            f.write(response.content)
        print(f"  -> Archived PDF to {pdf_path}")

        # Extract text from memory (or file) behavior
        with fitz.open(stream=response.content, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF {url}: {e}")
        return ""

async def process_and_save(url: str, raw_content: str, manifest: List[Dict], config: Dict):
    """Refactored pipeline: Raw Scrape -> Save Raw -> Chunk -> Save Chunks"""
    slug = url.split("/")[-1].replace(".html", "").replace(".pdf", "") or "index"
    if url.lower().endswith(".pdf"):
        slug += "_pdf"

    # 3. Skip Enrichment (Middleware Mode)
    # Treat raw_content (Trafilatura output) as the content to process
    print(f"  -> Processing raw content (Enrichment Skipped)...")
    content_to_process = raw_content

    filename = f"{slug}_raw.md"
    filepath = os.path.join(RAW_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Source: {url}\n\n{content_to_process}")

    print(f"  -> Saved to {filepath}")

    # Metadata Defaulting (No LLM to extract these)
    audience = "General"
    intent = "Inform"
    tags_list = "[local, extraction]"

    # 5. Chunking / Saving
    chunking_strategy = config.get("chunking_strategy", "markdown-header")

    # ALWAYS save the full file first
    full_filename = f"{slug}_full.md"
    full_filepath = os.path.join(OUTPUT_DIR, full_filename)

    full_frontmatter = f"""---
title: {slug.replace('-', ' ').title()}
source_title: {slug}
url: {url}
run_id: {RUN_ID}
tags: {tags_list}
audience: [{audience}]
intent: [{intent}]
---\n\n"""

    with open(full_filepath, "w", encoding="utf-8") as f:
        f.write(full_frontmatter + content_to_process)
    print(f"  -> Saved full content to: {full_filename}")

    if chunking_strategy == "none":
        print(f"  -> Chunking disabled by config.")
        chunks = []

    else:
        # Smart Chunking Strategy
        print(f"  -> Chunking content (Strategy: {chunking_strategy})...")
        raw_splits = re.split(r'\n## ', content_to_process)

        # Merge buffer for small chunks
        chunks = []
        buffer = ""

        for split in raw_splits:
            if not split.strip(): continue

            # Re-add the header marker
            current_text = split if split == raw_splits[0] else f"## {split}"

            if len(current_text) < 200:
                buffer += current_text + "\n\n"
            else:
                if buffer:
                    current_text = buffer + current_text
                    buffer = ""
                chunks.append(current_text)

        if buffer:
            if chunks:
                chunks[-1] += "\n\n" + buffer
            else:
                chunks.append(buffer)

    if chunks:
        chunk_count = 0
    for i, chunk in enumerate(chunks):
        if not chunk.strip(): continue
        chunk_count += 1

        # Construct YAML Frontmatter
        chunk_slug = f"{slug}_chunk-{i+1:02d}"
        chunk_filename = f"{chunk_slug}.md"
        chunk_path = os.path.join(OUTPUT_DIR, chunk_filename)

        frontmatter = f"""---
title: {slug.replace('-', ' ').title()} - Part {i+1}
source_title: {slug}
url: {url}
section: Part {i+1}
run_id: {RUN_ID}
tags: {tags_list}
audience: [{audience}]
intent: [{intent}]
---

"""
        content_body = chunk

        with open(chunk_path, "w", encoding="utf-8") as f:
            f.write(frontmatter + content_body)

        print(f"     -> Wrote chunk: {chunk_filename}")

    # Update Manifest
    manifest.append({
        "url": url,
        "slug": slug,
        "chunks": chunk_count,
        "status": "success",
        "processed_at": datetime.datetime.now().isoformat()
    })

async def main():
    parser = argparse.ArgumentParser(description="Local Extraction Runner")
    parser.add_argument("--url", help="Single URL to scrape (overrides seed file)")
    args = parser.parse_args()

    print(f"Starting Local Extraction Pipeline ({RUN_ID}) - MIDDLEWARE MODE")

    # Load Config
    config = load_config()
    print(f"Loaded config: {config}")

    if args.url:
        print(f"Single Mode detected. Target: {args.url}")
        seed_urls = [args.url]
    else:
        seed_urls = await get_seed_urls()

    print(f"Found {len(seed_urls)} URL(s) to process.")

    # Ensure directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(MEDIA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Manifest to track all URLs
    crawled_manifest = []

    crawlee_config = Configuration(storage_dir="data/.crawlee")
    crawler = PlaywrightCrawler(
        configuration=crawlee_config,
        max_requests_per_crawl=40, # Configurable
        headless=True,
    )

    @crawler.router.default_handler
    async def request_handler(context: Any) -> None:
        url = context.request.url
        print(f"Processing {url}...")

        # Check against ignore patterns (basic check)
        for pattern in config.get("ignore_patterns", []):
            if pattern in url.lower():
                print(f"Skipping {url} (matches ignore pattern '{pattern}')")
                return

        # 1. Check Content Type - Seeds or Direct Links
        if url.lower().endswith(".pdf"):
            print(f"  -> Detected PDF. Downloading and OCR-ing...")
            slug = url.split("/")[-1].replace(".pdf", "")
            markdown = extract_text_from_pdf(url, slug)
            if markdown:
                await process_and_save(url, markdown, crawled_manifest, config)
            else:
                 print(f"Failed to read PDF {url}")
        else:
            # 1b. Get HTML for normal pages
            html = await context.page.content()

            # 1c. Manual PDF discovery and INLINE processing
            print(f"  -> Scanning for PDFs to process inline...")
            pdf_links = await context.page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a'))
                    .map(a => a.href)
                    .filter(href => href.toLowerCase().endsWith('.pdf'));
            }""")

            pdf_section_content = ""

            for pdf_url in pdf_links:
                print(f"    -> Found PDF: {pdf_url}. Extracting to merge...")
                slug = pdf_url.split("/")[-1].replace(".pdf", "")
                pdf_text = extract_text_from_pdf(pdf_url, slug)
                if pdf_text:
                     pdf_section_content += f"\n\n# ATTACHED PDF CONTENT: {slug}\n\n{pdf_text}\n\n---\n"

            # 2. Convert to Markdown (Trafilatura)
            markdown = extract(html, output_format="markdown", include_links=True)

            # MERGE: Append PDF content to main markdown
            if pdf_section_content:
                print(f"  -> Merging {len(pdf_links)} PDF(s) into main content...")
                markdown += f"\n\n{pdf_section_content}"

            await process_and_save(url, markdown, crawled_manifest, config)

    await crawler.run(seed_urls)

    # Save JSON Manifest
    # Save JSON Manifest - Append to master manifest in storage root
    master_manifest_path = os.path.join(STORAGE_DIR, "manifest.json")

    # Load existing if present
    if os.path.exists(master_manifest_path):
        try:
            with open(master_manifest_path, "r", encoding="utf-8") as f:
                master_manifest = json.load(f)
        except:
            master_manifest = []
    else:
        master_manifest = []

    # Create run entry
    run_entry = {
         "run_id": RUN_ID,
         "mode": "single" if args.url else "batch",
         "config": config,
         "timestamp": datetime.datetime.now().isoformat(),
         "items": crawled_manifest
    }
    master_manifest.append(run_entry)

    with open(master_manifest_path, "w", encoding="utf-8") as f:
        json.dump(master_manifest, f, indent=2)
    print(f"Updated run manifest at {master_manifest_path}")

    print("Extraction Complete.")

    # 6. Logging
    log_path = os.path.join(LOGS_DIR, "run-log.md")
    timestamp_log = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"""
| {timestamp_log} | {len(seed_urls)} Seeds | Middleware Mode | {RUN_ID} |
"""
    # Ensure log file exists with header if new
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("# Extraction Run Log\n\n| Date | Seeds | Model | Run ID | Notes |\n|---|---|---|---|---|")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(f"Logged run to {log_path}")

if __name__ == "__main__":
    asyncio.run(main())
