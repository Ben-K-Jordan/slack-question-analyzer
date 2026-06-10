// Modal shell + Upload-transcript and Connect-email flows.
function Modal({ open, onClose, children, width = 480 }) {
  const [render, setRender] = React.useState(open);
  const [vis, setVis] = React.useState(false);
  React.useEffect(() => {
    if (open) { setRender(true); const r = requestAnimationFrame(() => setVis(true)); return () => cancelAnimationFrame(r); }
    setVis(false); const id = setTimeout(() => setRender(false), 240); return () => clearTimeout(id);
  }, [open]);
  React.useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose(); };
    if (open) window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);
  if (!render) return null;
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div onClick={onClose} style={{ position: 'absolute', inset: 0, background: 'rgba(22,22,22,.55)', opacity: vis ? 1 : 0, transition: 'opacity 220ms var(--ease-entrance)' }} />
      <div style={{ position: 'relative', width, maxWidth: '92vw', background: '#fff', boxShadow: 'var(--shadow-overlay)', opacity: vis ? 1 : 0, transform: vis ? 'none' : 'translateY(14px) scale(.97)', transition: 'opacity 240ms var(--ease-entrance), transform 240ms var(--ease-entrance)' }}>
        {children}
      </div>
    </div>
  );
}

function ModalHead({ title, sub, onClose }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', padding: '22px 24px 16px' }}>
      <div>
        <div style={{ fontSize: 20, fontWeight: 400, letterSpacing: '-.01em' }}>{title}</div>
        {sub ? <div style={{ fontSize: 13.5, color: 'var(--text-secondary)', marginTop: 6, lineHeight: 1.45, maxWidth: 380 }}>{sub}</div> : null}
      </div>
      <button onClick={onClose} aria-label="Close" style={{ width: 32, height: 32, border: 'none', background: 'transparent', cursor: 'pointer', color: 'var(--text-secondary)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', flex: '0 0 auto' }}>
        <Icon name="x" size={18} />
      </button>
    </div>
  );
}

// ---- Upload transcript ----
function UploadModal({ open, onClose, onImported }) {
  const { Button, FileDropzone } = window.QuestionAnalyzerDesignSystem_03a921;
  const [file, setFile] = React.useState(null);
  const [phase, setPhase] = React.useState('pick'); // pick | running | done | error
  const [progress, setProgress] = React.useState(0);
  const [results, setResults] = React.useState(null);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    if (!open) {
      setFile(null);
      setPhase('pick');
      setProgress(0);
      setResults(null);
      setError(null);
    }
  }, [open]);

  const steps = ['Parsing transcript', 'Extracting questions', 'Embedding & grouping', 'Ranking by frequency'];
  const [activeStep, setActiveStep] = React.useState(0);

  // Map backend progress events onto the step list and percent bar.
  const onProgress = ({ stage, completed, total }) => {
    if (stage === 'starting') { setActiveStep(0); setProgress(2); }
    else if (stage === 'extracting') { setActiveStep(1); setProgress(completed ? 8 : 5); }
    else if (stage === 'embedding') {
      setActiveStep(2);
      const share = total > 0 ? completed / total : 1;
      setProgress(Math.round(10 + share * 75));
    }
    else if (stage === 'grouping') { setActiveStep(3); setProgress(88); }
    else if (stage === 'keywords') { setActiveStep(3); setProgress(90); }
    else if (stage === 'labeling') {
      setActiveStep(3);
      const share = total > 0 ? completed / total : 1;
      setProgress(Math.round(90 + share * 9));
    }
    else if (stage === 'complete') { setActiveStep(3); setProgress(100); }
  };

  const run = async () => {
    if (!file) return;

    setPhase('running');
    setProgress(0);
    setActiveStep(0);
    setError(null);

    try {
      // Fail fast with a clear message if the backend/Ollama isn't ready
      const status = await window.QA_API.health().catch(() => {
        throw new Error('Cannot reach the analyzer backend. Start it with: python api_server.py');
      });
      if (status.status !== 'ok') {
        throw new Error(status.message || 'The analysis backend is not ready.');
      }

      const content = await file.text();
      const data = await window.QA_API.analyze(content, window.QA_SETTINGS.get(), onProgress);

      setProgress(100);
      setResults(data);

      // Store results globally for dashboard to use
      window.ANALYSIS_RESULTS = data;

      setTimeout(() => setPhase('done'), 300);

    } catch (err) {
      setError(err.message);
      setPhase('error');
      console.error('Analysis error:', err);
    }
  };

  return (
    <Modal open={open} onClose={onClose} width={520}>
      <ModalHead title="Upload transcript" sub="Drop the JSON export your Slack bot produces. Questions are extracted, grouped, and merged into your dashboard." onClose={onClose} />
      <div style={{ padding: '0 24px 24px' }}>
        {phase === 'pick' ? (
          <React.Fragment>
            <FileDropzone fileName={file ? file.name : null} accept=".json,.txt,.csv"
              title="Drop a transcript export here or click to browse" hint="JSON, TXT or CSV up to 200MB"
              onFile={(f) => setFile(f)} onClear={() => setFile(null)} />
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 20 }}>
              <Button variant="ghost" onClick={onClose}>Cancel</Button>
              <Button variant="primary" disabled={!file} icon={<Icon name="sparkles" size={16} />} onClick={run}>Analyze</Button>
            </div>
          </React.Fragment>
        ) : null}

        {phase === 'running' ? (
          <div style={{ padding: '8px 0 4px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8 }}>
              <span>{steps[activeStep]}…</span><span style={{ fontFamily: 'var(--font-mono)' }}>{progress}%</span>
            </div>
            <div style={{ height: 4, background: 'var(--gray-20)', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${progress}%`, background: 'var(--blue-60)', transition: 'width 40ms linear' }} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 18 }}>
              {steps.map((s, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: i <= activeStep ? 'var(--text-primary)' : 'var(--text-placeholder)', transition: 'color 200ms' }}>
                  <span style={{ width: 16, height: 16, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: i < activeStep ? 'var(--green-60)' : 'var(--blue-60)' }}>
                    {i < activeStep ? <Icon name="check" size={14} /> : i === activeStep ? <Icon name="loader" size={14} /> : <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--gray-30)' }} />}
                  </span>
                  {s}
                </div>
              ))}
            </div>
          </div>
        ) : null}

        {phase === 'done' && results ? (
          <div style={{ textAlign: 'center', padding: '12px 0 4px' }}>
            <div className="qa-pop" style={{ width: 56, height: 56, borderRadius: '50%', background: 'var(--green-60)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <Icon name="check" size={28} color="#fff" />
            </div>
            <div style={{ fontSize: 18, fontWeight: 400, marginBottom: 6 }}>Transcript analyzed</div>
            <div style={{ fontSize: 13.5, color: 'var(--text-secondary)', marginBottom: 22 }}>
              Found <b>{results.total_questions} questions</b> across <b>{results.total_groups} groups</b>.
              {results.groups && results.groups[0] ? ` ${results.groups[0].representative_question.split(' ').slice(0, 4).join(' ')}... is your most-asked.` : ''}
            </div>
            <Button variant="primary" fullWidth icon={<Icon name="arrow-right" size={16} />} onClick={() => onImported && onImported()}>View dashboard</Button>
          </div>
        ) : null}

        {phase === 'error' ? (
          <div style={{ textAlign: 'center', padding: '12px 0 4px' }}>
            <div className="qa-pop" style={{ width: 56, height: 56, borderRadius: '50%', background: 'var(--red-60)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <Icon name="x" size={28} color="#fff" />
            </div>
            <div style={{ fontSize: 18, fontWeight: 400, marginBottom: 6 }}>Analysis failed</div>
            <div style={{ fontSize: 13.5, color: 'var(--text-secondary)', marginBottom: 22, maxHeight: 120, overflow: 'auto', textAlign: 'left', background: 'var(--gray-10)', padding: 12, fontFamily: 'var(--font-mono)', fontSize: 12 }}>
              {error || 'Unknown error occurred'}
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <Button variant="ghost" fullWidth onClick={onClose}>Close</Button>
              <Button variant="primary" fullWidth onClick={() => { setPhase('pick'); setError(null); }}>Try again</Button>
            </div>
          </div>
        ) : null}
      </div>
    </Modal>
  );
}

// ---- Connect email / manage ----
function SignInModal({ open, onClose, account, onConnect, onDisconnect }) {
  const { Button } = window.QuestionAnalyzerDesignSystem_03a921;
  const [email, setEmail] = React.useState('');
  const [focus, setFocus] = React.useState(false);
  React.useEffect(() => { if (!open) { setEmail(''); setFocus(false); } }, [open]);
  const valid = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);

  if (account) {
    return (
      <Modal open={open} onClose={onClose} width={440}>
        <ModalHead title="Weekly report" sub={null} onClose={onClose} />
        <div style={{ padding: '0 24px 24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px', background: 'var(--gray-10)', borderLeft: '3px solid var(--green-60)', marginBottom: 18 }}>
            <span style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--blue-60)', color: '#fff', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: 13 }}>{account.initials}</span>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: 14, fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis' }}>{account.email}</div>
              <div style={{ fontSize: 12, color: 'var(--green-60)', display: 'inline-flex', alignItems: 'center', gap: 5 }}><Icon name="check" size={12} /> Weekly digest active</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0', borderTop: '1px solid var(--border-subtle)', fontSize: 13.5 }}>
            <span>Next digest</span><span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>Mon, Jun 15 · 9:00</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, marginTop: 18 }}>
            <Button variant="ghost" icon={<Icon name="log-out" size={16} />} onClick={onDisconnect}>Disconnect</Button>
            <Button variant="primary" onClick={onClose}>Done</Button>
          </div>
        </div>
      </Modal>
    );
  }

  return (
    <Modal open={open} onClose={onClose} width={440}>
      <ModalHead title="Get your weekly report" sub="Connect your email and we'll send a Week-in-Review digest — top questions and what's trending — every Monday morning." onClose={onClose} />
      <div style={{ padding: '0 24px 24px' }}>
        <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>Work email</label>
        <div style={{ display: 'flex', alignItems: 'center', height: 44, padding: '0 14px', background: 'var(--field)', borderBottom: `2px solid ${focus ? 'var(--blue-60)' : 'var(--border-strong)'}`, transition: 'border-color var(--duration-base)' }}>
          <Icon name="mail" size={16} color="var(--text-helper)" />
          <input type="email" value={email} placeholder="you@webmethods.io" autoFocus
            onFocus={() => setFocus(true)} onBlur={() => setFocus(false)}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && valid) onConnect(email); }}
            style={{ border: 'none', outline: 'none', background: 'transparent', marginLeft: 10, fontFamily: 'var(--font-sans)', fontSize: 15, width: '100%', color: 'var(--text-primary)' }} />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: 'var(--text-helper)', margin: '14px 0 4px' }}>
          <Icon name="calendar-clock" size={14} /> Delivered Mondays · unsubscribe anytime
        </div>
        <Button variant="primary" fullWidth disabled={!valid} icon={<Icon name="arrow-right" size={16} />} onClick={() => onConnect(email)}>Connect email</Button>
      </div>
    </Modal>
  );
}

// ---- Analysis history ----
function HistoryModal({ open, onClose, onLoad }) {
  const { Button } = window.QuestionAnalyzerDesignSystem_03a921;
  const [items, setItems] = React.useState(null); // null = loading
  const [error, setError] = React.useState(null);
  const [loadingId, setLoadingId] = React.useState(null);

  React.useEffect(() => {
    if (!open) return;
    setItems(null); setError(null); setLoadingId(null);
    window.QA_API.listAnalyses()
      .then(setItems)
      .catch((err) => setError(err.message));
  }, [open]);

  const pick = async (id) => {
    setLoadingId(id);
    try {
      const data = await window.QA_API.getAnalysis(id);
      onLoad(data);
    } catch (err) {
      setError(err.message);
      setLoadingId(null);
    }
  };

  const when = (iso) => iso ? new Date(iso).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) : '—';

  return (
    <Modal open={open} onClose={onClose} width={560}>
      <ModalHead title="Analysis history" sub="Every analysis is saved automatically. Load a past one to revisit it in the dashboard." onClose={onClose} />
      <div style={{ padding: '0 24px 24px' }}>
        {error ? (
          <div style={{ fontSize: 13, color: 'var(--red-60)', padding: '14px 16px', background: 'var(--gray-10)', borderLeft: '3px solid var(--red-60)', marginBottom: 16 }}>{error}</div>
        ) : null}

        {items === null && !error ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-secondary)', fontSize: 13.5, padding: '18px 0' }}>
            <Icon name="loader" size={16} /> Loading history…
          </div>
        ) : null}

        {items && items.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-helper)', fontSize: 13.5, padding: '26px 0 18px' }}>
            No saved analyses yet. Upload a transcript to create your first one.
          </div>
        ) : null}

        {items && items.length > 0 ? (
          <div style={{ border: '1px solid var(--border-subtle)', borderBottom: 'none', maxHeight: 360, overflowY: 'auto' }}>
            {items.map((item) => (
              <button key={item.id} onClick={() => pick(item.id)} disabled={loadingId !== null}
                style={{ display: 'block', width: '100%', textAlign: 'left', padding: '14px 16px', background: '#fff', border: 'none', borderBottom: '1px solid var(--border-subtle)', cursor: loadingId ? 'wait' : 'pointer', fontFamily: 'var(--font-sans)' }}
                onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--gray-10)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = '#fff'; }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 12 }}>
                  <span style={{ fontSize: 13.5, fontWeight: 500, color: 'var(--text-primary)' }}>{when(item.analyzed_at)}</span>
                  <span style={{ fontSize: 12, color: 'var(--text-helper)', fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap' }}>
                    {loadingId === item.id ? 'Loading…' : `${item.total_questions} questions · ${item.total_groups} groups`}
                  </span>
                </div>
                {item.top_question ? (
                  <div style={{ fontSize: 12.5, color: 'var(--text-secondary)', marginTop: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    Top: {item.top_question}
                  </div>
                ) : null}
              </button>
            ))}
          </div>
        ) : null}

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 18 }}>
          <Button variant="ghost" onClick={onClose}>Close</Button>
        </div>
      </div>
    </Modal>
  );
}

// ---- Analysis settings (provider + similarity threshold) ----
function SettingsModal({ open, onClose }) {
  const { Button, Slider } = window.QuestionAnalyzerDesignSystem_03a921;
  const [settings, setSettings] = React.useState(window.QA_SETTINGS.get());
  const providers = [
    { key: 'ollama', label: 'Ollama', hint: 'Local & free' },
    { key: 'azure', label: 'Azure OpenAI', hint: 'Needs API key' },
    { key: 'openai', label: 'OpenAI', hint: 'Needs API key' },
  ];

  React.useEffect(() => {
    if (open) window.QA_SETTINGS.loadServerDefaults().then(setSettings);
  }, [open]);

  const save = () => { window.QA_SETTINGS.set(settings); onClose(); };

  return (
    <Modal open={open} onClose={onClose} width={480}>
      <ModalHead title="Analysis settings" sub="Applied to every new transcript analysis. Provider credentials are configured in the backend's .env file." onClose={onClose} />
      <div style={{ padding: '0 24px 24px' }}>
        <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 8 }}>AI provider</label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, marginBottom: 24 }}>
          {providers.map((p) => {
            const active = settings.provider === p.key;
            return (
              <button key={p.key} onClick={() => setSettings({ ...settings, provider: p.key })}
                style={{ padding: '12px 10px', textAlign: 'left', cursor: 'pointer', fontFamily: 'var(--font-sans)', background: active ? 'var(--blue-60)' : 'var(--field)', color: active ? '#fff' : 'var(--text-primary)', border: `1px solid ${active ? 'var(--blue-60)' : 'var(--border-strong)'}`, transition: 'background var(--duration-base), border-color var(--duration-base)' }}>
                <div style={{ fontSize: 13.5, fontWeight: 500 }}>{p.label}</div>
                <div style={{ fontSize: 11.5, marginTop: 3, color: active ? 'rgba(255,255,255,.75)' : 'var(--text-helper)' }}>{p.hint}</div>
              </button>
            );
          })}
        </div>

        <Slider label="Similarity threshold" value={Math.round(settings.threshold * 100)}
          min={50} max={100} step={1} format={(v) => `${v}%`}
          onChange={(v) => setSettings({ ...settings, threshold: v / 100 })} />
        <div style={{ fontSize: 12, color: 'var(--text-helper)', margin: '10px 0 22px', lineHeight: 1.5 }}>
          Higher = stricter grouping (questions must be nearly identical). Lower = broader topics.
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button variant="primary" icon={<Icon name="check" size={16} />} onClick={save}>Save settings</Button>
        </div>
      </div>
    </Modal>
  );
}

Object.assign(window, { UploadModal, SignInModal, HistoryModal, SettingsModal });
