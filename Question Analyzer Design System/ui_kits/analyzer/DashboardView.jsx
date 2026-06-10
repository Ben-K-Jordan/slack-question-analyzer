// Overall dashboard — common questions, ranked by occurrences (all-time).
// Entirely backend-driven: real saved analyses or an empty state, never mocks.
function DashboardView({ onUpload }) {
  // Use real analysis results when available; on first load, pull the most
  // recent saved analysis from the backend so results survive page refreshes.
  const [analysisResults, setAnalysisResults] = React.useState(window.ANALYSIS_RESULTS || null);
  const [loadingLatest, setLoadingLatest] = React.useState(!window.ANALYSIS_RESULTS);
  React.useEffect(() => {
    if (analysisResults || !window.QA_API) { setLoadingLatest(false); return; }
    let cancelled = false;
    window.QA_API.latestAnalysis().then((latest) => {
      if (cancelled) return;
      if (latest) {
        window.ANALYSIS_RESULTS = latest;
        setAnalysisResults(latest);
      }
      setLoadingLatest(false);
    }).catch(() => { if (!cancelled) setLoadingLatest(false); });
    return () => { cancelled = true; };
  }, []);

  const PAGE_SIZE = 50;
  // First-run onboarding: surface backend/model setup problems before the
  // user wastes an upload finding out. Missing Ollama models get a one-click
  // download button instead of terminal instructions.
  const [setupHealth, setSetupHealth] = React.useState(null); // latest health payload
  const [pulls, setPulls] = React.useState({}); // model -> {pct, detail, error}
  const checkHealth = React.useCallback(() => {
    if (!window.QA_API) return;
    window.QA_API.health(window.QA_SETTINGS && window.QA_SETTINGS.get().provider)
      .then(setSetupHealth)
      .catch(() => setSetupHealth({ status: 'unavailable',
        message: 'Cannot reach the analyzer backend. Start it with: python api_server.py' }));
  }, []);
  React.useEffect(() => { checkHealth(); }, [checkHealth]);

  const downloadModel = async (model) => {
    try {
      setPulls((p) => ({ ...p, [model]: { pct: 0, detail: 'starting…' } }));
      await window.QA_API.pullModel(model);
      const timer = setInterval(async () => {
        try {
          const s = await window.QA_API.pullStatus(model);
          if (s.status === 'done') { clearInterval(timer); setPulls((p) => ({ ...p, [model]: null })); checkHealth(); }
          else if (s.status === 'error') { clearInterval(timer); setPulls((p) => ({ ...p, [model]: { error: s.detail } })); }
          else setPulls((p) => ({ ...p, [model]: { pct: s.total ? Math.round(s.completed / s.total * 100) : 0, detail: s.detail } }));
        } catch (err) { /* keep polling */ }
      }, 1000);
    } catch (err) {
      setPulls((p) => ({ ...p, [model]: { error: err.message } }));
    }
  };

  // Renaming updates the learned bank (future analyses) and the current view
  const renameTopic = async (topicId, newName) => {
    try {
      await window.QA_API.renameTopic(topicId, newName);
    } catch (err) {
      alert('Rename failed: ' + err.message);
      return;
    }
    if (window.ANALYSIS_RESULTS && window.ANALYSIS_RESULTS.groups) {
      window.ANALYSIS_RESULTS = {
        ...window.ANALYSIS_RESULTS,
        groups: window.ANALYSIS_RESULTS.groups.map((g) =>
          g.topic_id === topicId ? { ...g, topic: newName } : g),
      };
      setAnalysisResults(window.ANALYSIS_RESULTS);
    }
  };

  // Models the banner should offer to download (Ollama reachable but missing).
  // A missing LABEL model doesn't fail health (analysis still works), but it
  // silently downgrades topic names to keywords — so surface it here too.
  const missingModels = [];
  if (setupHealth && setupHealth.ollama && setupHealth.ollama.reachable) {
    if (!setupHealth.ollama.model_available) missingModels.push(setupHealth.ollama.model);
    if (!setupHealth.ollama.label_model_available && setupHealth.ollama.label_model) {
      missingModels.push(setupHealth.ollama.label_model);
    }
  }
  const healthBroken = setupHealth && setupHealth.status !== 'ok';
  const showSetupBanner = healthBroken || missingModels.length > 0;

  const d = analysisResults ? transformAnalysisResults(analysisResults) : null;
  const [query, setQuery] = React.useState('');
  const [visibleCount, setVisibleCount] = React.useState(PAGE_SIZE);
  const [showUnique, setShowUnique] = React.useState(true);

  const exportBtn = {
    height: 32, padding: '0 12px', display: 'inline-flex', alignItems: 'center', gap: 6,
    background: '#fff', color: 'var(--text-secondary)', border: '1px solid var(--border-strong)',
    fontFamily: 'var(--font-sans)', fontSize: 12.5, cursor: 'pointer', whiteSpace: 'nowrap',
  };
  const download = (format) => {
    if (window.ANALYSIS_ID) window.open(window.QA_API.exportUrl(window.ANALYSIS_ID, format), '_blank');
  };
  const max = d && d.groups && d.groups.length > 0 ? d.groups[0].count : 0;
  const groups = d && d.groups ? d.groups.filter((g) =>
    g.question.toLowerCase().includes(query.toLowerCase()) ||
    g.keywords.join(' ').includes(query.toLowerCase()) ||
    (g.topic && g.topic.toLowerCase().includes(query.toLowerCase()))) : [];
  const uniqueQuestions = ((d && d.ungrouped) || []).filter((q) =>
    q.text.toLowerCase().includes(query.toLowerCase()));

  const stat = (label, value, accent) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <span style={{ fontSize: 11, color: 'var(--text-helper)', fontWeight: 500 }}>{label}</span>
      <span style={{ fontSize: 34, fontWeight: 300, letterSpacing: '-.02em', lineHeight: 1, color: accent || 'var(--text-primary)', fontVariantNumeric: 'tabular-nums' }}>
        <CountUp to={value} />
      </span>
    </div>
  );

  const search = {
    display: 'flex', alignItems: 'center', gap: 8, height: 40, padding: '0 14px',
    background: 'var(--field)', borderBottom: '1px solid var(--border-strong)', width: 300, maxWidth: '40vw',
  };

  const setupBanner = showSetupBanner ? (
    <Reveal delay={100}>
      <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', padding: '16px 24px', background: '#fff', border: '1px solid var(--border-subtle)', borderLeft: `3px solid ${healthBroken ? 'var(--red-60)' : 'var(--blue-60)'}`, marginBottom: 32 }}>
        <span style={{ color: healthBroken ? 'var(--red-60)' : 'var(--blue-60)', flex: '0 0 auto', marginTop: 1 }}><Icon name={healthBroken ? 'alert-triangle' : 'download'} size={16} /></span>
        <div style={{ fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.55, minWidth: 0, flex: 1 }}>
          <b>{healthBroken ? 'Setup needed before analyzing.' : 'Topic labels are running in keyword-fallback mode.'}</b>
          {missingModels.length === 0 ? <span> {setupHealth.message}</span> : null}
          {missingModels.map((model) => (
            <div key={model} style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 10 }}>
              {pulls[model] && pulls[model].error ? (
                <span style={{ color: 'var(--red-60)' }}>Download of {model} failed: {pulls[model].error}</span>
              ) : pulls[model] ? (
                <React.Fragment>
                  <span style={{ whiteSpace: 'nowrap' }}>Downloading <b>{model}</b>… {pulls[model].pct}%</span>
                  <div style={{ flex: 1, height: 4, background: 'var(--gray-20)', overflow: 'hidden', minWidth: 80 }}>
                    <div style={{ height: '100%', width: `${pulls[model].pct}%`, background: 'var(--blue-60)', transition: 'width 600ms linear' }} />
                  </div>
                </React.Fragment>
              ) : (
                <React.Fragment>
                  <span>Model <b>{model}</b> isn't downloaded yet.</span>
                  <button onClick={() => downloadModel(model)}
                    style={{ height: 28, padding: '0 12px', display: 'inline-flex', alignItems: 'center', gap: 6, background: 'var(--blue-60)', color: '#fff', border: 'none', cursor: 'pointer', fontFamily: 'var(--font-sans)', fontSize: 12.5, whiteSpace: 'nowrap' }}>
                    <Icon name="download" size={13} /> Download now
                  </button>
                </React.Fragment>
              )}
            </div>
          ))}
        </div>
      </div>
    </Reveal>
  ) : null;

  if (loadingLatest) {
    return (
      <div style={{ maxWidth: 1000, margin: '0 auto', padding: '60px 40px', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, color: 'var(--text-secondary)', fontSize: 14 }}>
        <Icon name="loader" size={16} /> Loading…
      </div>
    );
  }

  if (!d) {
    // Backend has no saved analyses yet: honest empty state, no mock data
    return (
      <div style={{ maxWidth: 1000, margin: '0 auto', padding: '44px 40px 80px', width: '100%' }}>
        {setupBanner}
        <Reveal>
          <div style={{ textAlign: 'center', padding: '70px 24px', border: '1px dashed var(--border-strong)', background: '#fff' }}>
            <span style={{ display: 'inline-flex', width: 56, height: 56, borderRadius: '50%', background: 'var(--gray-10)', alignItems: 'center', justifyContent: 'center', marginBottom: 18, color: 'var(--blue-60)' }}>
              <Icon name="upload" size={24} />
            </span>
            <h1 style={{ fontSize: 26, fontWeight: 300, letterSpacing: '-.02em', margin: '0 0 8px' }}>No analyses yet</h1>
            <div style={{ fontSize: 14, color: 'var(--text-secondary)', maxWidth: 440, margin: '0 auto 24px', lineHeight: 1.55 }}>
              Upload a Slack transcript (TXT, JSON, CSV, or a zipped export) and the questions
              will be extracted, grouped by topic, and ranked right here.
            </div>
            <button onClick={onUpload}
              style={{ height: 40, padding: '0 22px', display: 'inline-flex', alignItems: 'center', gap: 8, background: 'var(--blue-60)', color: '#fff', border: 'none', cursor: 'pointer', fontFamily: 'var(--font-sans)', fontSize: 14 }}>
              <Icon name="upload" size={16} /> Upload transcript
            </button>
          </div>
        </Reveal>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '44px 40px 80px', width: '100%' }}>
      <Reveal>
        <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 24, flexWrap: 'wrap', marginBottom: 30 }}>
          <div>
            <h1 style={{ fontSize: 32, fontWeight: 300, letterSpacing: '-.02em', margin: '0 0 6px' }}>Most-asked questions</h1>
            <div style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
              All-time across your monitored Slack channels · ranked by occurrences
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            {window.ANALYSIS_ID ? (
              <React.Fragment>
                <button style={exportBtn} title="Download Markdown report" onClick={() => download('md')}>
                  <Icon name="download" size={14} /> Report
                </button>
                <button style={exportBtn} title="Download CSV" onClick={() => download('csv')}>
                  <Icon name="download" size={14} /> CSV
                </button>
              </React.Fragment>
            ) : null}
            <div style={search}>
              <Icon name="search" size={16} color="var(--text-helper)" />
              <input value={query} onChange={(e) => { setQuery(e.target.value); setVisibleCount(PAGE_SIZE); }} placeholder="Filter questions or topics"
                style={{ border: 'none', outline: 'none', background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: 14, width: '100%', color: 'var(--text-primary)' }} />
            </div>
          </div>
        </div>
      </Reveal>

      <Reveal delay={90}>
        <div style={{ display: 'flex', gap: 56, padding: '22px 24px', background: 'var(--gray-10)', borderLeft: '3px solid var(--blue-60)', marginBottom: d.executiveSummary ? 16 : 32 }}>
          {stat('Questions logged', d.totalQuestions)}
          {stat('Distinct topics', d.totalGroups, 'var(--purple-60)')}
          {stat('Answered', d.resolved, 'var(--teal-60)')}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, justifyContent: 'center', marginLeft: 'auto', textAlign: 'right' }}>
            <span style={{ fontSize: 11, color: 'var(--text-helper)', fontWeight: 500 }}>Top topic</span>
            <span style={{ fontSize: 18, fontWeight: 600, color: 'var(--blue-70)' }}>{d.topTopic}</span>
          </div>
        </div>
      </Reveal>

      {setupBanner}

      {d.autoAdjusted ? (
        <Reveal delay={105}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', padding: '14px 24px', background: '#fff', border: '1px solid var(--border-subtle)', borderLeft: '3px solid var(--teal-60)', marginBottom: 32 }}>
            <span style={{ color: 'var(--teal-60)', flex: '0 0 auto', marginTop: 1 }}><Icon name="sliders-horizontal" size={16} /></span>
            <span style={{ fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.55 }}>
              Nothing grouped at the default threshold, so it was automatically relaxed to <b>{Math.round(d.autoAdjusted * 100)}%</b> for this analysis. Pin a value in Settings if you prefer.
            </span>
          </div>
        </Reveal>
      ) : null}

      {d.thresholdHint ? (
        <Reveal delay={110}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', padding: '16px 24px', background: '#fff', border: '1px solid var(--border-subtle)', borderLeft: '3px solid var(--yellow-40, #f1c21b)', marginBottom: 32 }}>
            <span style={{ color: 'var(--text-secondary)', flex: '0 0 auto', marginTop: 1 }}><Icon name="sliders-horizontal" size={16} /></span>
            <span style={{ fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.55 }}>
              No questions grouped at threshold <b>{Math.round(d.thresholdHint.threshold * 100)}%</b> — your most similar pair scored <b>{Math.round(d.thresholdHint.max * 100)}%</b> (similarity scales vary by embedding model).
              Open <b>Settings</b> (gear icon), set the threshold to about <b>{Math.round(d.thresholdHint.suggestion * 100)}%</b>, and re-upload — cached embeddings make the re-run fast.
            </span>
          </div>
        </Reveal>
      ) : null}

      {d.executiveSummary ? (
        <Reveal delay={120}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', padding: '16px 24px', background: '#fff', border: '1px solid var(--border-subtle)', borderLeft: '3px solid var(--purple-60)', marginBottom: 32 }}>
            <span style={{ color: 'var(--purple-60)', flex: '0 0 auto', marginTop: 1 }}><Icon name="sparkles" size={16} /></span>
            <span style={{ fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.55 }}>{d.executiveSummary}</span>
          </div>
        </Reveal>
      ) : null}

      <Reveal delay={160}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: 13, color: 'var(--text-helper)', fontWeight: 500 }}>Ranked · {groups.length} topics</span>
          <span style={{ fontSize: 12, color: 'var(--text-helper)', display: 'inline-flex', alignItems: 'center', gap: 6 }}><Icon name="arrow-down" size={13} /> Most frequent first</span>
        </div>
      </Reveal>

      <div style={{ border: '1px solid var(--border-subtle)', borderBottom: 'none', background: '#fff' }}>
        {groups.slice(0, visibleCount).map((g, i) => (
          <RankedRow key={g.rank} rank={g.rank} index={i} question={g.question} count={g.count}
            maxCount={max} keywords={g.keywords} similarity={g.similarity} questions={g.questions}
            topic={g.topic} summary={g.summary} seenIn={g.seenIn}
            onRenameTopic={g.topicId ? (name) => renameTopic(g.topicId, name) : null}
            defaultOpen={i === 0 && !query} />
        ))}
        {groups.length === 0 ? <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-helper)', borderBottom: '1px solid var(--border-subtle)' }}>No topics match “{query}”.</div> : null}
      </div>
      {groups.length > visibleCount ? (
        <button onClick={() => setVisibleCount((v) => v + PAGE_SIZE)}
          style={{ display: 'block', width: '100%', padding: '13px 0', marginTop: -1, background: '#fff', border: '1px solid var(--border-subtle)', cursor: 'pointer', fontFamily: 'var(--font-sans)', fontSize: 13, color: 'var(--blue-60)' }}>
          Show {Math.min(PAGE_SIZE, groups.length - visibleCount)} more · {groups.length - visibleCount} remaining
        </button>
      ) : null}

      {uniqueQuestions.length ? (
        <div style={{ marginTop: 28 }}>
          <button onClick={() => setShowUnique(!showUnique)}
            style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', border: 'none', cursor: 'pointer', fontFamily: 'var(--font-sans)', fontSize: 13, fontWeight: 500, color: 'var(--text-secondary)', padding: 0 }}>
            <span style={{ display: 'inline-flex', transform: showUnique ? 'rotate(90deg)' : 'none', transition: 'transform var(--duration-base) var(--ease-productive)' }}>
              <Icon name="chevron-right" size={14} />
            </span>
            Unique questions ({uniqueQuestions.length}) — asked only once, kept in every export
          </button>
          {showUnique ? (
            <ul style={{ listStyle: 'none', margin: '12px 0 0', padding: 0, borderLeft: '1px solid var(--border-subtle)' }}>
              {uniqueQuestions.map((q, i) => (
                <li key={i} style={{ display: 'flex', justifyContent: 'space-between', gap: 16, padding: '8px 16px' }}>
                  <span style={{ fontSize: 13.5, color: 'var(--text-secondary)', lineHeight: 1.45 }}>{q.text}</span>
                  {q.date && q.date !== 'Unknown' ? <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-placeholder)', whiteSpace: 'nowrap' }}>{q.date}</span> : null}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
window.DashboardView = DashboardView;

// Suggest a workable threshold when nothing grouped (mirrors the backend's
// QuestionAnalyzer.suggested_threshold logic).
function thresholdHint(results) {
  const stats = results.metadata && results.metadata.similarity_stats;
  if (!stats || (results.total_groups || 0) > 0) return null;
  const threshold = results.metadata.similarity_threshold;
  if (stats.max >= threshold) return null;
  const suggestion = Math.round((stats.max - 0.02) * 100) / 100;
  if (suggestion <= 0 || suggestion >= threshold) return null;
  return { threshold, max: stats.max, suggestion };
}

// Transform API results to dashboard format
function transformAnalysisResults(results) {
  if (!results || !results.groups) return null;
  
  const fallbackTopic = (g) => g.representative_question.split(' ').slice(0, 3).join(' ') + '...';
  return {
    totalQuestions: results.total_questions || 0,
    totalGroups: results.total_groups || 0,
    resolved: results.answered_questions || 0, // LLM answer detection (threads only)
    executiveSummary: results.executive_summary || null,
    ungrouped: results.ungrouped_questions || [],
    thresholdHint: thresholdHint(results),
    autoAdjusted: (results.metadata && results.metadata.threshold_auto_adjusted)
      ? results.metadata.similarity_threshold : null,
    topTopic: results.groups[0] ? (results.groups[0].topic || fallbackTopic(results.groups[0])) : 'N/A',
    groups: results.groups.map((g, i) => ({
      rank: i + 1,
      count: g.count,
      similarity: `${Math.round(g.avg_similarity * 100)}%`,
      topic: g.topic || null,
      summary: g.summary || null,
      seenIn: g.seen_in_analyses || 0,
      topicId: g.topic_id || null,
      question: g.representative_question,
      keywords: g.keywords || [],
      questions: g.questions || []
    }))
  };
}
