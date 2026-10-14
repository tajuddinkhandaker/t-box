"""T-BOX interactive shell."""
import atexit
import json
import os
import platform
import queue
import random
import readline
import select
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

try:
    import termios
    import tty
except ImportError:  # pragma: no cover - Docker runs Linux; keeps imports portable.
    termios = tty = None

from . import ollama
from .catalog import CATALOG, supported
from .router import choose

VERSION = "0.1.0"
HISTORY_FILE = Path(os.getenv("TBOX_HISTORY", ".tbox_history"))

COMMANDS = {
    "/help": "show commands", "/exit": "close T-BOX", "/health": "check Ollama",
    "/models": "show models suitable for this device", "/pull N|NAME": "download a model",
    "/model N|NAME": "select a model",
}

WAITING_PHRASES = (
    "Thinking", "Cooking", "Woodgabasting", "Bubbling", "Noodling",
    "Cogitating", "Whirring", "Mulling", "Percolating", "Waffling",
    "Brain-simmering", "Gizmofying", "Flibbertigibbeting", "Mumbo-jumboing",
    "Sprocket-spinning", "Wiggle-wrangling", "Idea-marinating",
)
WAITING_COLORS = ("\033[36m", "\033[35m", "\033[33m", "\033[32m", "\033[34m")
RESET_COLOR = "\033[0m"
YELLOW = "\033[33m"


class _WaitingStatus:
    """Show a light-hearted progress message until an Ollama call completes."""

    def __init__(self, interval: float = 1.5) -> None:
        self.interval = interval
        self.enabled = sys.stdout.isatty()
        self.done = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.shown = False

    def _run(self) -> None:
        while not self.done.wait(self.interval):
            if not self.enabled:
                continue
            color = random.choice(WAITING_COLORS)
            print(
                f"\033[2K\r{color}{random.choice(WAITING_PHRASES)} ...{RESET_COLOR}",
                end="",
                flush=True,
            )
            self.shown = True

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.done.set()
        self.thread.join()
        if self.shown:
            print("\033[2K\r", end="", flush=True)


class _EscapeListener:
    """Read ESC immediately without leaving the terminal in raw mode."""

    def __enter__(self):
        self.enabled = bool(sys.stdin.isatty() and termios and tty)
        self.settings = None
        if self.enabled:
            self.settings = termios.tcgetattr(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
        return self

    def pressed(self) -> bool:
        if not self.enabled or not select.select([sys.stdin], [], [], 0)[0]:
            return False
        return sys.stdin.read(1) == "\x1b"

    def __exit__(self, *_):
        if self.settings is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.settings)


def _chat_with_abort(model: str, prompt: str) -> str | None:
    result: queue.Queue[tuple[bool, str]] = queue.Queue()

    def work() -> None:
        try:
            result.put((True, ollama.chat(model, prompt)))
        except OSError as exc:
            result.put((False, str(exc)))

    threading.Thread(target=work, daemon=True).start()
    with _EscapeListener() as keys, _WaitingStatus():
        while True:
            if keys.pressed():
                return None
            try:
                ok, value = result.get(timeout=0.1)
                if ok:
                    return value
                raise OSError(value)
            except queue.Empty:
                continue


def _ram_gb() -> str:
    try:
        total = int(open("/proc/meminfo").readline().split()[1]) * 1024
        return f"{total / 1024**3:.1f} GB"
    except OSError:
        return "unknown"


def _ram_value() -> float:
    try:
        return int(open("/proc/meminfo").readline().split()[1]) * 1024 / 1024**3
    except OSError:
        return 32  # declared target machine; overridden by Docker's visible memory on Linux


def _pick_model(value: str) -> str | None:
    choices = supported(_ram_value())
    if value.isdigit() and 1 <= int(value) <= len(choices):
        return choices[int(value) - 1].name
    return next((model.name for model in CATALOG if model.name == value), None)


def _show_models() -> None:
    try:
        installed = set(ollama.models())
    except OSError:
        installed = set()
    for number, model in enumerate(supported(_ram_value()), 1):
        state = "installed" if model.name in installed else "available"
        print(f"{number}. {model.name} | {model.size} | {model.workload} | {state}")


def _loaded_model() -> str:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        with urllib.request.urlopen(f"{host}/api/ps", timeout=1) as response:
            models = json.load(response).get("models", [])
            if models:
                return models[0].get("name", "unknown")
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        pass
    return f"none (default: {os.getenv('TBOX_DEFAULT_MODEL', 'qwen3:14b')})"


def _greeting() -> str:
    cpu = os.cpu_count() or "unknown"
    return (
        f"T-BOX v{VERSION} | Tajuddin-SandBox\n"
        f"Model: {_loaded_model()}\n"
        f"Runtime: {platform.system()} {platform.machine()} | CPU: {cpu} threads | RAM: {_ram_gb()}\n"
        "Type /help for commands."
    )


def _history() -> None:
    try:
        readline.read_history_file(HISTORY_FILE)
    except OSError:
        pass
    readline.set_history_length(1_000)
    atexit.register(lambda: readline.write_history_file(HISTORY_FILE))


def _pull(model: str) -> None:
    for update in ollama.pull(model):
        status = update.get("status", "pulling")
        total, done = update.get("total"), update.get("completed")
        progress = f" {done * 100 // total}%" if total and done is not None else ""
        print(f"\r{status}{progress}", end="", flush=True)
    print("\nReady.")


def main() -> None:
    _history()
    print(_greeting())
    selected: str | None = None
    while True:
        try:
            value = input("tbox> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if value == "/exit":
            return
        if value == "/help":
            print("\n".join(f"{key} - {text}" for key, text in COMMANDS.items()))
        elif value == "/health":
            try:
                print(f"Ollama: ready | loaded: {', '.join(ollama.running()) or 'none'}")
            except OSError:
                print("Ollama: unavailable")
        elif value == "/models":
            try:
                _show_models()
                print("Use /pull N to download, /model N to select.")
            except OSError as exc:
                print(f"Ollama: unavailable | {exc}")
        elif value.startswith("/pull "):
            model = _pick_model(value.removeprefix("/pull ").strip())
            if not model:
                print("Unknown or unsupported model.")
            else:
                try:
                    print(f"Pulling {model}...")
                    _pull(model)
                except OSError as exc:
                    print(f"Ollama: unavailable | {exc}")
        elif value.startswith("/model "):
            selected = _pick_model(value.removeprefix("/model ").strip())
            print(f"Selected: {selected}" if selected else "Unknown or unsupported model.")
        elif value:
            model = selected or choose(value)
            try:
                if model not in ollama.models():
                    print(f"Pulling {model}...")
                    _pull(model)
                answer = _chat_with_abort(model, value)
                print(f"{YELLOW}Aborted.{RESET_COLOR}" if answer is None else answer)
            except OSError as exc:
                print(f"Ollama: unavailable | {exc}")
