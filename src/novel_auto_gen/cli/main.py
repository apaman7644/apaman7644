from __future__ import annotations

import argparse
import json
from pathlib import Path

from novel_auto_gen.core.config import load_config
from novel_auto_gen.core.export.exporter import ManuscriptExporter
from novel_auto_gen.core.pipeline.engine import PipelineEngine
from novel_auto_gen.core.prompts.manager import PromptManager
from novel_auto_gen.core.providers.mock_provider import MockProvider
from novel_auto_gen.core.providers.service import ProviderService
from novel_auto_gen.core.revision.reviser import RunComparator
from novel_auto_gen.core.storage.repository import JsonRepository


def build_engine(config_path: str) -> PipelineEngine:
    config = load_config(config_path)
    repo = JsonRepository(config.paths.get("storage_root", "./workspace_data"))
    provider = ProviderService(MockProvider())
    prompts = PromptManager(config.paths.get("prompt_root", "prompts"))
    return PipelineEngine(config=config, provider=provider, prompt_manager=prompts, repository=repo)


def cmd_init_project(args):
    engine = build_engine(args.config)
    project = engine.init_project(args.name, args.description)
    print(json.dumps(project, ensure_ascii=False, indent=2))


def cmd_generate_novel(args):
    engine = build_engine(args.config)
    run = engine.start_run(args.project_id, args.version)
    concepts = engine.generate_concepts(run.run_id, args.candidates)
    chosen = concepts[args.pick - 1]
    bible = engine.build_bible(run.run_id, chosen)
    outline = engine.build_outline(run.run_id, bible)
    chapters = engine.generate_chapters(run.run_id, bible, outline, upto=args.upto_chapter)
    result = engine.evaluate(run.run_id, chapters)
    exporter = ManuscriptExporter(Path(engine.repo.root) / "runs" / run.run_id / "exports")
    exporter.export_markdown(args.project_id, chapters)
    exporter.export_txt(chapters)
    exporter.export_split_chapters(chapters)
    print(f"run_id={run.run_id} score={result['report'].overall_score}")


def cmd_generate_concept(args):
    engine = build_engine(args.config)
    concepts = engine.generate_concepts(args.run_id, args.candidates)
    print(json.dumps([c.__dict__ for c in concepts], ensure_ascii=False, indent=2))


def cmd_build_bible(args):
    engine = build_engine(args.config)
    concept_data = json.loads(Path(args.concept_json).read_text(encoding="utf-8"))
    from novel_auto_gen.core.models import ConceptPlan

    concept = ConceptPlan(**concept_data)
    bible = engine.build_bible(args.run_id, concept)
    print(json.dumps(bible.__dict__, ensure_ascii=False, indent=2))


def cmd_build_outline(args):
    engine = build_engine(args.config)
    bible = engine.repo.read_json(f"runs/{args.run_id}/bible.json")
    from novel_auto_gen.core.models import Bible

    outline = engine.build_outline(args.run_id, Bible(**bible))
    print(json.dumps({"chapters": len(outline.chapters)}, ensure_ascii=False, indent=2))


def cmd_generate_chapter(args):
    engine = build_engine(args.config)
    from novel_auto_gen.core.models import Bible, Outline, ChapterPlan

    bible = Bible(**engine.repo.read_json(f"runs/{args.run_id}/bible.json"))
    outline_raw = engine.repo.read_json(f"runs/{args.run_id}/outline.json")
    outline = Outline(
        structure_summary=outline_raw["structure_summary"],
        chapters=[ChapterPlan(**c) for c in outline_raw["chapters"]],
    )
    drafts = engine.generate_chapters(args.run_id, bible, outline, upto=args.upto)
    print(json.dumps({"generated": len(drafts)}, ensure_ascii=False, indent=2))


def cmd_evaluate(args):
    engine = build_engine(args.config)
    from novel_auto_gen.core.models import ChapterDraft

    raws = engine.repo.read_json(f"runs/{args.run_id}/chapters.json")
    drafts = [ChapterDraft(**r) for r in raws]
    result = engine.evaluate(args.run_id, drafts)
    print(json.dumps({"overall": result["report"].overall_score}, ensure_ascii=False, indent=2))


def cmd_revise(args):
    engine = build_engine(args.config)
    rev = engine.repo.read_json(f"runs/{args.run_id}/revision_instruction.json")
    print(json.dumps(rev, ensure_ascii=False, indent=2))


def cmd_compare_runs(args):
    engine = build_engine(args.config)
    comparator = RunComparator()
    from novel_auto_gen.core.models import EvaluationReport, ScoreItem

    def load_report(run_id: str):
        raw = engine.repo.read_json(f"runs/{run_id}/evaluation.json")
        dims = {k: ScoreItem(**v) for k, v in raw["dimensions"].items()}
        return EvaluationReport(overall_score=raw["overall_score"], dimensions=dims, priorities_top3=raw["priorities_top3"])

    previous = load_report(args.previous_run)
    current = load_report(args.current_run)
    diff = comparator.compare_scores(previous, current)
    engine.repo.write_json(f"comparisons/{args.previous_run}_vs_{args.current_run}.json", diff)
    print(json.dumps(diff, ensure_ascii=False, indent=2))


def cmd_apply_feedback(args):
    engine = build_engine(args.config)
    engine.save_feedback(args.run_id, args.feedback)
    print("saved")


def cmd_export_manuscript(args):
    engine = build_engine(args.config)
    from novel_auto_gen.core.models import ChapterDraft

    raws = engine.repo.read_json(f"runs/{args.run_id}/chapters.json")
    chapters = [ChapterDraft(**r) for r in raws]
    exporter = ManuscriptExporter(Path(engine.repo.root) / "runs" / args.run_id / "exports")
    md = exporter.export_markdown(args.project_name, chapters)
    txt = exporter.export_txt(chapters)
    exporter.export_split_chapters(chapters)
    print(json.dumps({"markdown": str(md), "txt": str(txt)}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="novelgen")
    parser.add_argument("--config", default="configs/default.toml")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("init-project")
    p.add_argument("--name", required=True)
    p.add_argument("--description", default="")
    p.set_defaults(func=cmd_init_project)

    p = sub.add_parser("generate-concept")
    p.add_argument("--run-id", required=True)
    p.add_argument("--candidates", type=int, default=3)
    p.set_defaults(func=cmd_generate_concept)

    p = sub.add_parser("build-bible")
    p.add_argument("--run-id", required=True)
    p.add_argument("--concept-json", required=True)
    p.set_defaults(func=cmd_build_bible)

    p = sub.add_parser("build-outline")
    p.add_argument("--run-id", required=True)
    p.set_defaults(func=cmd_build_outline)

    p = sub.add_parser("generate-chapter")
    p.add_argument("--run-id", required=True)
    p.add_argument("--upto", type=int, default=1)
    p.set_defaults(func=cmd_generate_chapter)

    p = sub.add_parser("generate-novel")
    p.add_argument("--project-id", required=True)
    p.add_argument("--version", type=int, default=1)
    p.add_argument("--candidates", type=int, default=3)
    p.add_argument("--pick", type=int, default=1)
    p.add_argument("--upto-chapter", type=int, default=3)
    p.set_defaults(func=cmd_generate_novel)

    p = sub.add_parser("evaluate")
    p.add_argument("--run-id", required=True)
    p.set_defaults(func=cmd_evaluate)

    p = sub.add_parser("revise")
    p.add_argument("--run-id", required=True)
    p.set_defaults(func=cmd_revise)

    p = sub.add_parser("compare-runs")
    p.add_argument("--previous-run", required=True)
    p.add_argument("--current-run", required=True)
    p.set_defaults(func=cmd_compare_runs)

    p = sub.add_parser("apply-feedback")
    p.add_argument("--run-id", required=True)
    p.add_argument("--feedback", required=True)
    p.set_defaults(func=cmd_apply_feedback)

    p = sub.add_parser("export-manuscript")
    p.add_argument("--run-id", required=True)
    p.add_argument("--project-name", default="Untitled")
    p.set_defaults(func=cmd_export_manuscript)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
