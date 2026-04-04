import React, { useState } from 'react';
import './fonts.css'; 
import './App.css';

function App() {
  const [view, setView] = useState('REGISTER'); // REGISTER or DASHBOARD
  const [status, setStatus] = useState('READY'); 
  const [userId, setUserId] = useState('');
  const [history, setHistory] = useState([
    { id: 1, amount: 120.50, status: 'SUCCESS', time: '10:30 AM' },
    { id: 2, amount: 45.00, status: 'SUCCESS', time: '12:15 PM' }
  ]);

  const handleAction = async (endpoint) => {
    if (!userId) { alert("Please enter User ID"); return; }
    setStatus('SCANNING');

    try {
      const response = await fetch(`http://localhost:8000/${endpoint}?user_id=${userId}`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (data.status === 'SUCCESS') {
        setStatus('SUCCESS');
        if (endpoint === 'verify') {
          // Add new international transaction to history
          const newTx = { id: Date.now(), amount: 500.00, status: 'SUCCESS', time: 'Now' };
          setHistory([newTx, ...history]);
        }
        setTimeout(() => setStatus('READY'), 4000);
      } else {
        setStatus('ERROR');
        setTimeout(() => setStatus('READY'), 3000);
      }
    } catch (error) {
      setStatus('ERROR');
    }
  };

  return (
    <div className="App">
      <header className="dashboard-header">
        <h1 className="brand-title">FACESECURE PAY <span className="intl-tag">INTL</span></h1>
        <nav className="view-switcher">
          <button onClick={() => setView('REGISTER')} className={view === 'REGISTER' ? 'active' : ''}>Registration</button>
          <button onClick={() => setView('DASHBOARD')} className={view === 'DASHBOARD' ? 'active' : ''}>Terminal</button>
        </nav>
      </header>

      <main className="main-container">
        {view === 'REGISTER' ? (
          <div className="auth-card">
            <h2>User Enrollment</h2>
            <input 
              type="text" 
              placeholder="Enter International User ID" 
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="id-input"
            />
            <button className="action-btn" onClick={() => handleAction('register')}>
              {status === 'SCANNING' ? 'Capturing...' : 'Capture & Register'}
            </button>
            <p className="status-msg">Status: {status}</p>
          </div>
        ) : (
          <div className="dashboard-grid">
            {/* Left: Biometric Scanner */}
            <div className={`face-id-card ${status === 'SUCCESS' ? 'success-glow' : ''}`}>
              <h3>Biometric Vault</h3>
              <p className="active-user">User: {userId || "Select User"}</p>
              <div className="biometric-trigger" onClick={() => handleAction('verify')}>
                <div className="scanner-box">
                  {status === 'SCANNING' && <div className="scan-line"></div>}
                  <p>{status === 'READY' ? 'INITIATE $500.00 TX' : status}</p>
                </div>
              </div>
            </div>

            {/* Right: Transaction History (USD) */}
            <div className="history-card">
              <h3>Global Ledger (SHA-256)</h3>
              <div className="history-list">
                {history.map(tx => (
                  <div key={tx.id} className="history-item">
                    <span>{tx.time}</span>
                    <span className="tx-amount">${tx.amount.toFixed(2)} USD</span>
                    <span className="tx-status">{tx.status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;