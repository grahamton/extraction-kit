const API_BASE = 'http://localhost:8000/api';

async function triggerScrape() {
  const urlInput = document.getElementById('urlInput');
  const url = urlInput.value.trim();
  const btn = document.getElementById('scrapeBtn');

  if (!url) {
    alert("Please enter a URL");
    return;
  }

  try {
    btn.disabled = true;
    btn.innerText = "Queuing...";

    const res = await fetch(`${API_BASE}/scrape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });

    const data = await res.json();
    if (data.status === 'accepted') {
      alert("Scrape started! Check the logs.");
      urlInput.value = "";
    } else {
      alert("Error: " + JSON.stringify(data));
    }
  } catch (e) {
    console.error(e);
    alert("Failed to contact server.");
  } finally {
    btn.disabled = false;
    btn.innerText = "Start Extraction";
    loadHistory(); // Refresh table potentially (although it runs in background)
  }
}

async function loadHistory() {
  const tbody = document.getElementById('historyTableBody');
  const countEl = document.getElementById('runCount');

  try {
    const res = await fetch(`${API_BASE}/history`);
    const data = await res.json();

    if (!data.runs || data.runs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">No runs found.</td></tr>';
      countEl.innerText = "0";
      return;
    }

    countEl.innerText = data.runs.length;

    // Reverse order to show newest first if multiple
    const runs = data.runs.reverse();

    tbody.innerHTML = runs.map(run => `
            <tr>
                <td>${run.run_id}</td>
                <td>${new Date(run.generated_at).toLocaleString()}</td>
                <td>${run.seeds}</td>
                <td>${run.items}</td>
                <td><span style="color: #238636">Success</span></td>
            </tr>
        `).join('');

  } catch (e) {
    console.error(e);
    tbody.innerHTML = '<tr><td colspan="5" style="color:red">Failed to load history. Is server running?</td></tr>';
  }
}

async function loadLogs() {
  const logWindow = document.getElementById('logWindow');
  try {
    const res = await fetch(`${API_BASE}/logs/latest`);
    const data = await res.json();

    if (data.content) {
      // Check if it changed to avoid heavy DOM ops? For now just replace.
      logWindow.innerText = data.content;
      // Auto scroll to bottom
      logWindow.scrollTop = logWindow.scrollHeight;
    }
  } catch (e) {
    // Silent fail for logs
    console.log("Log poll failed");
  }
}

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
  loadHistory();
  loadLogs();

  // Poll logs every 2 seconds
  setInterval(loadLogs, 2000);
});
