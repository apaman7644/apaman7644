from __future__ import annotations

import hashlib
from typing import Any

from .base import BaseProvider, ModelRequest


class MockProvider(BaseProvider):
    """Deterministic provider for local development/tests."""

    def generate(self, request: ModelRequest) -> str:
        digest = hashlib.md5((request.role + request.prompt).encode("utf-8")).hexdigest()[:8]
        return f"[{request.role}] {request.prompt[:120]}... (mock:{digest})"

    def generate_json(self, request: ModelRequest) -> dict[str, Any]:
        text = self.generate(request)
        return {"role": request.role, "content": text}
