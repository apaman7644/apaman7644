from novel_auto_gen.core.config import load_config
from novel_auto_gen.core.pipeline.engine import PipelineEngine
from novel_auto_gen.core.prompts.manager import PromptManager
from novel_auto_gen.core.providers.mock_provider import MockProvider
from novel_auto_gen.core.providers.service import ProviderService
from novel_auto_gen.core.storage.repository import JsonRepository


def test_chapter_pipeline(tmp_path):
    cfg = load_config("configs/default.toml")
    cfg.raw["paths"]["storage_root"] = str(tmp_path)
    engine = PipelineEngine(cfg, ProviderService(MockProvider()), PromptManager("prompts"), JsonRepository(tmp_path))
    p = engine.init_project("p", "d")
    run = engine.start_run(p["project_id"])
    concept = engine.generate_concepts(run.run_id, 1)[0]
    bible = engine.build_bible(run.run_id, concept)
    outline = engine.build_outline(run.run_id, bible)
    chapters = engine.generate_chapters(run.run_id, bible, outline, upto=2)
    assert len(chapters) == 2
