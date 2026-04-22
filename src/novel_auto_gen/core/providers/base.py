from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ModelRequest:
    role: str
    prompt: str
    temperature: float = 0.7
    as_json: bool = False


class BaseProvider(ABC):
    @abstractmethod
    def generate(self, request: ModelRequest) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_json(self, request: ModelRequest) -> dict[str, Any]:
        raise NotImplementedError
