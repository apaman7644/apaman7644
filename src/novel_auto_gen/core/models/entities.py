from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


@dataclass
class Project:
    project_id: str
    name: str
    description: str
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass
class NovelSpec:
    target_chars: int
    chapter_count: int
    chars_per_chapter: int
    genre: str
    style: str
    prohibited_expressions: list[str]
    safety: dict[str, Any]


@dataclass
class ConceptPlan:
    genre: str
    concept: str
    theme: str
    target_reader: str
    logline: str


@dataclass
class Bible:
    world_bible: str
    character_bible: list[dict[str, Any]]
    style_guide: str
    restrictions: list[str]
    foreshadowing_list: list[str]
    glossary: list[dict[str, str]]
    timeline: list[dict[str, str]]


@dataclass
class ChapterPlan:
    chapter_number: int
    title: str
    purpose: str
    emotional_curve: str
    information_reveal: str
    scene_breakdown: list[dict[str, Any]]


@dataclass
class Outline:
    structure_summary: str
    chapters: list[ChapterPlan]


@dataclass
class ChapterDraft:
    chapter_number: int
    title: str
    outline: str
    draft_text: str
    chapter_summary: str
    known_facts: list[str]
    unresolved_elements: list[str]


@dataclass
class ScoreItem:
    score: float
    strengths: list[str]
    issues: list[str]
    suggestions: list[str]


@dataclass
class EvaluationReport:
    overall_score: float
    dimensions: dict[str, ScoreItem]
    priorities_top3: list[str]
    created_at: str = field(default_factory=utc_now_iso)


@dataclass
class RevisionInstruction:
    instruction_id: str
    derived_from_run_id: str
    derived_from_evaluation_id: str
    summary: str
    directives: list[str]
    created_at: str = field(default_factory=utc_now_iso)


@dataclass
class FeedbackEntry:
    feedback_id: str
    run_id: str
    content: str
    tags: list[str]
    created_at: str = field(default_factory=utc_now_iso)


@dataclass
class RunArtifact:
    run_id: str
    project_id: str
    version: int
    config_snapshot: dict[str, Any]
    status: str
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
