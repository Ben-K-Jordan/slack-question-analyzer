// App header: brand, animated Dashboard | Week in Review toggle,
// Upload transcript, and the account / sign-in avatar.
function AppHeader({ view, setView, onUpload, account, onAvatar, onManage }) {
  const segs = [{ key: 'dashboard', label: 'Dashboard' }, { key: 'week', label: 'Week in Review' }];
  const activeIdx = segs.findIndex((s) => s.key === view);

  const seg = (s, i) => ({
    position: 'relative', zIndex: 1, height: 32, padding: '0 18px',
    display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap',
    fontFamily: 'var(--font-sans)', fontSize: 13, cursor: 'pointer', border: 'none',
    background: 'transparent',
    color: view === s.key ? '#fff' : 'var(--gray-30)',
    transition: 'color var(--duration-moderate) var(--ease-productive)',
  });

  return (
    <header style={{ height: 48, background: 'var(--gray-100)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 16px', flex: '0 0 auto', zIndex: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        {/* Animated segmented toggle */}
        <span style={{ position: 'relative', display: 'inline-flex', border: '1px solid var(--gray-80)' }}>
          <span style={{
            position: 'absolute', top: 0, bottom: 0, left: 0, width: `${100 / segs.length}%`,
            background: 'var(--blue-60)', transform: `translateX(${activeIdx * 100}%)`,
            transition: 'transform var(--duration-moderate) var(--ease-productive)', zIndex: 0,
          }} />
          {segs.map((s, i) => (
            <button key={s.key} style={seg(s, i)} onClick={() => setView(s.key)}>{s.label}</button>
          ))}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <button onClick={onUpload} style={{
          height: 32, padding: '0 14px', display: 'inline-flex', alignItems: 'center', gap: 8,
          background: 'transparent', color: '#fff', border: '1px solid var(--gray-70)',
          fontFamily: 'var(--font-sans)', fontSize: 13, cursor: 'pointer', whiteSpace: 'nowrap',
          transition: 'background var(--duration-base) var(--ease-productive), border-color var(--duration-base)',
        }}
          onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--gray-80)'; e.currentTarget.style.borderColor = 'var(--gray-50)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = 'var(--gray-70)'; }}>
          <Icon name="upload" size={15} /> Upload transcript
        </button>

        {account ? (
          <button onClick={onManage} title={account.email} style={{
            height: 32, padding: '0 6px 0 10px', display: 'inline-flex', alignItems: 'center', gap: 8,
            background: 'var(--gray-90)', color: '#fff', border: '1px solid var(--gray-70)', cursor: 'pointer',
            fontFamily: 'var(--font-sans)', fontSize: 12.5,
          }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, color: 'var(--green-50)' }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--green-50)' }} />
            </span>
            <span style={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{account.email}</span>
            <span style={{ width: 24, height: 24, borderRadius: '50%', background: 'var(--blue-60)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 600 }}>{account.initials}</span>
          </button>
        ) : (
          <button onClick={onAvatar} style={{
            width: 32, height: 32, borderRadius: '50%', background: 'var(--gray-80)',
            border: '1px solid var(--gray-60)', color: 'var(--gray-30)', cursor: 'pointer',
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            transition: 'background var(--duration-base) var(--ease-productive)',
          }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--blue-60)'; e.currentTarget.style.color = '#fff'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'var(--gray-80)'; e.currentTarget.style.color = 'var(--gray-30)'; }}>
            <Icon name="user" size={16} />
          </button>
        )}
      </div>
    </header>
  );
}
window.AppHeader = AppHeader;
