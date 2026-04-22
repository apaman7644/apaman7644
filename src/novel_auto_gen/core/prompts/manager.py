from __future__ import annotations

from pathlib import Path
from string import Template


class PromptManager:
    def __init__(self, prompt_dir: str | Path = "prompts") -> None:
        self.prompt_dir = Path(prompt_dir)

    def render(self, template_name: str, **kwargs) -> str:
        path = self.prompt_dir / f"{template_name}.txt"
        text = path.read_text(encoding="utf-8")
        return Template(text).safe_substitute(**kwargs)
