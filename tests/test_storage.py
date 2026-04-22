from novel_auto_gen.core.storage.repository import JsonRepository


def test_storage_read_write(tmp_path):
    repo = JsonRepository(tmp_path)
    repo.write_json("a/b.json", {"x": 1})
    data = repo.read_json("a/b.json")
    assert data["x"] == 1
