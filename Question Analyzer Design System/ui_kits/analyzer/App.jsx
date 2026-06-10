// Question Analyzer — consolidated app.
function App() {
  const [view, setView] = React.useState('dashboard');
  const [analysisVersion, setAnalysisVersion] = React.useState(0);
  const [uploadOpen, setUploadOpen] = React.useState(false);
  const [signInOpen, setSignInOpen] = React.useState(false);
  const [account, setAccount] = React.useState(null);

  const connect = (email) => {
    const base = email.split('@')[0].replace(/[^a-z]/gi, '');
    const initials = (base.slice(0, 2) || 'me').toUpperCase();
    setAccount({ email, initials });
    setSignInOpen(false);
  };
  const disconnect = () => { setAccount(null); setSignInOpen(false); };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#fff' }}>
      <AppHeader view={view} setView={setView} onUpload={() => setUploadOpen(true)}
        account={account} onAvatar={() => setSignInOpen(true)} onManage={() => setSignInOpen(true)} />
      <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', background: '#fff' }}>
        <div key={`${view}:${analysisVersion}`} className="qa-view">
          {view === 'dashboard' ? <DashboardView /> : <WeekView />}
        </div>
      </div>
      <UploadModal open={uploadOpen} onClose={() => setUploadOpen(false)}
        onImported={() => { setUploadOpen(false); setView('dashboard'); setAnalysisVersion((v) => v + 1); }} />
      <SignInModal open={signInOpen} onClose={() => setSignInOpen(false)}
        account={account} onConnect={connect} onDisconnect={disconnect} />
    </div>
  );
}
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
