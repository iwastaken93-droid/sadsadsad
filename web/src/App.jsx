import React, { useState, useCallback, useEffect } from 'react';
import PersonaSelector from './components/PersonaSelector.jsx';
import FileDropZone from './components/FileDropZone.jsx';
import ResultsPanel from './components/ResultsPanel.jsx';
import SettingsModal from './components/SettingsModal.jsx';

const API = 'http://localhost:8137';

export default function App() {
  const [step, setStep] = useState(1); // 1=file, 2=persona, 3=roast
  const [file, setFile] = useState(null);
  const [source, setSource] = useState('');
  const [persona, setPersona] = useState('');
  const [level, setLevel] = useState('savage');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState('unknown');
  const [config, setConfig] = useState(null);

  // Check backend status on mount
  useEffect(() => {
    checkBackend();
    loadConfig();
  }, []);

  const checkBackend = async () => {
    try {
      await fetch(`${API}/api/personas`);
      setBackendStatus('connected');
    } catch {
      setBackendStatus('error');
    }
  };

  const loadConfig = async () => {
    try {
      const res = await fetch(`${API}/api/config`);
      const data = await res.json();
      setConfig(data);
      if (data.persona) setPersona(data.persona);
    } catch { /* ignore */ }
  };

  const handleFileLoaded = useCallback((name, content) => {
    setFile({ name, size: content.length });
    setSource(content);
    setResult(null);
    setError('');
    setStep(2);
  }, []);

  const handleRoast = useCallback(async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch(`${API}/api/roast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source,
          file_path: file?.name || 'untitled.py',
          config: {
            api_key: config?.api_key || '',
            api_base: config?.api_base || 'https://api.openai.com/v1',
            model: config?.model || 'gpt-4o',
            roast_level: level,
            persona,
          },
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Roast failed. Check your settings.');
      }

      const data = await res.json();
      setResult(data);
      setStep(3);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [source, file, persona, level, config]);

  const handleAnalyze = useCallback(async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch(`${API}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, file_path: file?.name || 'untitled.py' }),
      });

      if (!res.ok) throw new Error('Analysis failed');

      const data = await res.json();
      setResult(data);
      setStep(3);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [source, file]);

  const scoreColor = result?.shame_score < 20 ? 'var(--success)' : result?.shame_score < 50 ? 'var(--accent-warm)' : 'var(--accent)';

  return (
    <div className="app">
      {/* Top Bar */}
      <header className="topbar">
        <div className="topbar-logo">
          <span className="fire">🔥</span>
          <span className="title">RoastMe</span>
        </div>
        <div className="topbar-steps">
          <span className={`step-badge ${step >= 1 ? (step === 1 ? 'active' : 'done') : ''}`}>
            {step > 1 ? '✅' : '1️⃣'} Pick File
          </span>
          <span className={`step-badge ${step >= 2 ? (step === 2 ? 'active' : 'done') : ''}`}>
            {step > 2 ? '✅' : '2️⃣'} Choose Roaster
          </span>
          <span className={`step-badge ${step >= 3 ? 'active' : ''}`}>
            3️⃣ Get Roasted
          </span>
        </div>
      </header>

      {/* Main */}
      <div className="main">
        {/* Left Panel */}
        <aside className="panel-left">
          {/* Step 1: File */}
          <div>
            <div className="section-title">📄 Step 1: Pick Your Code</div>
            <FileDropZone onFileLoaded={handleFileLoaded} />
            {file && (
              <div className="file-loaded" style={{ marginTop: 12 }}>
                <span className="file-icon">📄</span>
                <div>
                  <div className="file-name">{file.name}</div>
                  <div className="file-size">{file.size.toLocaleString()} characters</div>
                </div>
              </div>
            )}
          </div>

          {/* Step 2: Persona */}
          {step >= 2 && (
            <div>
              <div className="section-title">🎭 Step 2: Choose Your Roaster</div>
              <PersonaSelector selected={persona} onSelect={setPersona} />

              <div className="section-title" style={{ marginTop: 16 }}>🌶️ Heat Level</div>
              <div className="level-buttons">
                {[
                  { id: 'mild', label: '🌶️ Mild' },
                  { id: 'medium', label: '🌶️🌶️ Medium' },
                  { id: 'savage', label: '🔥 Savage' },
                  { id: 'nuclear', label: '☢️ Nuclear' },
                ].map(l => (
                  <button
                    key={l.id}
                    className={`level-btn ${level === l.id ? 'selected' : ''}`}
                    onClick={() => setLevel(l.id)}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Action */}
          {step >= 2 && !loading && !result && (
            <div>
              <div className="section-title">🚀 Step 3: Roast It!</div>
              <button className="roast-button" onClick={handleRoast} disabled={!persona}>
                🔥 ROAST MY CODE 🔥
              </button>
              <button
                className="roast-button"
                style={{ background: 'linear-gradient(135deg, #4499ff, #2266cc)', marginTop: 10, fontSize: 16, padding: '14px' }}
                onClick={handleAnalyze}
              >
                🔍 Just Analyze (No Roast)
              </button>
            </div>
          )}
        </aside>

        {/* Right Panel */}
        <div className="panel-right">
          {loading && (
            <div className="loading-state">
              <div className="loading-fire">🔥</div>
              <div className="loading-text">Roasting your code... this might take a moment...</div>
            </div>
          )}

          {error && (
            <div className="empty-state" style={{ color: 'var(--accent)' }}>
              <div className="icon">😢</div>
              <h2>Something went wrong</h2>
              <p>{error}</p>
              <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => setSettingsOpen(true)}>
                ⚙️ Check Settings
              </button>
            </div>
          )}

          {result && !loading && <ResultsPanel result={result} scoreColor={scoreColor} />}

          {!result && !loading && !error && (
            <div className="empty-state">
              <div className="icon">🔥</div>
              <h2>Your code is about to get roasted!</h2>
              <p>
                <strong>Step 1:</strong> Drop or paste a code file on the left<br/>
                <strong>Step 2:</strong> Pick who roasts you and how hard<br/>
                <strong>Step 3:</strong> Hit the big red button and enjoy the burns!
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Status Bar */}
      <footer className="statusbar">
        <div className="status-indicator">
          <span className={`status-dot ${backendStatus}`} />
          Backend: {backendStatus === 'connected' ? '✅ Connected' : '❌ Not running — start with "roastme serve"'}
        </div>
        <div>RoastMe v0.1.0 — Your code deserves this 🔥</div>
      </footer>

      {/* Settings */}
      <button className="settings-btn" onClick={() => setSettingsOpen(true)} title="Settings">⚙️</button>

      {settingsOpen && (
        <SettingsModal
          config={config}
          onClose={() => setSettingsOpen(false)}
          onSave={() => { loadConfig(); checkBackend(); }}
        />
      )}
    </div>
  );
}
