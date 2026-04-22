from __future__ import annotations

from novel_auto_gen.core.models import EvaluationReport, RevisionInstruction, generate_id


class RevisionPlanner:
    def create_instruction(self, run_id: str, report: EvaluationReport) -> RevisionInstruction:
        directives = []
        for key in ["style_stability", "character_consistency", "foreshadow_payoff_consistency", "theme_penetration"]:
            item = report.dimensions.get(key)
            if item:
                directives.extend(item.suggestions)
        directives.extend(report.priorities_top3)
        return RevisionInstruction(
            instruction_id=generate_id("rev"),
            derived_from_run_id=run_id,
            derived_from_evaluation_id=generate_id("eval"),
            summary="評価結果から抽出した改稿指示",
            directives=list(dict.fromkeys(directives))[:10],
        )


class RunComparator:
    def compare_scores(self, previous: EvaluationReport, current: EvaluationReport) -> dict:
        delta = round(current.overall_score - previous.overall_score, 2)
        verdict = "improved" if delta > 0 else ("regressed" if delta < 0 else "unchanged")
        return {
            "previous": previous.overall_score,
            "current": current.overall_score,
            "delta": delta,
            "verdict": verdict,
        }
