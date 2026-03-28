from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.runner import run as run_output_processing


def _build_model_output(candidate_id: str, template_id: str, decision: str, priority: str = "A") -> str:
    payload = {
        "overall_diagnosis": "regression",
        "batch_advice": "regression",
        "top_recommendations": [
            {
                "candidate_id": candidate_id,
                "rank": 1,
                "total_score": 85,
                "decision": decision,
                "priority": priority,
                "action_timing": "today",
                "core_judgement": "regression candidate",
                "reasons": ["reason 1", "reason 2", "reason 3"],
                "risks": ["risk 1"],
                "score_breakdown": {
                    "hard_skill": 80,
                    "experience": 80,
                    "stability": 80,
                    "potential": 80,
                    "conversion": 80,
                },
                "structured_score": {
                    "template_id": template_id,
                    "dimension_scores": {
                        "hard_skill_match": 80,
                        "experience_depth": 80,
                        "innovation_potential": 75,
                        "execution_goal_breakdown": 80,
                        "team_fit": 75,
                        "willingness": 95,
                        "stability": 70,
                    },
                    "weight_snapshot": {},
                    "dimension_evidence": {},
                },
                "action": {
                    "should_contact": True,
                    "hook_message": "hook",
                    "verification_question": "question",
                    "message_template": "template",
                    "deep_questions": ["q1", "q2", "q3"],
                },
            }
        ],
    }
    return json.dumps(payload, ensure_ascii=False)


def _run_case(name: str, batch_input: dict, output_text: str, expected: dict) -> None:
    result = run_output_processing(batch_input, output_text)
    candidate = result["json"]["top_recommendations"][0]

    for key, expected_value in expected.items():
        actual = candidate
        for part in key.split("."):
            actual = actual[part]
        assert actual == expected_value, f"{name}: expected {key}={expected_value!r}, got {actual!r}"

    print(f"[ok] {name}")


def main() -> None:
    hard_mismatch_input = {
        "jd": {
            "title": "高级产品经理",
            "must_have": ["PRD", "需求分析"],
            "nice_to_have": ["数据分析"],
            "salary_range": "25-35K",
            "base_location": "杭州",
            "seniority_level": "senior",
        },
        "candidates": [
            {
                "candidate_id": "case_hard",
                "raw_resume": "5年销售管理，渠道合作，KA 销售，华南区域拓展",
                "location": "深圳",
                "expected_salary": "30K",
            }
        ],
    }
    _run_case(
        "hard_mismatch_forces_no",
        hard_mismatch_input,
        _build_model_output("case_hard", "sales_director", "strong_yes", "A"),
        {
            "mismatch_type": "hard_mismatch",
            "decision": "no",
            "priority": "N",
            "recruitability_breakdown.location_feasibility.level": "low",
        },
    )

    salary_mismatch_input = {
        "jd": {
            "title": "高级产品经理",
            "must_have": ["产品规划", "需求分析"],
            "nice_to_have": ["增长"],
            "salary_range": "20-30K",
            "base_location": "杭州",
            "seniority_level": "senior",
        },
        "candidates": [
            {
                "candidate_id": "case_salary",
                "raw_resume": "高级产品经理，负责产品规划、需求分析、增长策略，senior product manager",
                "location": "杭州",
                "expected_salary": "60K",
            }
        ],
    }
    _run_case(
        "salary_mismatch_lowers_recruitability",
        salary_mismatch_input,
        _build_model_output("case_salary", "product_manager", "strong_yes", "A"),
        {
            "match_fit": "strong",
            "recruitability": "low",
            "recruitability_breakdown.compensation_feasibility.level": "low",
            "decision": "maybe",
        },
    )

    strong_yes_input = {
        "jd": {
            "title": "高级产品经理",
            "must_have": ["产品规划", "需求分析"],
            "nice_to_have": ["增长"],
            "salary_range": "30-40K",
            "base_location": "杭州",
            "seniority_level": "senior",
            "language_requirements": ["英语"],
        },
        "candidates": [
            {
                "candidate_id": "case_yes",
                "raw_resume": "高级产品经理，负责产品规划、需求分析、增长策略，英语流利，senior product manager",
                "location": "杭州",
                "expected_salary": "35K",
            }
        ],
    }
    _run_case(
        "strong_fit_and_constraints_keep_positive_decision",
        strong_yes_input,
        _build_model_output("case_yes", "product_manager", "yes", "B"),
        {
            "match_fit": "strong",
            "recruitability": "high",
            "recruitability_breakdown.location_feasibility.level": "high",
            "decision": "strong_yes",
        },
    )


if __name__ == "__main__":
    main()
