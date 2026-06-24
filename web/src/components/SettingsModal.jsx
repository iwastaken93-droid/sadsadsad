import React, { useState, useEffect } from 'react';

const API = 'http://localhost:8137';

export default function SettingsModal({ config, onClose, onSave }) {
  const [apiKey, setApiKey] = useState('');
  const [apiBase, setApiBase] = useState('https://api.openai.com/v1');
  const [model, setModel] = useState('gpt-4o');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (config) {
      setApiKey(config.api_key_configured ? '••••••••••••••••' : '');
      setApiBase(config.api_base || 'https://api.openai.com/v1');
      setModel(config.model || 'gpt-4o');
    }
  }, [config]);

  const handleSave = async () => {
    try {
      await fetch(`${API}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKey.startsWith('••') ? '' : apiKey,
          api_base: apiBase,
          model,
          roast_level: 'savage',
          persona: config?.persona || 'disappointed_mentor',
        }),
      });
      setSaved(true);
      setTimeout(() => { onSave?.(); onClose(); }, 1200);
    } catch (e) {
      alert('Could not save. Make sure RoastMe is running (roastme serve).');
    }
  };

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-modal" onClick={e => e.stopPropagation()}>
        <h2>⚙️ Settings</h2>
        <p style={{ color: 'var(--text-dim)', marginBottom: 20, fontSize: 14 }}>
          Configure your AI provider. Works with OpenAI, Anthropic (via proxy), Ollama, or any OpenAI-compatible API.
        </p>

        <div className="form-group">
          <label>🔑 API Key</label>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder="sk-... (your secret key)"
          />
          <div className="help">Your key is stored locally and never sent anywhere except your chosen API.</div>
        </div>

        <div className="form-group">
          <label>🌐 API URL</label>
          <input
            value={apiBase}
            onChange={e => setApiBase(e.target.value)}
            placeholder="https://api.openai.com/v1"
          />
          <div className="help">Default: https://api.openai.com/v1 — change for Ollama, OpenRouter, etc.</div>
        </div>

        <div className="form-group">
          <label>🤖 Model Name</label>
          <input
            value={model}
            onChange={e => setModel(e.target.value)}
            placeholder="gpt-4o"
          />
          <div className="help">Examples: gpt-4o, gpt-3.5-turbo, llama3, claude-3-opus</div>
        </div>

        <div className="settings-buttons">
          <button className="btn btn-primary" onClick={handleSave}>
            {saved ? '✅ Saved!' : '💾 Save Settings'}
          </button>
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
