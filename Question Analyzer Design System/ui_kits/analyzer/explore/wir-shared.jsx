// Shared chrome + small primitives for the Week-in-Review explorations.
const DS_NS = () => window.QuestionAnalyzerDesignSystem_03a921;

// App shell header with the Dashboard | Week in Review segmented toggle,
// the always-available upload button, and the account avatar.
function AppShellHeader({ active = 'week' }) {
  const seg = (label, key) => ({
    height: 32, padding: '0 16px', display: 'inline-flex', alignItems: 'center',
    fontSize: 13, cursor: 'pointer', border: 'none',
    background: active === key ? 'var(--blue-60)' : 'transparent',
    color: active === key ? '#fff' : 'var(--gray-30)',
  });
  return (
    <header style={{ height: 48, background: 'var(--gray-100)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px', flex: '0 0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <span style={{ width: 26, height: 26, background: '#fff', position: 'relative' }}>
          <span style={{ position: 'absolute', left: 5, top: 6, width: 15, height: 3, background: 'var(--blue-60)' }} />
          <span style={{ position: 'absolute', left: 5, top: 12, width: 10, height: 3, background: 'var(--blue-50)' }} />
          <span style={{ position: 'absolute', left: 5, top: 18, width: 6, height: 3, background: 'var(--blue-40)' }} />
        </span>
        <span style={{ fontSize: 14 }}><b style={{ fontWeight: 600 }}>Question</b><span style={{ fontWeight: 300, opacity: .8 }}> Analyzer</span></span>
        <span style={{ display: 'inline-flex', border: '1px solid var(--gray-80)', marginLeft: 8 }}>
          <button style={seg('Dashboard', 'dashboard')}>Dashboard</button>
          <button style={seg('Week in Review', 'week')}>Week in Review</button>
        </span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <button style={{ height: 32, padding: '0 14px', display: 'inline-flex', alignItems: 'center', gap: 8, background: 'transparent', color: '#fff', border: '1px solid var(--gray-70)', fontSize: 13, cursor: 'pointer' }}>
          <Icon name="upload" size={15} /> Upload transcript
        </button>
        <span style={{ width: 30, height: 30, borderRadius: '50%', background: 'var(--blue-60)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 600, border: '2px solid var(--gray-80)' }}>SA</span>
      </div>
    </header>
  );
}

// ▲18% / ▼6% delta chip
function DeltaBadge({ value, size = 'md' }) {
  const up = value >= 0;
  const big = size === 'lg';
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: up ? 'var(--green-60)' : 'var(--red-60)', fontFamily: 'var(--font-mono)', fontSize: big ? 18 : 13, fontWeight: 500 }}>
      <Icon name={up ? 'trending-up' : 'trending-down'} size={big ? 18 : 14} />
      {up ? '+' : ''}{value}%
    </span>
  );
}

// NEW / ▲2 / ▼1 movement marker for a ranked row
function MovementBadge({ movement }) {
  if (movement === 'new') {
    return <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '.5px', color: 'var(--blue-70)', background: 'var(--blue-20)', padding: '2px 6px', borderRadius: 'var(--radius-sm)' }}>NEW</span>;
  }
  if (typeof movement === 'number' && movement !== 0) {
    const up = movement > 0;
    return <span style={{ display: 'inline-flex', alignItems: 'center', gap: 2, fontFamily: 'var(--font-mono)', fontSize: 11, color: up ? 'var(--green-60)' : 'var(--gray-50)' }}>
      <Icon name={up ? 'arrow-up' : 'arrow-down'} size={12} />{Math.abs(movement)}
    </span>;
  }
  return <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-placeholder)' }}>—</span>;
}

// Tiny vertical bar-chart of weekly volume; last bar highlighted.
function TrendBars({ data, height = 64, barW = 20, gap = 8 }) {
  const max = Math.max(...data);
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap, height }}>
      {data.map((v, i) => {
        const last = i === data.length - 1;
        return (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
            <span style={{ width: barW, height: Math.max(3, (v / max) * (height - 16)), background: last ? 'var(--blue-60)' : 'var(--gray-30)' }} />
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: last ? 'var(--text-primary)' : 'var(--text-placeholder)' }}>{v}</span>
          </div>
        );
      })}
    </div>
  );
}

Object.assign(window, { DS_NS, AppShellHeader, DeltaBadge, MovementBadge, TrendBars });
