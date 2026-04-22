from novel_auto_gen.core.evaluation.evaluator import HeuristicEvaluator, REQUIRED_DIMENSIONS


def test_evaluation_dimensions():
    report = HeuristicEvaluator().evaluate(["テスト本文"])
    assert set(REQUIRED_DIMENSIONS) == set(report.dimensions.keys())
    assert len(report.priorities_top3) == 3
