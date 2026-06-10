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
  function health() {
    return getJSON('/api/health');
  }

  // Most recent saved analysis, or null when none exist yet.
  async function latestAnalysis() {
    try {
      const data = await getJSON('/api/analyses/latest');
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
      if (job.status === 'done') return job.data;
      if (job.status === 'error') throw new Error(job.error || 'Analysis failed');
    }
  }

  window.QA_API = { API_BASE, health, latestAnalysis, analyze };
})();
