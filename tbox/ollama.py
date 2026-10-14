"""Small Ollama HTTP client."""
import json
import os
import urllib.request

HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def request(path: str, data: dict | None = None) -> dict:
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{HOST}{path}", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as response:
        return json.load(response)


def models() -> list[str]:
    return [item["name"] for item in request("/api/tags").get("models", [])]


def running() -> list[str]:
    return [item["name"] for item in request("/api/ps").get("models", [])]


def pull(model: str):
    req = urllib.request.Request(
        f"{HOST}/api/pull", json.dumps({"name": model}).encode(), {"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=300) as response:
        for line in response:
            yield json.loads(line)


def chat(model: str, prompt: str) -> str:
    return request("/api/generate", {"model": model, "prompt": prompt, "stream": False})["response"]
