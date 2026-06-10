// OPTION C — "Pulse": trend-led. Volume chart hero + delta, then ranked rows.
function WirPulse() {
  const { Button } = DS_NS();
  const d = window.WEEK_DATA;
  const max = d.groups[0].count;
  const weeks = ['May 5', 'May 12', 'May 19', 'May 26', 'Jun 1', 'Jun 8'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#fff' }}>
      <AppShellHeader active="week" />
      <div style={{ flex: 1, overflow: 'hidden', padding: '32px 48px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
          <div style={{ fontSize: 13, fontFamily: 'var(--font-mono)', color: 'var(--text-helper)' }}>WEEK IN REVIEW · {d.weekLabel}</div>
          <Button variant="tertiary" size="md" icon={<Icon name="send" size={16} />}>Post to Slack</Button>
        </div>

        {/* Trend hero */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 0, border: '1px solid var(--border-subtle)', marginBottom: 28 }}>
          <div style={{ padding: '24px 28px' }}>
            <div style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '.32px', color: 'var(--text-helper)', fontWeight: 500, marginBottom: 16 }}>Weekly question volume · 6 weeks</div>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 22 }}>
              {d.trend.map((v, i) => {
                const last = i === d.trend.length - 1;
                const h = Math.max(6, (v / Math.max(...d.trend)) * 120);
                return (
                  <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, flex: 1 }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: last ? 600 : 400, color: last ? 'var(--blue-60)' : 'var(--text-placeholder)' }}>{v}</span>
                    <span style={{ width: '100%', maxWidth: 38, height: h, background: last ? 'var(--blue-60)' : 'var(--gray-20)' }} />
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: last ? 'var(--text-secondary)' : 'var(--text-placeholder)' }}>{weeks[i]}</span>
                  </div>
                );
              })}
            </div>
          </div>
          {/* Delta callout */}
          <div style={{ background: 'var(--gray-100)', color: '#fff', padding: '24px 28px', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 18 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--green-50)' }}>
                <Icon name="trending-up" size={26} color="var(--green-50)" />
                <span style={{ fontSize: 40, fontWeight: 300, fontFamily: 'var(--font-mono)' }}>+{d.deltaPct}%</span>
              </div>
              <div style={{ fontSize: 13, color: 'var(--gray-30)', marginTop: 4 }}>vs. last week ({d.totalLastWeek} → {d.totalThisWeek})</div>
            </div>
            <div style={{ height: 1, background: 'var(--gray-80)' }} />
            <div style={{ display: 'flex', gap: 28 }}>
              <div><div style={{ fontSize: 26, fontWeight: 300 }}>{d.totalThisWeek}</div><div style={{ fontSize: 11, color: 'var(--gray-40)' }}>this week</div></div>
              <div><div style={{ fontSize: 26, fontWeight: 300, color: 'var(--blue-40)' }}>{d.newQuestionTypes}</div><div style={{ fontSize: 11, color: 'var(--gray-40)' }}>new types</div></div>
            </div>
          </div>
        </div>

        {/* Ranked rows with movement */}
        <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          <Icon name="activity" size={16} color="var(--blue-60)" /> Questions this week, by frequency
        </div>
        <div style={{ borderTop: '2px solid var(--gray-100)' }}>
          {d.groups.map((g) => (
            <div key={g.rank} style={{ display: 'grid', gridTemplateColumns: '24px 64px 1fr 160px 40px', alignItems: 'center', gap: 16, padding: '12px 0', borderBottom: '1px solid var(--border-subtle)' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 14, color: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-50)' }}>{String(g.rank).padStart(2, '0')}</span>
              <span><MovementBadge movement={g.movement} /></span>
              <span style={{ fontSize: 14, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{g.question}</span>
              <span style={{ height: 8, background: 'var(--gray-10)', position: 'relative' }}><span style={{ position: 'absolute', inset: '0 auto 0 0', width: `${Math.max(8,(g.count/max)*100)}%`, background: g.rank <= 3 ? 'var(--blue-60)' : 'var(--gray-40)' }} /></span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 500, textAlign: 'right' }}>{g.count}×</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
window.WirPulse = WirPulse;
