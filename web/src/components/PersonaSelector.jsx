import React, { useState, useEffect } from 'react';

const FALLBACK_PERSONAS = {
  disappointed_mentor: { name: 'Disappointed Mentor', description: 'Your CS professor, deeply let down', emoji: '👨‍🏫' },
  chaos_goblin: { name: 'Chaos Goblin', description: 'Unhinged, meme-fueled destruction', emoji: '👺' },
  senior_dev_karen: { name: 'Senior Dev Karen', description: 'Corporate savage, wants the manager', emoji: '💼' },
  standup_comedian: { name: 'Standup Comedian', description: 'Your code is the punchline', emoji: '🎤' },
  drill_sergeant: { name: 'Drill Sergeant', description: 'Military-grade code destruction', emoji: '🪖' },
  therapist: { name: 'Code Therapist', description: "Let's talk about your code's issues", emoji: '🛋️' },
};

export default function PersonaSelector({ selected, onSelect }) {
  const [personas, setPersonas] = useState(FALLBACK_PERSONAS);

  useEffect(() => {
    fetch('http://localhost:8137/api/personas')
      .then(r => r.json())
      .then(data => { if (Object.keys(data).length > 0) setPersonas(data); })
      .catch(() => {});
  }, []);

  return (
    <div className="persona-grid">
      {Object.entries(personas).map(([id, p]) => (
        <div
          key={id}
          className={`persona-card ${selected === id ? 'selected' : ''}`}
          onClick={() => onSelect(id)}
        >
          <div className="emoji">{p.emoji}</div>
          <div className="name">{p.name}</div>
          <div className="desc">{p.description}</div>
        </div>
      ))}
    </div>
  );
}
