# frontend/src/App.jsx
import React, { useState } from 'react';
import TransactionUpload from './components/TransactionUpload';
import FinancialDashboard from './components/FinancialDashboard';
import AIChat from './components/AIChat';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [hasData, setHasData] = useState(false);

  const handleUploadSuccess = (data) => {
    setHasData(true);
    setActiveTab('dashboard');
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Personal Finance Coach</h1>
        <nav className="app-nav">
          <button
            className={activeTab === 'upload' ? 'active' : ''}
            onClick={() => setActiveTab('upload')}
          >
            Upload Data
          </button>
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
            disabled={!hasData}
          >
            Dashboard
          </button>
          <button
            className={activeTab === 'chat' ? 'active' : ''}
            onClick={() => setActiveTab('chat')}
            disabled={!hasData}
          >
            AI Coach
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'upload' && (
          <TransactionUpload onUploadSuccess={handleUploadSuccess} />
        )}
        {activeTab === 'dashboard' && hasData && <FinancialDashboard />}
        {activeTab === 'chat' && hasData && <AIChat />}
        
        {!hasData && activeTab !== 'upload' && (
          <div className="no-data-message">
            <h2>Welcome to your Personal Finance Coach!</h2>
            <p>Please upload your transaction data to get started.</p>
            <button onClick={() => setActiveTab('upload')}>
              Upload Transaction Data
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;