import React, { useState, useEffect, useRef } from 'react';
import { Play, Clipboard, Loader, CheckCircle, Zap, Code, Clock, Database, Terminal, Settings } from 'lucide-react';
import SettingsModal from './components/SettingsModal';

// --- CONFIG ---
const INITIAL_URL = 'https://example.com/data-target';
const API_BASE_URL = 'http://localhost:5000';
const ACCENT_COLOR = 'text-green-400';
const BG_COLOR = 'bg-gray-950';

const initialJobs = [
  { id: 'JOB-004', url: 'https://site4.net/page', status: 'COMPLETE', items: 25, duration: '0:15' },
  { id: 'JOB-003', url: 'https://api.docs/v2', status: 'RUNNING', items: 12, duration: '0:08' },
];

const getJobStatusConfig = (status) => {
  switch (status) {
    case 'RUNNING':
      return { classes: 'bg-yellow-900/40 text-yellow-300 border-yellow-500', icon: <Loader className="w-4 h-4 mr-1 animate-spin" /> };
    case 'COMPLETE':
      return { classes: 'bg-green-900/40 text-green-300 border-green-500', icon: <CheckCircle className="w-4 h-4 mr-1" /> };
    case 'FAILED':
      return { classes: 'bg-red-900/40 text-red-300 border-red-500', icon: <Code className="w-4 h-4 mr-1" /> };
    case 'QUEUED':
    default:
      return { classes: 'bg-blue-900/40 text-blue-300 border-blue-500', icon: <Clock className="w-4 h-4 mr-1" /> };
  }
};

const JobCard = ({ job }) => {
  const { classes, icon } = getJobStatusConfig(job.status);
  return (
    <div className={`p-4 rounded-xl font-mono text-sm border-l-4 ${classes} transition-all hover:brightness-110 mb-3`}>
      <div className="flex justify-between items-start">
        <p className="font-semibold text-white/90">{job.id}</p>
        <div className="flex items-center text-xs font-bold uppercase tracking-wider">
          {icon}
          {job.status}
        </div>
      </div>
      <p className="text-xs truncate text-gray-400 mt-2 font-medium">{job.url}</p>
    </div>
  );
};

const SimplifiedStatus = ({ logs }) => {
  // Helper to strip ANSI codes
  const stripAnsi = (str) => str.replace(/\x1b\[[0-9;]*m/g, '');

  // Get the last 3 non-empty logs and clean them
  const recentLogs = logs
    .map(stripAnsi)
    .filter(l => l.trim().length > 0)
    .slice(-3);

  const lastStatus = recentLogs[recentLogs.length - 1] || "Ready for input...";

  return (
    <div className="mt-8">
      <h2 className="text-lg font-bold mb-3 flex items-center gap-2 text-white">
        <Terminal className="w-5 h-5 text-gray-400" />
        Current Status
      </h2>
      <div className={`p-6 rounded-xl bg-gray-900/80 border border-gray-700/50 shadow-inner flex flex-col justify-center min-h-[120px]`}>

        {/* Main Status Line */}
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.5)]"></div>
          <p className="text-green-400 font-mono text-base md:text-lg font-semibold truncate leading-tight">
            {lastStatus}
          </p>
        </div>

        {/* History hints (faded) */}
        <div className="mt-4 pt-3 border-t border-gray-800 space-y-1">
          {recentLogs.slice(0, -1).map((log, i) => (
            <p key={i} className="text-gray-600 font-mono text-xs truncate">{log}</p>
          ))}
        </div>

      </div>
    </div>
  );
};

// -------------------------------------------------------------
// MAIN APP COMPONENT
// -------------------------------------------------------------
const App = () => {
  const [jobs, setJobs] = useState(initialJobs);
  const [logs, setLogs] = useState(["// System Initialized"]);
  const [url, setUrl] = useState(INITIAL_URL);
  const [isApiReady, setIsApiReady] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  const startNewJob = async (targetUrl) => {
    // Optimistic Update
    const tempId = `JOB-PENDING`;
    setLogs(prev => [...prev, `[INFO] Requesting extract: ${targetUrl}`]);

    try {
      const response = await fetch(`${API_BASE_URL}/api/job/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: targetUrl }),
      });

      if (!response.ok) throw new Error('API Error');
      const result = await response.json();
      setLogs(prev => [...prev, `[SUCCESS] Job Started: ${result.job_id}`]);

    } catch (error) {
      setLogs(prev => [...prev, `[ERROR] Connection failed. Is server.py running?`]);
    }
  };

  // Polling
  useEffect(() => {
    if (!isApiReady) return;
    const pollApi = async () => {
      try {
        const jobRes = await fetch(`${API_BASE_URL}/api/jobs`);
        const jobData = await jobRes.json();
        if (Array.isArray(jobData)) setJobs(jobData);

        const logRes = await fetch(`${API_BASE_URL}/api/logs`);
        const logData = await logRes.json();
        if (Array.isArray(logData)) {
          // Only update if changed to avoid jitter
          setLogs(prev => logData.length !== prev.length ? logData : prev);
        }
      } catch (e) { /* silent fail */ }
    };
    const intervalId = setInterval(pollApi, 2000);
    return () => clearInterval(intervalId);
  }, [isApiReady]);


  return (
    <div className={`min-h-screen ${BG_COLOR} text-gray-100 p-4 sm:p-8 font-sans`}>

      {/* App Header */}
      <header className="flex justify-between items-center mb-10 border-b border-gray-800 pb-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center shadow-lg shadow-green-900/20">
            <Database className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Data Runner</h1>
            <p className="text-xs font-mono text-gray-500 uppercase tracking-widest mt-1">Extraction Kit v2.1</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setShowSettings(true)}
            className="p-2 rounded-lg bg-gray-900 border border-gray-700 text-gray-400 hover:text-white hover:bg-gray-800 transition-all"
            title="Pipeline Settings"
          >
            <Settings className="w-5 h-5" />
          </button>
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-900 border border-gray-800">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-xs font-medium text-gray-400">System Online</span>
          </div>
        </div>
      </header>

      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        apiUrl={API_BASE_URL}
      />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* --- MAIN CONTROL (Left 8 cols) --- */}
        <div className="lg:col-span-8">

          {/* Input Card */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-900/50 p-1 rounded-2xl border border-gray-800 shadow-xl">
            <div className="bg-gray-950/80 rounded-xl p-8 backdrop-blur-sm">
              <label className="block text-sm font-medium text-gray-400 mb-2 ml-1">Process New URL</label>
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/article"
                  className="flex-grow bg-gray-900 border border-gray-700 text-white text-lg rounded-xl px-4 py-3 focus:ring-2 focus:ring-green-500/50 outline-none transition-all placeholder-gray-600 font-mono"
                />
                <button
                  onClick={() => startNewJob(url)}
                  disabled={!url}
                  className="bg-green-600 hover:bg-green-500 text-white font-bold py-3 px-8 rounded-xl shadow-lg shadow-green-900/30 transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <Play className="w-5 h-5 fill-current" />
                  RUN
                </button>
              </div>
            </div>
          </div>

          <SimplifiedStatus logs={logs} />

        </div>

        {/* --- SIDEBAR (Right 4 cols) --- */}
        <div className="lg:col-span-4 pl-0 lg:pl-4 border-l border-gray-800/50">
          <h2 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Clipboard className="w-4 h-4" />
            Job Queue
          </h2>
          <div className="space-y-3">
            {jobs.length === 0 && <p className="text-gray-600 text-sm italic">No active jobs.</p>}
            {jobs.map(job => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};

export default App;
