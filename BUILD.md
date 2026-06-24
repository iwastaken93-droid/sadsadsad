# Building RoastMe

## Prerequisites

- [Rust](https://rustup.rs/) (1.96+)
- [Node.js](https://nodejs.org/) (18+)
- [Python](https://python.org/) (3.10+)
- [Tauri CLI](https://v2.tauri.app/start/prerequisites/)

```bash
cargo install tauri-cli
```

## Development

```bash
# 1. Install Python deps
pip install -e ".[dev]"

# 2. Install frontend deps
cd web && npm install && cd ..

# 3. Run in dev mode (hot reload)
cargo tauri dev
```

## Production Build

```bash
# Build frontend first
cd web && npm run build && cd ..

# Build the app
cargo tauri build
```

Output will be in `src-tauri/target/release/bundle/`:
- **Windows**: `.msi` installer
- **macOS**: `.dmg` disk image  
- **Linux**: `.AppImage` or `.deb` package

## GitHub Actions

Every push to `main` automatically builds for all 3 platforms and creates a GitHub Release.

To trigger manually: Go to Actions → Build & Release → "Run workflow"
