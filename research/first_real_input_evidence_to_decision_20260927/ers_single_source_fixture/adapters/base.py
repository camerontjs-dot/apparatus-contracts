"""Base adapter interface for LLM backends.

All adapters (Ollama, MLX, stub) implement this contract so the harness
can swap backends without code changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMAdapter(ABC):
    """Unified interface for local LLM inference."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the backend is reachable and ready."""
        ...

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> str | dict[str, Any]:
        """Generate text from prompt.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system instruction.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Hard token limit (None = backend default).
            json_mode: If True, request structured JSON output.

        Returns:
            Generated text string, or a dict when json_mode=True.
        """
        ...

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for the given texts."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable model identifier for telemetry."""
        ...

    @property
    @abstractmethod
    def adapter_name(self) -> str:
        """Backend type identifier (e.g. 'ollama', 'mlx', 'stub')."""
        ...
