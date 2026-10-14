# Local AI Console

Build a Gemini-like terminal console that runs entirely in Docker and uses Ollama for local workloads.

## Rules
- Access it through Docker container commands only.
- Let users select a task; route it to a suitable Ollama model and pull missing models automatically.
- Store reusable user workflows in `skills/`.
- Provide `/` commands for model selection (filtered by detected device capacity) and settings.
- Show live CPU, RAM, and GPU telemetry in the background; users may disable it.
- Keep design rules and token-efficiency guidance (RPM, TPM, RPD) in `docs/`.

## Target machine
Ryzen 9 9950X, 32 GB RAM, ~485 MB VRAM: CPU-first, one model at a time, default 16K context, one parallel request.

## Model defaults
| Workload | Model |
| --- | --- |
| General chat, scripting, reasoning | `qwen3:14b` |
| Coding | `qwen2.5-coder:14b` |
| Deep math | `deepseek-r1:14b` |
| Experimental coding | `qwen3-coder:30b` (memory-sensitive) |

Ollama environment: `OLLAMA_CONTEXT_LENGTH=16384`, `OLLAMA_NUM_PARALLEL=1`.
