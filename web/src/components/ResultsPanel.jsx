import React from 'react';

export default function ResultsPanel({ result, scoreColor }) {
  if (!result) return null;

  const shameText =
    result.shame_score < 10 ? 'Suspiciously Clean 🤔' :
    result.shame_score < 25 ? 'Not Bad 😏' :
    result.shame_score < 45 ? 'Needs Work 😬' :
    result.shame_score < 65 ? 'Concerning 😰' :
    result.shame_score < 85 ? 'Disastrous 💀' :
    'Absolutely Catastrophic 🔥💀🔥';

  return (
    <div className="results">
      {/* Shame Score */}
      <div className="shame-header">
        <div className="shame-circle" style={{ borderColor: scoreColor }}>
          <span className="number" style={{ color: scoreColor }}>{result.shame_score}</span>
          <span className="label">Shame</span>
        </div>
        <div className="shame-info">
          <div className="score-label">Your Shame Score (lower is better)</div>
          <div className="score-text">{shameText}</div>
          {result.persona_name && (
            <div className="persona-name">Roasted by: {result.persona_name}</div>
          )}
        </div>
      </div>

      {/* Overall Roast */}
      {result.overall_roast && (
        <div className="roast-card">
          <h3>🔥 The Roast</h3>
          <div className="roast-body">{result.overall_roast}</div>
        </div>
      )}

      {/* Line Roasts */}
      {result.line_roasts?.length > 0 && (
        <div className="findings-card">
          <h3>🎯 Line-by-Line Burns</h3>
          {result.line_roasts.map((lr, i) => (
            <div key={i} className="finding-row">
              <span className="line-num">Line {lr.line}</span>
              <div style={{ flex: 1 }}>
                <div className="msg">{lr.roast}</div>
                <div className="hint">💡 Fix: {lr.suggestion}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Findings (Analyze mode) */}
      {result.findings?.length > 0 && (
        <div className="findings-card">
          <h3>🔍 Issues Found</h3>
          {result.findings.map((f, i) => (
            <div key={i} className="finding-row">
              <span className="line-num">L{f.line}</span>
              <span className={`sev sev-${f.severity}`}>{f.severity}</span>
              <div style={{ flex: 1 }}>
                <div className="msg">{f.message}</div>
                {f.roast_hint && <div className="hint">🔥 {f.roast_hint}</div>}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Refactoring Suggestions */}
      {result.refactoring_suggestions?.length > 0 && (
        <div className="suggestions-card">
          <h3>💡 How to Fix It</h3>
          {result.refactoring_suggestions.map((s, i) => (
            <div key={i} className="suggestion-row">
              <span className="num">{i + 1}</span>
              <span className="text">{s}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
