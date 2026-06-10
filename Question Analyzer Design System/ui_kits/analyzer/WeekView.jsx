// Week in Review — "Pulse": animated trend hero + ranked rows with movement.
function WeekView() {
  const d = window.WEEK_DATA;
  
  // Debug logging
  console.log('WeekView rendering, WEEK_DATA:', d);
  
  // Safety check
  if (!d || !d.groups || d.groups.length === 0) {
    console.log('No week data available');
    return (
      <div style={{ maxWidth: 1040, margin: '0 auto', padding: '36px 40px 80px', width: '100%', textAlign: 'center' }}>
        <h2 style={{ fontSize: 32, fontWeight: 300, marginBottom: 16 }}>Week in Review</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: 16 }}>No weekly data available yet. Upload a transcript to see trends!</p>
        <p style={{ color: 'var(--text-helper)', fontSize: 14, marginTop: 12 }}>Debug: WEEK_DATA = {d ? 'exists but empty' : 'undefined'}</p>
      </div>
    );
  }
  
  console.log('Week data loaded successfully, groups:', d.groups.length);
  
  const max = d.groups[0].count;
  const chev = { width: 32, height: 32, border: '1px solid var(--border-subtle)', background: '#fff', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--text-secondary)' };

  return (
    <div style={{ maxWidth: 1040, margin: '0 auto', padding: '36px 40px 80px', width: '100%' }}>
      <Reveal>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-helper)', fontWeight: 500 }}>Week in review</div>
            <div style={{ fontSize: 22, fontWeight: 300, letterSpacing: '-.01em', marginTop: 4 }}>{d.weekLabel}</div>
          </div>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <span style={chev}><Icon name="chevron-left" size={16} /></span>
            <span style={{ ...chev, width: 'auto', padding: '0 12px', fontSize: 13, gap: 6, color: 'var(--text-secondary)' }}><Icon name="calendar" size={14} /> This week</span>
            <span style={{ ...chev, color: 'var(--text-placeholder)' }}><Icon name="chevron-right" size={16} /></span>
          </div>
        </div>
      </Reveal>

      {/* Trend hero */}
      <Reveal delay={80}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', border: '1px solid var(--border-subtle)', marginBottom: 34, background: '#fff' }}>
          <div style={{ padding: '22px 26px 14px' }}>
            <div style={{ fontSize: 11, color: 'var(--text-helper)', fontWeight: 500, marginBottom: 4 }}>Weekly question volume</div>
            <AreaChart data={d.trend} labels={d.trendLabels} width={560} height={232} />
          </div>
          <div style={{ padding: '22px 26px', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 20, borderLeft: '1px solid var(--border-subtle)', background: 'var(--gray-10)' }}>
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-helper)', fontWeight: 500, marginBottom: 8 }}>Vs. last week</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Icon name="trending-up" size={24} color="var(--green-60)" />
                <span style={{ fontSize: 42, fontWeight: 300, fontFamily: 'var(--font-mono)', lineHeight: 1, color: 'var(--green-60)' }}>+<CountUp to={d.deltaPct} duration={1300} />%</span>
              </div>
            </div>

            {/* last vs this week comparison */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-helper)', marginBottom: 5 }}><span>Last week</span><span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>{d.totalLastWeek}</span></div>
                <Bar pct={(d.totalLastWeek / d.totalThisWeek) * 100} color="var(--gray-40)" bg="var(--gray-20)" height={8} delay={220} />
              </div>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-primary)', marginBottom: 5 }}><span style={{ fontWeight: 500 }}>This week</span><span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{d.totalThisWeek}</span></div>
                <Bar pct={100} color="var(--blue-60)" bg="var(--gray-20)" height={8} delay={360} />
              </div>
            </div>

            <div style={{ height: 1, background: 'var(--border-subtle)' }} />
            <div style={{ display: 'flex', gap: 30 }}>
              <div><div style={{ fontSize: 26, fontWeight: 300, color: 'var(--text-primary)' }}><CountUp to={d.newQuestionTypes} /></div><div style={{ fontSize: 11, color: 'var(--text-helper)', marginTop: 2 }}>new topics</div></div>
              <div><div style={{ fontSize: 26, fontWeight: 300, color: 'var(--teal-60)' }}><CountUp to={d.answered} /></div><div style={{ fontSize: 11, color: 'var(--text-helper)', marginTop: 2 }}>answered</div></div>
            </div>
          </div>
        </div>
      </Reveal>

      {/* Ranked rows */}
      <Reveal delay={160}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: 13, color: 'var(--text-helper)', fontWeight: 500 }}>
            Questions this week, by frequency
          </span>
        </div>
      </Reveal>

      <div style={{ borderTop: '2px solid var(--gray-100)', borderBottom: '1px solid var(--border-subtle)', background: '#fff' }}>
        {d.groups.map((g, i) => (
          <RankedRow key={g.rank} rank={g.rank} index={i} question={g.question} count={g.count}
            maxCount={max} keywords={g.keywords} movement={g.movement} />
        ))}
      </div>
    </div>
  );
}
window.WeekView = WeekView;
