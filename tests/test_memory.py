from novel_auto_gen.core.memory.context_manager import ContextManager


def test_memory_context_recent_chapters():
    cm = ContextManager()
    cm.update_from_chapter(1, "s1", ["f1"], ["u1"])
    cm.update_from_chapter(2, "s2", ["f2"], ["u2"])
    ctx = cm.build_chapter_context(3)
    assert 1 in ctx["recent_chapter_summaries"]
    assert 2 in ctx["recent_chapter_summaries"]
