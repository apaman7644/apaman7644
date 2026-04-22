from novel_auto_gen.core.models import EvaluationReport, ScoreItem
from novel_auto_gen.core.revision.reviser import RunComparator


def test_compare_runs_improved():
    a = EvaluationReport(overall_score=6.0, dimensions={"overall": ScoreItem(6, [], [], [])}, priorities_top3=["a", "b", "c"])
    b = EvaluationReport(overall_score=7.0, dimensions={"overall": ScoreItem(7, [], [], [])}, priorities_top3=["a", "b", "c"])
    diff = RunComparator().compare_scores(a, b)
    assert diff["verdict"] == "improved"
