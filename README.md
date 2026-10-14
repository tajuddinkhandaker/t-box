# T-BOX

Docker-first local Ollama console.

## Overview

A terminal console that runs entirely in Docker and uses Ollama for local AI workloads. Users can select tasks, route them to suitable Ollama models, and pull missing models automatically.

## Features

- **Docker-first**: All processing runs inside Docker containers
- **Ollama integration**: Uses local Ollama models for AI workloads
- **Model selection**: Choose from multiple models filtered by device capacity
- **Skills system**: Reusable user workflows stored in `skills/`
- **Live telemetry**: CPU, RAM, and GPU monitoring in the background
- **Command palette**: `/` commands for model selection and settings
- **Token efficiency**: Guidance for RPM, TPM, RPD in `docs/`

## Target Machine

- Ryzen 9 9950X, 32 GB RAM, ~485 MB VRAM
- CPU-first architecture: one model at a time
- Default context: 16K
- One parallel request allowed

## Model Defaults

| Workload | Model |
| --- | --- |
| General chat, scripting, reasoning | `qwen3:14b` |
| Coding | `qwen2.5-coder:14b` |
| Deep math | `deepseek-r1:14b` |
| Experimental coding | `qwen3-coder:30b` (memory-sensitive) |

## Getting Started

### Prerequisites

- Docker Desktop installed
- Ollama installed and running

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/tajuddinkhandaker/t-box.git
   cd t-box
   ```

2. Copy environment file:
   ```powershell
   Copy-Item .env.example .env
   ```
   The `.env.example` file is included in the repository as a template. Copy it to `.env` and modify as needed.
=======

3. Edit `.env` to set `OLLAMA_MODELS_DIR` if needed

4. Build and start Docker containers:
   ```bash
   docker compose up -d
   ```

### Running T-BOX

```powershell
.\tbox
```

Add this project directory to `PATH` to run it as `tbox` from anywhere.

## npm Package

Requires Docker Desktop. Install the public package with `npm install -g tbox-local-ai`,
then run `tbox`. While Ollama prepares a response, T-BOX rotates playful status messages
such as `Thinking ...`, `Cooking ...`, and `Woodgabasting ...`.

Before publishing, replace the `REPLACE_WITH_OWNER` GitHub URLs in `package.json`,
then run `npm publish` while authenticated to npm.

## Project Structure

```
.
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore file
├── AGENT.md              # Agent rules and configuration
├── compose.yaml          # Docker Comfile configuration
├── Dockerfile            # Docker build file
├── LICENSE               # Project license
├── README.md             # This file
├── package.json          # npm package configuration
├── .npmignore            # npm ignore file
├── bin/
│   ├── tbox             # PowerShell script
│   └── tbox.js          # JavaScript entry point
├── docs/
│   └── architecture.md   # Architecture documentation
├── docker-tools/
│   └── docker-cleanup.ps1  # Docker cleanup utility
├── tbox/
│   ├── __init__.py       # Python package init
│   ├── __main__.py       # Python main entry
│   ├── catalog.py        # Model catalog
│   ├── cli.py            # CLI interface
│   ├── ollama.py         # Ollama integration
│   └── router.py         # Request routing
└── skills/               # Reusable user workflows
```

## License

MIT

## Repository

https://github.com/tajuddinkhandaker/t-box
=======
