from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from novel_auto_gen.core.config import AppConfig
from novel_auto_gen.core.evaluation.evaluator import HeuristicEvaluator
from novel_auto_gen.core.memory.context_manager import ContextManager
from novel_auto_gen.core.models import Bible, ChapterDraft, ChapterPlan, ConceptPlan, Outline, RunArtifact, generate_id
from novel_auto_gen.core.prompts.manager import PromptManager
from novel_auto_gen.core.providers.service import ProviderService
from novel_auto_gen.core.revision.reviser import RevisionPlanner
from novel_auto_gen.core.storage.repository import JsonRepository


class PipelineEngine:
    def __init__(
        self,
        config: AppConfig,
        provider: ProviderService,
        prompt_manager: PromptManager,
        repository: JsonRepository,
    ) -> None:
        self.config = config
        self.provider = provider
        self.prompts = prompt_manager
        self.repo = repository
        self.evaluator = HeuristicEvaluator()
        self.revision_planner = RevisionPlanner()

    def init_project(self, name: str, description: str) -> dict[str, Any]:
        project_id = generate_id("project")
        data = {"project_id": project_id, "name": name, "description": description}
        self.repo.write_json(f"projects/{project_id}/project.json", data)
        return data

    def start_run(self, project_id: str, version: int = 1) -> RunArtifact:
        run = RunArtifact(
            run_id=generate_id("run"),
            project_id=project_id,
            version=version,
            config_snapshot=self.config.raw,
            status="started",
        )
        self.repo.write_json(f"runs/{run.run_id}/meta.json", run)
        return run

    def generate_concepts(self, run_id: str, candidate_count: int = 3) -> list[ConceptPlan]:
        candidates = []
        for i in range(candidate_count):
            prompt = self.prompts.render(
                "planner",
                genre=self.config.generation.get("genre", "現代ファンタジー"),
                target_reader="一般文芸読者",
                idx=i + 1,
            )
            _ = self.provider.generate("企画者", prompt, temperature=self.config.generation.get("temperature", 0.7))
            candidates.append(
                ConceptPlan(
                    genre=self.config.generation.get("genre", "現代ファンタジー"),
                    concept=f"候補{i+1}: 記憶改竄が都市インフラ化した社会での抗争",
                    theme="自由意志と責任",
                    target_reader="25-45歳の長編読者",
                    logline=f"候補{i+1}: 過去を書き換える企業に家族を奪われた主人公の再生譚",
                )
            )
        self.repo.write_json(f"runs/{run_id}/concept_candidates.json", [asdict(c) for c in candidates])
        return candidates

    def build_bible(self, run_id: str, concept: ConceptPlan) -> Bible:
        prompt = self.prompts.render("character_designer", concept=concept.concept, theme=concept.theme)
        _ = self.provider.generate("キャラクター設計者", prompt)
        bible = Bible(
            world_bible="2038年の東京湾岸。記憶証券市場が存在し、人格信用スコアが支配する。",
            character_bible=[
                {"name": "篠宮 凛", "speech": "簡潔で断定的", "value": "責任", "principle": "犠牲は最小化"},
                {"name": "真壁 透", "speech": "比喩が多い", "value": "自由", "principle": "管理社会への抵抗"},
            ],
            style_guide="三人称限定視点。簡潔で硬質な文体。比喩は章あたり2回以内。",
            restrictions=self.config.generation.get("prohibited_expressions", []),
            foreshadowing_list=["凛の左手の古傷", "透が隠す旧型記憶鍵", "湾岸停電予告"],
            glossary=[{"term": "記憶証券", "description": "記憶を担保化した金融商品"}],
            timeline=[{"time": "2038-04", "event": "記憶証券取引所の本格稼働"}],
        )
        self.repo.write_json(f"runs/{run_id}/bible.json", bible)
        return bible

    def build_outline(self, run_id: str, bible: Bible) -> Outline:
        chapter_count = int(self.config.generation.get("chapter_count", 8))
        chapters: list[ChapterPlan] = []
        for n in range(1, chapter_count + 1):
            chapters.append(
                ChapterPlan(
                    chapter_number=n,
                    title=f"第{n}章 境界線",
                    purpose="主人公の目的達成を一段進める",
                    emotional_curve="抑制→葛藤→決意",
                    information_reveal="敵対企業の内部事情を1つ開示",
                    scene_breakdown=[
                        {"scene": 1, "goal": "調査", "conflict": "監視強化", "turn": "協力者の裏切り示唆"},
                        {"scene": 2, "goal": "対話", "conflict": "価値観衝突", "turn": "共闘の条件提示"},
                    ],
                )
            )
        outline = Outline(structure_summary="三幕構成で崩壊した信頼を再構築する復讐譚。", chapters=chapters)
        self.repo.write_json(f"runs/{run_id}/outline.json", outline)
        return outline

    def generate_chapters(self, run_id: str, bible: Bible, outline: Outline, upto: int | None = None) -> list[ChapterDraft]:
        context = ContextManager()
        context.state.character_bible = bible.character_bible
        context.state.world_bible = bible.world_bible
        context.state.glossary = bible.glossary
        context.state.timeline = bible.timeline
        context.state.foreshadow_ledger = bible.foreshadowing_list

        limit = upto or len(outline.chapters)
        drafts: list[ChapterDraft] = []
        for chapter in outline.chapters[:limit]:
            ch_ctx = context.build_chapter_context(chapter.chapter_number)
            prompt = self.prompts.render(
                "novelist",
                chapter_title=chapter.title,
                purpose=chapter.purpose,
                conflict=chapter.scene_breakdown[0]["conflict"],
                context=str(ch_ctx),
            )
            generated = self.provider.generate("本文執筆者", prompt)
            draft = ChapterDraft(
                chapter_number=chapter.chapter_number,
                title=chapter.title,
                outline=chapter.purpose,
                draft_text=f"{generated}\n\n（本文ドラフト。TODO: 実モデルで長文化）",
                chapter_summary=f"{chapter.title}では協力と裏切りの兆候が示される。",
                known_facts=[f"事実: 第{chapter.chapter_number}章で取引所の秘密が判明"],
                unresolved_elements=["凛の古傷の由来", "停電予告の真意"],
            )
            drafts.append(draft)
            context.update_from_chapter(
                chapter.chapter_number,
                draft.chapter_summary,
                draft.known_facts,
                draft.unresolved_elements,
            )

        self.repo.write_json(f"runs/{run_id}/chapters.json", drafts)
        return drafts

    def evaluate(self, run_id: str, chapters: list[ChapterDraft]) -> dict[str, Any]:
        report = self.evaluator.evaluate([c.draft_text for c in chapters])
        markdown = self.evaluator.to_markdown(report)
        self.repo.write_json(f"runs/{run_id}/evaluation.json", self.evaluator.to_jsonable(report))
        self.repo.write_markdown(f"runs/{run_id}/evaluation.md", markdown)
        revision = self.revision_planner.create_instruction(run_id, report)
        self.repo.write_json(f"runs/{run_id}/revision_instruction.json", revision)
        return {"report": report, "revision": revision}

    def save_feedback(self, run_id: str, feedback: str) -> Path:
        rel = f"runs/{run_id}/feedback.md"
        return self.repo.write_markdown(rel, feedback)
