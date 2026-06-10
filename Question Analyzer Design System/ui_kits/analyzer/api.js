// Shared API client for the analyzer backend.
// Uses relative URLs when served by the Flask server; falls back to
// localhost:5000 when the page is opened directly from disk (file://).
(function () {
  const API_BASE = location.protocol === 'file:' ? 'http://localhost:5000' : '';
  const POLL_INTERVAL_MS = 600;

  async function getJSON(path) {
    const response = await fetch(`${API_BASE}${path}`);
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.success === false) {
      throw new Error(data.error || `Request failed (${response.status})`);
    }
    return data;
  }

  // Health check — resolves with the health payload, including provider status.
  // Pass the provider that will be used so the right backend gets verified.
  function health(provider) {
    return getJSON(`/api/health${provider ? `?provider=${encodeURIComponent(provider)}` : ''}`);
  }

  // Most recent saved analysis, or null when none exist yet.
  // Also records its id (window.ANALYSIS_ID) so exports target what's shown.
  async function latestAnalysis() {
    try {
      const data = await getJSON('/api/analyses/latest');
      window.ANALYSIS_ID = data.id;
      return data.data;
    } catch (err) {
      return null;
    }
  }

  // Summaries of all saved analyses, newest first.
  async function listAnalyses() {
    const data = await getJSON('/api/analyses');
    return data.analyses;
  }

  // Full results of one saved analysis.
  async function getAnalysis(id) {
    const data = await getJSON(`/api/analyses/${encodeURIComponent(id)}`);
    window.ANALYSIS_ID = id;
    return data.data;
  }

  // Delete a saved analysis.
  async function deleteAnalysis(id) {
    const response = await fetch(`${API_BASE}/api/analyses/${encodeURIComponent(id)}`,
      { method: 'DELETE' });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.success === false) {
      throw new Error(data.error || `Delete failed (${response.status})`);
    }
  }

  // Download URL for a saved analysis (format: 'md' | 'csv' | 'json').
  function exportUrl(id, format) {
    return `${API_BASE}/api/analyses/${encodeURIComponent(id)}/export?format=${format}`;
  }

  // Week-in-Review stats for the latest analysis, or null when unavailable.
  async function latestWeekly() {
    try {
      const data = await getJSON('/api/analyses/latest/weekly');
      return data.data;
    } catch (err) {
      return null;
    }
  }

  // Start an analysis job and poll until it finishes.
  // onProgress receives {stage, completed, total} as the backend reports it.
  async function analyze(content, { provider = 'ollama', threshold = 0.85 } = {}, onProgress) {
    const response = await fetch(`${API_BASE}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, provider, threshold }),
    });
    const started = await response.json().catch(() => ({}));
    if (!response.ok || !started.success) {
      throw new Error(started.error || `Could not start analysis (${response.status})`);
    }

    for (;;) {
      await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
      const job = await getJSON(`/api/jobs/${started.job_id}`);
      if (job.progress && onProgress) onProgress(job.progress);
      if (job.status === 'done') {
        window.ANALYSIS_ID = job.analysis_id;
        return job.data;
      }
      if (job.status === 'error') throw new Error(job.error || 'Analysis failed');
    }
  }

  window.QA_API = { API_BASE, health, latestAnalysis, listAnalyses, getAnalysis,
    deleteAnalysis, exportUrl, latestWeekly, analyze };

  // ---- Analysis settings (provider + threshold), persisted locally ----
  const SETTINGS_KEY = 'qa-analysis-settings';
  const DEFAULT_SETTINGS = { provider: 'ollama', threshold: 0.85 };

  function getSettings() {
    try {
      const stored = JSON.parse(localStorage.getItem(SETTINGS_KEY));
      return { ...DEFAULT_SETTINGS, ...(stored || {}) };
    } catch (err) {
      return { ...DEFAULT_SETTINGS };
    }
  }

  function setSettings(settings) {
    const merged = { ...getSettings(), ...settings };
    try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(merged)); } catch (err) { /* private mode */ }
    return merged;
  }

  // Seed defaults from the server's configuration the first time.
  async function loadServerDefaults() {
    try {
      const data = await getJSON('/api/config');
      if (!localStorage.getItem(SETTINGS_KEY) && data.config) {
        setSettings({ provider: data.config.provider, threshold: data.config.threshold });
      }
    } catch (err) { /* backend offline; local defaults apply */ }
    return getSettings();
  }

  window.QA_SETTINGS = { get: getSettings, set: setSettings, loadServerDefaults };
})();
