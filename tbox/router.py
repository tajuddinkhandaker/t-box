"""Conservative task-to-model routing."""
MODELS = {
    "general": "qwen3:14b",
    "coding": "qwen2.5-coder:14b",
    "math": "deepseek-r1:14b",
}


def choose(prompt: str) -> str:
    text = prompt.lower()
    if any(word in text for word in ("code", "python", "script", "bug", "docker", "powershell")):
        return MODELS["coding"]
    if any(word in text for word in ("math", "calculate", "equation", "proof")):
        return MODELS["math"]
    return MODELS["general"]
