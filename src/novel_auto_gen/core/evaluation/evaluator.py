from __future__ import annotations

from dataclasses import asdict
from statistics import mean

from novel_auto_gen.core.models import EvaluationReport, ScoreItem


REQUIRED_DIMENSIONS = [
    "story_consistency",
    "character_consistency",
    "causality_clarity",
    "foreshadow_payoff_consistency",
    "theme_penetration",
    "style_stability",
    "low_redundancy",
    "pacing",
    "chapter_hooks",
    "reader_engagement",
    "information_reveal_balance",
    "dialogue_naturalness",
    "scene_description_quality",
    "emotional_buildup",
    "overall",
]


class HeuristicEvaluator:
    def evaluate(self, chapter_texts: list[str]) -> EvaluationReport:
        dimensions: dict[str, ScoreItem] = {}
        for dim in REQUIRED_DIMENSIONS:
            base = 6.0
            length_bonus = min(2.0, sum(len(c) for c in chapter_texts) / 80000)
            score = round(min(10.0, base + length_bonus), 2)
            dimensions[dim] = ScoreItem(
                score=score,
                strengths=[f"{dim}に関して最低限の基準を満たしています。"],
                issues=[f"{dim}に関する深掘り改善余地があります。"],
                suggestions=[f"{dim}を改善するために章ごとの検査を追加してください。"],
            )

        priorities = [
            "章末の引きを強化する",
            "会話の冗長説明を削減する",
            "伏線と回収の対応表を章ごとに検証する",
        ]
        overall_score = round(mean([v.score for v in dimensions.values()]), 2)
        return EvaluationReport(overall_score=overall_score, dimensions=dimensions, priorities_top3=priorities)

    @staticmethod
    def to_markdown(report: EvaluationReport) -> str:
        lines = ["# Evaluation Report", "", f"- Overall: **{report.overall_score} / 10**", ""]
        for name, item in report.dimensions.items():
            lines.append(f"## {name}")
            lines.append(f"- score: {item.score}")
            lines.append(f"- 良い点: {'; '.join(item.strengths)}")
            lines.append(f"- 問題点: {'; '.join(item.issues)}")
            lines.append(f"- 改善提案: {'; '.join(item.suggestions)}")
            lines.append("")
        lines.append("## 次の改稿で優先すべき3点")
        for p in report.priorities_top3:
            lines.append(f"- {p}")
        return "\n".join(lines)

    @staticmethod
    def to_jsonable(report: EvaluationReport) -> dict:
        return asdict(report)
