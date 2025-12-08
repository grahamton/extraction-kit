import React, { useState, useEffect } from 'react';
import { X, Save, Settings } from 'lucide-react';

const SettingsModal = ({ isOpen, onClose, apiUrl }) => {
  const [formData, setFormData] = useState({
    chunking_strategy: 'markdown-header',
    allowed_domains: [],
    ignore_patterns: [],
    depth_limit: 1,
    max_pages: 10
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetch(`${apiUrl}/api/config`)
        .then(res => res.json())
        .then(data => {
          // Merge defaults in case config is empty
          setFormData(prev => ({ ...prev, ...data }));
          setLoading(false);
        })
        .catch(err => {
          console.error("Failed to load config", err);
          setLoading(false);
        });
    }
  }, [isOpen, apiUrl]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (type === 'checkbox') {
      // Toggle specific for this app? No, we don't use checkboxes yet.
    } else if (name === 'allowed_domains' || name === 'ignore_patterns') {
      // Handle comma-separated lists
      setFormData(prev => ({ ...prev, [name]: value.split(',').map(s => s.trim()) }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleListChange = (e, field) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value.split(',').map(s => s.trim()) }));
  };

  const saveConfig = async () => {
    setLoading(true);
    try {
      await fetch(`${apiUrl}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 2000);
      setLoading(false);
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-gray-900 border border-gray-700 w-full max-w-lg rounded-2xl shadow-2xl flex flex-col max-h-[90vh]">

        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-800">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Settings className="w-5 h-5 text-gray-400" />
            Pipeline Settings
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6 overflow-y-auto">

          {/* Chunking Strategy */}
          <div className="space-y-3">
            <label className="text-sm font-bold text-gray-400 uppercase tracking-wider">Chunking Strategy (RAG)</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setFormData({ ...formData, chunking_strategy: 'markdown-header' })}
                className={`p-3 rounded-lg border text-sm font-medium transition-all ${formData.chunking_strategy === 'markdown-header'
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-gray-800 border-gray-700 text-gray-400 hover:bg-gray-700'
                  }`}
              >
                Header Split (Recommended)
              </button>
              <button
                onClick={() => setFormData({ ...formData, chunking_strategy: 'none' })}
                className={`p-3 rounded-lg border text-sm font-medium transition-all ${formData.chunking_strategy === 'none'
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-gray-800 border-gray-700 text-gray-400 hover:bg-gray-700'
                  }`}
              >
                No Chunking (Single File)
              </button>
            </div>
            <p className="text-xs text-gray-500">
              Use "Header Split" for chatbots. Use "No Chunking" for reading manually.
            </p>
          </div>

          <hr className="border-gray-800" />

          {/* Limits */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm text-gray-400">Depth Limit</label>
              <input
                type="number"
                name="depth_limit"
                value={formData.depth_limit}
                onChange={handleChange}
                className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-white focus:border-blue-500 outline-none"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-gray-400">Max Pages</label>
              <input
                type="number"
                name="max_pages"
                value={formData.max_pages}
                onChange={handleChange}
                className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-white focus:border-blue-500 outline-none"
              />
            </div>
          </div>

          {/* Patterns */}
          <div className="space-y-2">
            <label className="text-sm text-gray-400">Ignore Patterns (Comma separated)</label>
            <input
              type="text"
              value={formData.ignore_patterns.join(', ')}
              onChange={(e) => handleListChange(e, 'ignore_patterns')}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg p-2 text-white focus:border-blue-500 outline-none font-mono text-xs"
            />
          </div>

        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-800 flex justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 text-gray-400 hover:text-white font-medium">Cancel</button>
          <button
            onClick={saveConfig}
            disabled={loading}
            className="px-6 py-2 bg-green-600 hover:bg-green-500 text-white font-bold rounded-lg flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            {success ? "Saved!" : "Save Changes"}
          </button>
        </div>

      </div>
    </div>
  );
};

// Simple Loader for the modal
const Loader = ({ className }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
);

export default SettingsModal;
