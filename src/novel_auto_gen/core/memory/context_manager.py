from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryState:
    character_bible: list[dict[str, Any]] = field(default_factory=list)
    world_bible: str = ""
    glossary: list[dict[str, str]] = field(default_factory=list)
    timeline: list[dict[str, str]] = field(default_factory=list)
    foreshadow_ledger: list[str] = field(default_factory=list)
    chapter_summaries: dict[int, str] = field(default_factory=dict)
    scene_summaries: dict[str, str] = field(default_factory=dict)
    established_facts: list[str] = field(default_factory=list)
    unresolved_elements: list[str] = field(default_factory=list)


class ContextManager:
    def __init__(self, state: MemoryState | None = None) -> None:
        self.state = state or MemoryState()

    def build_chapter_context(self, chapter_number: int, max_recent_chapters: int = 3) -> dict[str, Any]:
        recent_keys = sorted(k for k in self.state.chapter_summaries if k < chapter_number)[-max_recent_chapters:]
        recent = {k: self.state.chapter_summaries[k] for k in recent_keys}
        return {
            "character_bible": self.state.character_bible,
            "world_bible": self.state.world_bible,
            "glossary": self.state.glossary,
            "timeline": self.state.timeline,
            "foreshadow_ledger": self.state.foreshadow_ledger,
            "recent_chapter_summaries": recent,
            "established_facts": self.state.established_facts[-50:],
            "unresolved_elements": self.state.unresolved_elements,
        }

    def update_from_chapter(self, chapter_number: int, summary: str, facts: list[str], unresolved: list[str]) -> None:
        self.state.chapter_summaries[chapter_number] = summary
        self.state.established_facts.extend(facts)
        self.state.unresolved_elements = unresolved
