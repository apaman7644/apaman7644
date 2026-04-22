from novel_auto_gen.core.config import load_config


def test_load_config():
    cfg = load_config("configs/default.toml")
    assert cfg.generation["target_chars"] == 100000
    assert cfg.paths["storage_root"]
