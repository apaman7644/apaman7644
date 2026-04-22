from __future__ import annotations

from pathlib import Path

from novel_auto_gen.core.models import ChapterDraft


class ManuscriptExporter:
    def __init__(self, output_root: str | Path) -> None:
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)

    def export_markdown(self, project_name: str, chapters: list[ChapterDraft]) -> Path:
        content = [f"# {project_name}", ""]
        for ch in chapters:
            content.append(f"## 第{ch.chapter_number}章 {ch.title}")
            content.append("")
            content.append(ch.draft_text)
            content.append("")
        path = self.output_root / "manuscript.md"
        path.write_text("\n".join(content), encoding="utf-8")
        return path

    def export_txt(self, chapters: list[ChapterDraft]) -> Path:
        content = "\n\n".join([ch.draft_text for ch in chapters])
        path = self.output_root / "manuscript.txt"
        path.write_text(content, encoding="utf-8")
        return path

    def export_split_chapters(self, chapters: list[ChapterDraft]) -> list[Path]:
        out = []
        for ch in chapters:
            p = self.output_root / "chapters" / f"chapter_{ch.chapter_number:02d}.txt"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(ch.draft_text, encoding="utf-8")
            out.append(p)
        return out
