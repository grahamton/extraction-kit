import asyncio
import os
import json
import datetime
import re
from typing import List, Dict

# Set shared browser path BEFORE importing crawlee/playwright
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = r"C:\tools\playwright_browsers"

# Third party imports
import requests
import fitz  # PyMuPDF
from crawlee.crawlers._playwright import PlaywrightCrawler
from typing import Any
from trafilatura import extract
from openai import OpenAI

# Configuration
LM_STUDIO_URL = "http://127.0.0.1:1234/v1"
MODEL_ID = "qwen/qwen2.5-vl-7b"
TARGETS_DIR = "_01_targets"

# Dynamic Run Configuration
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
RUN_ID = f"{TIMESTAMP}_run"

RAW_DIR = os.path.join("_02_scrapes_raw", RUN_ID)
OUTPUT_DIR = os.path.join("_03_scrapes_clean", RUN_ID)
MEDIA_DIR = os.path.join("_04_media", RUN_ID)
LOGS_DIR = "_06_logs"

# Initialize OpenAI Client (points to local LM Studio)
client = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")

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

async def run_enrichment_agent(content: str, url: str) -> str:
    """Sends content to local LLM for enrichment"""

    prompt_path = os.path.join("_00_system", "multi-url-agent-prompt.md")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    else:
        system_prompt = "Enrich the content."

    # Load and Inject Templates
    page_template_path = os.path.join("_05_templates", "page-extraction-template.md")
    pdf_template_path = os.path.join("_05_templates", "pdf-extraction-template.md")

    templates_content = "\n\n# TEMPLATES\n"
    if os.path.exists(page_template_path):
        with open(page_template_path, "r", encoding="utf-8") as f:
            templates_content += f"## Page Template:\n{f.read()}\n"
    if os.path.exists(pdf_template_path):
        with open(pdf_template_path, "r", encoding="utf-8") as f:
            templates_content += f"## PDF Template:\n{f.read()}\n"

    system_prompt += templates_content

    # Truncate content to avoid context limits (approx 20k chars)
    user_prompt = f"Extract and enrich the following content from {url}:\n\n{content[:20000]}"

    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            top_p=0.95,
            frequency_penalty=1.1,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"LLM Enrichment failed: {e}")
        return f"Error enriching content: {e}"

async def process_and_save(url: str, raw_content: str, manifest: List[Dict]):
    """Refactored pipeline: Enrich -> Save Raw -> Chunk -> Save Chunks"""
    slug = url.split("/")[-1].replace(".html", "").replace(".pdf", "") or "index"
    if url.lower().endswith(".pdf"):
        slug += "_pdf"

    # 3. Enrich with LLM
    print(f"  -> Enriching content with Local LLM...")
    enriched_output = await run_enrichment_agent(raw_content, url)

    filename = f"{slug}_raw.md"
    filepath = os.path.join(RAW_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Source: {url}\n\n{enriched_output}")

    print(f"  -> Saved to {filepath}")

    # 5. Chunking
    print(f"  -> Chunking content...")
    chunks = re.split(r'\n## ', enriched_output)

    chunk_count = 0
    for i, chunk in enumerate(chunks):
        if not chunk.strip(): continue
        chunk_count += 1

        # Construct YAML Frontmatter
        chunk_slug = f"{slug}_chunk-{i+1:02d}"
        chunk_filename = f"{chunk_slug}.md"
        chunk_path = os.path.join(OUTPUT_DIR, chunk_filename)

        audience_match = re.search(r"(?:- )?\**Audience\**:\s*(.*?)(?=\n(?:- |\n|$))", chunk, re.IGNORECASE | re.DOTALL)
        intent_match = re.search(r"(?:- )?\**Intent\**:\s*(.*?)(?=\n(?:- |\n|$))", chunk, re.IGNORECASE | re.DOTALL)

        def clean_meta(text):
            if not text: return "General"
            clean = re.sub(r"\*\*|__", "", text)
            clean = re.sub(r"\n\s*", " ", clean)
            return clean.strip()

        audience = clean_meta(audience_match.group(1)) if audience_match else "General"
        intent = clean_meta(intent_match.group(1)) if intent_match else "Inform"

        frontmatter = f"""---
title: {slug.replace('-', ' ').title()} - Part {i+1}
source_title: {slug}
url: {url}
section: Part {i+1}
run_id: {RUN_ID}
tags: [local, extraction]
audience: [{audience}]
intent: [{intent}]
---

"""
        content_body = f"## {chunk}" if i > 0 else chunk

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
    print(f"Starting Local Extraction Pipeline ({RUN_ID})...")

    # Load Config
    config = load_config()
    print(f"Loaded config: {config}")

    seed_urls = await get_seed_urls()
    print(f"Found {len(seed_urls)} seed URLs.")

    # Ensure directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(MEDIA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Manifest to track all URLs
    crawled_manifest = []

    crawler = PlaywrightCrawler(
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
                await process_and_save(url, markdown, crawled_manifest)
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

            for pdf_url in pdf_links:
                print(f"    -> Found PDF: {pdf_url}. Processing inline...")
                slug = pdf_url.split("/")[-1].replace(".pdf", "") + "_pdf"
                pdf_text = extract_text_from_pdf(pdf_url, slug)
                if pdf_text:
                     await process_and_save(pdf_url, pdf_text, crawled_manifest)

            # 2. Convert to Markdown (Trafilatura)
            markdown = extract(html, output_format="markdown", include_links=True)
            await process_and_save(url, markdown, crawled_manifest)

    await crawler.run(seed_urls)

    # Save JSON Manifest
    manifest_path = os.path.join(RAW_DIR, "url_manifest.json")
    final_manifest = {
        "run_id": RUN_ID,
        "config": config,
        "seeds": seed_urls,
        "items": crawled_manifest,
        "generated_at": datetime.datetime.now().isoformat()
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(final_manifest, f, indent=2)
    print(f"Saved run manifest to {manifest_path}")

    print("Extraction Complete.")

    # 6. Logging
    log_path = os.path.join(LOGS_DIR, "run-log.md")
    timestamp_log = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"""
| {timestamp_log} | {len(seed_urls)} Seeds | {MODEL_ID} | {RUN_ID} |
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
