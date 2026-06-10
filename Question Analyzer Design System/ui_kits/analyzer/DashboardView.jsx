// Overall dashboard — common questions, ranked by occurrences (all-time).
function DashboardView() {
  // Use real analysis results if available, otherwise fall back to mock data
  const analysisResults = window.ANALYSIS_RESULTS;
  const d = analysisResults ? transformAnalysisResults(analysisResults) : window.DASHBOARD_DATA;
  const [query, setQuery] = React.useState('');
  const max = d.groups && d.groups.length > 0 ? d.groups[0].count : 0;
  const groups = d.groups ? d.groups.filter((g) =>
    g.question.toLowerCase().includes(query.toLowerCase()) ||
    g.keywords.join(' ').includes(query.toLowerCase()) ||
    (g.topic && g.topic.toLowerCase().includes(query.toLowerCase()))) : [];

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

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '44px 40px 80px', width: '100%' }}>
      <Reveal>
        <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 24, flexWrap: 'wrap', marginBottom: 30 }}>
          <div>
            <h1 style={{ fontSize: 32, fontWeight: 300, letterSpacing: '-.02em', margin: '0 0 6px' }}>Most-asked questions</h1>
            <div style={{ fontSize: 14, color: 'var(--text-secondary)' }}>All-time across your monitored Slack channels · ranked by occurrences</div>
          </div>
          <div style={search}>
            <Icon name="search" size={16} color="var(--text-helper)" />
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Filter questions or topics"
              style={{ border: 'none', outline: 'none', background: 'transparent', fontFamily: 'var(--font-sans)', fontSize: 14, width: '100%', color: 'var(--text-primary)' }} />
          </div>
        </div>
      </Reveal>

      <Reveal delay={90}>
        <div style={{ display: 'flex', gap: 56, padding: '22px 24px', background: 'var(--gray-10)', borderLeft: '3px solid var(--blue-60)', marginBottom: 32 }}>
          {stat('Questions logged', d.totalQuestions)}
          {stat('Distinct topics', d.totalGroups, 'var(--purple-60)')}
          {stat('Answered', d.resolved, 'var(--teal-60)')}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, justifyContent: 'center', marginLeft: 'auto', textAlign: 'right' }}>
            <span style={{ fontSize: 11, color: 'var(--text-helper)', fontWeight: 500 }}>Top topic</span>
            <span style={{ fontSize: 18, fontWeight: 600, color: 'var(--blue-70)' }}>{d.topTopic}</span>
          </div>
        </div>
      </Reveal>

      <Reveal delay={160}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: 13, color: 'var(--text-helper)', fontWeight: 500 }}>Ranked · {groups.length} topics</span>
          <span style={{ fontSize: 12, color: 'var(--text-helper)', display: 'inline-flex', alignItems: 'center', gap: 6 }}><Icon name="arrow-down" size={13} /> Most frequent first</span>
        </div>
      </Reveal>

      <div style={{ border: '1px solid var(--border-subtle)', borderBottom: 'none', background: '#fff' }}>
        {groups.map((g, i) => (
          <RankedRow key={g.rank} rank={g.rank} index={i} question={g.question} count={g.count}
            maxCount={max} keywords={g.keywords} similarity={g.similarity} questions={g.questions}
            defaultOpen={i === 0 && !query} />
        ))}
        {groups.length === 0 ? <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-helper)', borderBottom: '1px solid var(--border-subtle)' }}>No topics match “{query}”.</div> : null}
      </div>
    </div>
  );
}
window.DashboardView = DashboardView;

// Transform API results to dashboard format
function transformAnalysisResults(results) {
  if (!results || !results.groups) return window.DASHBOARD_DATA;
  
  return {
    totalQuestions: results.total_questions || 0,
    totalGroups: results.total_groups || 0,
    resolved: 0, // Not tracked yet
    topTopic: results.groups[0] ? results.groups[0].representative_question.split(' ').slice(0, 3).join(' ') + '...' : 'N/A',
    groups: results.groups.map((g, i) => ({
      rank: i + 1,
      count: g.count,
      similarity: `${Math.round(g.avg_similarity * 100)}%`,
      topic: g.representative_question.split(' ').slice(0, 3).join(' ') + '...',
      question: g.representative_question,
      keywords: g.keywords || [],
      questions: g.questions || []
    }))
  };
}
