// OPTION A — "Briefing": editorial weekly digest, single column, email-ready.
function WirDigest() {
  const { Tag, Button } = DS_NS();
  const d = window.WEEK_DATA;
  const max = d.groups[0].count;

  const wkline = { display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 };
  const chev = { width: 32, height: 32, border: '1px solid var(--border-subtle)', background: '#fff', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--text-secondary)' };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#fff' }}>
      <AppShellHeader active="week" />
      <div style={{ flex: 1, overflow: 'hidden', padding: '40px 56px', maxWidth: 860, margin: '0 auto', width: '100%' }}>
        <div style={wkline}>
          <div>
            <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.32px', color: 'var(--text-helper)', fontWeight: 500 }}>Weekly digest</div>
            <div style={{ fontSize: 14, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)', marginTop: 4 }}>Week of {d.weekLabel}</div>
          </div>
          <div style={{ display: 'flex', gap: 6 }}>
            <span style={chev}><Icon name="chevron-left" size={16} /></span>
            <span style={chev}><Icon name="chevron-right" size={16} /></span>
          </div>
        </div>

        {/* Editorial hero */}
        <h1 style={{ fontSize: 38, fontWeight: 300, letterSpacing: '-.02em', lineHeight: 1.15, margin: '0 0 20px', color: 'var(--text-primary)' }}>
          Your channel asked <b style={{ fontWeight: 600 }}>{d.totalThisWeek} questions</b> this week —
          up {d.deltaPct}% from last.
        </h1>
        <div style={{ display: 'flex', gap: 40, marginBottom: 36, paddingBottom: 28, borderBottom: '1px solid var(--border-subtle)' }}>
          <div><div style={{ fontSize: 32, fontWeight: 300 }}>{d.totalThisWeek}</div><div style={{ fontSize: 12, color: 'var(--text-helper)' }}>questions logged</div></div>
          <div><div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}><span style={{ fontSize: 32, fontWeight: 300, color: 'var(--green-60)' }}>+{d.deltaPct}%</span></div><div style={{ fontSize: 12, color: 'var(--text-helper)' }}>vs last week</div></div>
          <div><div style={{ fontSize: 32, fontWeight: 300 }}>{d.newQuestionTypes}</div><div style={{ fontSize: 12, color: 'var(--text-helper)' }}>new question types</div></div>
        </div>

        {/* Spotlight */}
        <div style={{ borderLeft: '3px solid var(--blue-60)', background: 'var(--blue-10)', padding: '18px 22px', marginBottom: 32 }}>
          <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.32px', color: 'var(--blue-70)', fontWeight: 600, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
            <Icon name="sparkles" size={14} color="var(--blue-70)" /> Spotlight · document this first
          </div>
          <div style={{ fontSize: 19, fontWeight: 400, lineHeight: 1.35, marginBottom: 8 }}>{d.groups[0].question}</div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Asked <b>{d.groups[0].count}×</b> this week — your most-pressed topic. {d.groups[0].keywords.slice(0,3).join(', ')}.</div>
        </div>

        {/* Ranked list */}
        <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 12 }}>The week, ranked</div>
        <div style={{ borderTop: '1px solid var(--border-subtle)' }}>
          {d.groups.map((g) => (
            <div key={g.rank} style={{ display: 'grid', gridTemplateColumns: '28px 1fr 120px 44px', alignItems: 'center', gap: 16, padding: '13px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 15, color: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-50)', textAlign: 'right' }}>{String(g.rank).padStart(2, '0')}</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
                <span style={{ fontSize: 14, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{g.question}</span>
                {g.movement === 'new' ? <MovementBadge movement="new" /> : null}
              </span>
              <span style={{ height: 6, background: 'var(--gray-10)', position: 'relative' }}><span style={{ position: 'absolute', inset: '0 auto 0 0', width: `${Math.max(8, (g.count / max) * 100)}%`, background: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-40)' }} /></span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 500, textAlign: 'right' }}>{g.count}×</span>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 28, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 12, color: 'var(--text-helper)', display: 'inline-flex', alignItems: 'center', gap: 6 }}><Icon name="mail" size={14} /> Delivered Mondays to sam.archer@webmethods.io</span>
          <Button variant="tertiary" size="md" icon={<Icon name="send" size={16} />}>Post to Slack</Button>
        </div>
      </div>
    </div>
  );
}
window.WirDigest = WirDigest;
