from __future__ import annotations

from dataclasses import dataclass
from time import sleep
from typing import Any

from .base import BaseProvider, ModelRequest


@dataclass
class ProviderService:
    provider: BaseProvider
    retry_count: int = 2
    retry_interval_sec: float = 0.1

    def generate(self, role: str, prompt: str, temperature: float = 0.7) -> str:
        request = ModelRequest(role=role, prompt=prompt, temperature=temperature)
        return self._retry_call(lambda: self.provider.generate(request))

    def generate_json(self, role: str, prompt: str, temperature: float = 0.2) -> dict[str, Any]:
        request = ModelRequest(role=role, prompt=prompt, temperature=temperature, as_json=True)
        return self._retry_call(lambda: self.provider.generate_json(request))

    def _retry_call(self, fn):
        last_error = None
        for i in range(self.retry_count + 1):
            try:
                return fn()
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if i < self.retry_count:
                    sleep(self.retry_interval_sec)
        raise RuntimeError(f"provider call failed after retries: {last_error}") from last_error
