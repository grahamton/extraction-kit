from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import threading
import time
import os
import queue

app = Flask(__name__)
CORS(app) # Enable CORS for localhost React app

import json

# Global State
JOBS = []
LOGS = ["// Server Ready. Waiting for commands..."]
LOG_QUEUE = queue.Queue()
CONFIG_PATH = os.path.join("config", "config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(new_config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(new_config, f, indent=2)

def run_extraction_process(url, job_id):
    """
    Runs the existing local_extraction_runner.py as a subprocess.
    Captures stdout/stderr and pushes to LOGS.
    """
    cmd = ["python", "local_extraction_runner.py", "--url", url]

    # Update Job Status
    for job in JOBS:
        if job['id'] == job_id:
            job['status'] = 'RUNNING'
            break

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=os.getcwd()
        )

        # Helper to read stream
        def read_stream(stream, prefix=""):
            for line in iter(stream.readline, ''):
                clean_line = line.strip()
                if clean_line:
                    timestamp = time.strftime("%H:%M:%S")
                    log_msg = f"[{timestamp}] {prefix}{clean_line}"
                    LOG_QUEUE.put(log_msg)
            stream.close()

        # Threads to read stdout/stderr non-blocking
        t_out = threading.Thread(target=read_stream, args=(process.stdout,))
        t_err = threading.Thread(target=read_stream, args=(process.stderr, "[SYS] "))
        t_out.start()
        t_err.start()

        process.wait() # Wait for finish
        t_out.join()
        t_err.join()

        # Completion Status
        status = 'COMPLETE' if process.returncode == 0 else 'FAILED'
        for job in JOBS:
            if job['id'] == job_id:
                job['status'] = status
                job['duration'] = 'Done' # TODO real duration
                break

        LOG_QUEUE.put(f"// Process finished with code {process.returncode}")

    except Exception as e:
        LOG_QUEUE.put(f"[ERROR] Subprocess failed: {e}")
        for job in JOBS:
            if job['id'] == job_id:
                job['status'] = 'FAILED'

def background_log_worker():
    """Moves logs from Queue to List safely"""
    while True:
        try:
            msg = LOG_QUEUE.get(timeout=1)
            LOGS.append(msg)
            # Keep logs manageable
            if len(LOGS) > 1000:
                LOGS.pop(0)
        except queue.Empty:
            continue

# Start log worker
threading.Thread(target=background_log_worker, daemon=True).start()

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    return jsonify(JOBS)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(LOGS)

@app.route('/api/config', methods=['GET'])
def get_config_route():
    return jsonify(load_config())

@app.route('/api/config', methods=['POST'])
def update_config_route():
    try:
        new_config = request.json
        save_config(new_config)
        return jsonify({"status": "updated", "config": new_config})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/job/start', methods=['POST'])
def start_job():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    job_id = f"JOB-{len(JOBS)+1:03d}"
    new_job = {
        "id": job_id,
        "url": url,
        "status": "QUEUED",
        "items": 0,
        "duration": "0:00"
    }
    JOBS.insert(0, new_job)

    # Start thread
    thread = threading.Thread(target=run_extraction_process, args=(url, job_id))
    thread.start()

    return jsonify({"job_id": job_id, "status": "started"})

if __name__ == '__main__':
    print("Starting Flask API on port 5000...")
    app.run(port=5000, debug=True, use_reloader=False)
