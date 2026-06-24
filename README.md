# 🔥 RoastMe — AI Code Reviewer That Roasts You

> *"Your code is about to get roasted. And honestly? It deserves it."*

RoastMe is a **real desktop app** (Windows, Mac, Linux) that doesn't just find bugs — it **absolutely destroys** your code with hilarious roasts while delivering genuinely useful refactoring suggestions.

Built with **Tauri 2** (Rust backend + React frontend) — lightweight, fast, and native.

## ✨ Features

- 🖥️ **Real Desktop App** — not a website, an actual app on your computer
- 🌶️ **4 Roast Levels**: Mild → Medium → Savage → Nuclear
- 🎭 **6 Savage Personas**: From "Disappointed Mentor" to "Chaos Goblin"
- 🔍 **Static Analysis**: Catches security vulnerabilities, anti-patterns, complexity
- 🧠 **AI-Powered Roasts**: Uses your API key with any OpenAI-compatible endpoint
- 📂 **Drag & Drop**: Just drop your code file into the window
- 🔒 **Fully Local**: Your code never leaves your machine (only API calls for roasts)
- 🔑 **BYOK**: Bring your own API key — works with OpenAI, Anthropic, local models, anything
- 👵 **Grandma-Friendly**: So simple anyone can use it

## 🚀 Quick Start

### Option 1: Download (Coming Soon)
Download the installer for your platform and double-click to install.

### Option 2: Build from Source

**Prerequisites:**
- [Rust](https://rustup.rs/) (1.96+)
- [Node.js](https://nodejs.org/) (18+)
- [Python](https://python.org/) (3.10+)

```bash
# 1. Clone this repo
git clone <repo-url> && cd roastme

# 2. Install Python backend dependencies
pip install -e ".[dev]"

# 3. Install frontend dependencies
cd web && npm install && npm run build && cd ..

# 4. Run the desktop app!
cargo tauri dev
```

### First Time Setup

When you first open RoastMe:

1. Click the **⚙️ Settings** button (bottom-right corner)
2. Enter your **API key** (get one from [OpenAI](https://platform.openai.com/api-keys))
3. Leave the API URL as default (or change it for Ollama/OpenRouter/etc.)
4. Click **Save Settings**

That's it! Now you're ready to roast.

## 🎭 Personas

| Persona | Vibe |
|---------|------|
| 👨‍🏫 **Disappointed Mentor** | Your CS professor expected better |
| 👺 **Chaos Goblin** | Unhinged, meme-fueled destruction |
| 💼 **Senior Dev Karen** | Corporate savage, wants to speak to the manager |
| 🎤 **Standup Comedian** | Comedy roast special for your code |
| 🪖 **Drill Sergeant** | Military-grade code destruction |
| 🛋️ **Code Therapist** | Analyzes your code's deep-seated issues |

## 🌶️ Roast Levels

- **Mild** — Dad jokes and light teasing
- **Medium** — Witty burns, solid sarcarism
- **Savage** — Devastating roasts, no mercy
- **Nuclear** — Total annihilation. Maximum humiliation.

## 🏗️ Architecture

```
roastme/
├── src-tauri/           # Tauri Rust backend
│   ├── src/
│   │   ├── main.rs      # App entry point
│   │   └── commands.rs  # Tauri commands (proxy to Python backend)
│   ├── Cargo.toml
│   └── tauri.conf.json
├── roastme/             # Python backend (FastAPI)
│   ├── analyzer/        # Static analysis engine
│   ├── personas/         # 6 roast persona definitions
│   ├── reviewer/        # AI review orchestration
│   ├── cli/             # Terminal CLI
│   ├── web/             # FastAPI server
│   └── config.py        # Configuration management
├── web/                 # React frontend (Vite)
│   ├── src/
│   │   ├── App.jsx      # Main app shell
│   │   ├── components/  # UI components
│   │   └── styles.css   # All styles
│   └── index.html
├── tests/               # Test suite
├── pyproject.toml       # Python package config
└── README.md
```

## 🔧 API Configuration

RoastMe works with **any OpenAI-compatible API**:

| Provider | Base URL | Model |
|----------|----------|-------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| Anthropic (via proxy) | Your proxy URL | `claude-3-opus` |
| Local (Ollama) | `http://localhost:11434/v1` | `llama3` |
| OpenRouter | `https://openrouter.ai/api/v1` | Various |

## 📊 Shame Score

Every review comes with a **Shame Score (0-100)** based on:
- Number of findings
- Severity of issues (critical > warning > info)
- Security vulnerabilities (weighted highest)
- Code complexity and anti-patterns

## 🛠️ Development

```bash
# Run Python backend only
roastme serve

# Run frontend dev server (hot reload)
cd web && npm run dev

# Build for production
cd web && npm run build
cargo tauri build

# Run tests
pytest
```

## 📝 License

MIT — Roast responsibly.
