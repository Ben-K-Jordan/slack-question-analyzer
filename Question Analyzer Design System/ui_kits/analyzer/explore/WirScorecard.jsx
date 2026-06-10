// OPTION B — "Scorecard": analytics-dense KPI tiles + ranked list + movers rail.
function WirScorecard() {
  const { MetricTile, Tag, Button } = DS_NS();
  const d = window.WEEK_DATA;
  const max = d.groups[0].count;
  const movers = d.groups.filter((g) => g.movement === 'new' || (typeof g.movement === 'number' && g.movement > 0)).slice(0, 4);

  const kpi = { background: 'var(--layer-02)', borderLeft: '3px solid var(--blue-60)', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 8 };
  const kpiLabel = { fontSize: 11, textTransform: 'uppercase', letterSpacing: '.32px', color: 'var(--text-helper)', fontWeight: 500 };
  const kpiNum = { fontSize: 32, fontWeight: 300, lineHeight: 1, letterSpacing: '-.02em' };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: 'var(--gray-10)' }}>
      <AppShellHeader active="week" />
      <div style={{ flex: 1, overflow: 'hidden', padding: '28px 40px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 20 }}>
          <div>
            <div style={{ fontSize: 24, fontWeight: 300, letterSpacing: '-.01em' }}>Week in Review</div>
            <div style={{ fontSize: 13, fontFamily: 'var(--font-mono)', color: 'var(--text-helper)', marginTop: 2 }}>{d.weekLabel} · vs. May 26 – Jun 1</div>
          </div>
          <Button variant="tertiary" size="md" icon={<Icon name="send" size={16} />}>Post to Slack</Button>
        </div>

        {/* KPI row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 1, background: 'var(--border-subtle)', border: '1px solid var(--border-subtle)', marginBottom: 24 }}>
          <div style={kpi}>
            <span style={kpiLabel}>Questions this week</span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}><span style={kpiNum}>{d.totalThisWeek}</span><DeltaBadge value={d.deltaPct} /></div>
          </div>
          <div style={{ ...kpi, borderLeftColor: 'var(--purple-60)' }}>
            <span style={kpiLabel}>New question types</span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}><span style={kpiNum}>{d.newQuestionTypes}</span><span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>of {d.groupsThisWeek}</span></div>
          </div>
          <div style={{ ...kpi, borderLeftColor: 'var(--teal-60)' }}>
            <span style={kpiLabel}>Active groups</span>
            <span style={kpiNum}>{d.groupsThisWeek}</span>
          </div>
          <div style={{ ...kpi, borderLeftColor: 'var(--gray-60)' }}>
            <span style={kpiLabel}>Answered</span>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}><span style={kpiNum}>{d.answered}</span><span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>resolved</span></div>
          </div>
        </div>

        {/* Two columns */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 24, alignItems: 'start' }}>
          {/* Ranked list */}
          <div style={{ background: '#fff', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 18px', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: 14, fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 8 }}><Icon name="list-ordered" size={16} color="var(--blue-60)" /> Ranked this week</span>
              <span style={{ fontSize: 12, color: 'var(--text-helper)' }}>Δ = rank vs last week</span>
            </div>
            {d.groups.map((g) => (
              <div key={g.rank} style={{ display: 'grid', gridTemplateColumns: '26px 1fr 90px 40px 44px', alignItems: 'center', gap: 12, padding: '12px 18px', borderBottom: '1px solid var(--border-subtle)' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 14, color: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-50)', textAlign: 'right' }}>{String(g.rank).padStart(2, '0')}</span>
                <span style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 13.5, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{g.question}</div>
                  <div style={{ fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-placeholder)', marginTop: 2 }}>{g.keywords.slice(0,3).join(' · ')}</div>
                </span>
                <span style={{ height: 5, background: 'var(--gray-10)', position: 'relative' }}><span style={{ position: 'absolute', inset: '0 auto 0 0', width: `${Math.max(8,(g.count/max)*100)}%`, background: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-40)' }} /></span>
                <span style={{ textAlign: 'center' }}><MovementBadge movement={g.movement} /></span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 500, textAlign: 'right' }}>{g.count}×</span>
              </div>
            ))}
          </div>

          {/* Movers rail */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ background: '#fff', border: '1px solid var(--border-subtle)', padding: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 12, display: 'inline-flex', alignItems: 'center', gap: 6 }}><Icon name="trending-up" size={15} color="var(--green-60)" /> Biggest movers</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {movers.map((g) => (
                  <div key={g.rank} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <MovementBadge movement={g.movement} />
                    <span style={{ fontSize: 12.5, color: 'var(--text-secondary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{g.topic}</span>
                  </div>
                ))}
              </div>
            </div>
            <div style={{ background: '#fff', border: '1px solid var(--border-subtle)', padding: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 12 }}>New topics this week</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {d.groups.filter((g) => g.movement === 'new').map((g) => (
                  <Tag key={g.rank} color="blue" size="sm">{g.topic}</Tag>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
window.WirScorecard = WirScorecard;
