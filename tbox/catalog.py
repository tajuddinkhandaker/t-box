"""CPU-first model recommendations for the detected runtime."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Model:
    name: str
    size: str
    workload: str
    ram_gb: int


CATALOG = (
    Model("qwen3:8b", "~5.2 GB", "chat, summaries, everyday tasks", 12),
    Model("qwen3:14b", "~9.3 GB", "chat, reasoning, scripting", 20),
    Model("qwen2.5-coder:14b", "~9 GB", "complex coding, repair, refactoring", 20),
    Model("deepseek-r1:14b", "~9 GB", "complex math and reasoning", 20),
    Model("qwen3-coder:30b", "~19 GB", "advanced coding; slower, tight memory", 30),
)


def supported(ram_gb: float) -> tuple[Model, ...]:
    return tuple(model for model in CATALOG if model.ram_gb <= ram_gb)
