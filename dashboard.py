import os
import json
import asyncio
import subprocess
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import datetime

app = FastAPI(title="Extraction Kit Dashboard")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# New storage paths
STORAGE_DIR = os.path.join(BASE_DIR, "data")
MANIFEST_PATH = os.path.join(STORAGE_DIR, "manifest.json")
LOGS_DIR = os.path.join(STORAGE_DIR, "logs")
SEEDS_PATH = os.path.join(BASE_DIR, "config", "url-seeds.md")

# Models
class ScrapeRequest(BaseModel):
    url: str

class ScrapeRun(BaseModel):
    run_id: str
    status: str
    processed_at: str
    url_count: int

# Helpers
def get_latest_log_file():
    """Finds the most recent log file in storage/logs"""
    if not os.path.exists(LOGS_DIR):
        return None
    try:
        files = [os.path.join(LOGS_DIR, f) for f in os.listdir(LOGS_DIR) if f.endswith(".md") or f.endswith(".log")]
        if not files:
            return None
        return max(files, key=os.path.getmtime)
    except Exception:
        return None

async def run_extraction_script(url: str = None):
    """Runs the local_extraction_runner.py script as a subprocess"""
    print(f"Starting extraction for: {url if url else 'batch mode'}")

    cmd = ["python", "local_extraction_runner.py"]
    if url:
        cmd.extend(["--url", url])

    # Using subprocess to run the script in the same environment
    process = subprocess.Popen(
        cmd,
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    print(f"Extraction finished with code {process.returncode}")
    if process.returncode != 0:
        print(f"Error: {stderr}")

# Routes
@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/api/history")
def get_history():
    """Reads the master manifest from storage/manifest.json"""
    if not os.path.exists(MANIFEST_PATH):
        return {"runs": [], "message": "No runs found yet."}

    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            runs = json.load(f)
            # Manifest is already a list of runs now
            return {"runs": runs}
    except Exception as e:
        return {"error": str(e), "runs": []}

@app.get("/api/logs/latest")
def get_latest_logs():
    """Returns content of the latest log file"""
    log_file = get_latest_log_file()
    if not log_file:
        return {"content": "Waiting for logs..."}

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except Exception:
        return {"content": "Error reading log file."}

@app.post("/api/scrape")
async def trigger_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Triggers a single URL extraction"""
    # Trigger Background Task with specific URL
    background_tasks.add_task(run_extraction_script, request.url)

    return {"status": "accepted", "message": f"Queued scrape for {request.url}"}

app.mount("/", StaticFiles(directory="dashboard", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
