from __future__ import annotations

from typing import Any, Dict, List

from .utils import (
    normalize_candidate_output,
    normalize_human_label,
    reason_bucket_from_output,
)


def _priority_rank(value: str) -> int:
    return {"A": 0, "B": 1, "C": 2, "N": 3}.get(value, 9)


def _main_gap(human: Dict[str, Any], model: Dict[str, Any], model_reason: str) -> str:
    if human["should_contact"] != model["should_contact"]:
        return "should_contact_gap"
    if human["priority"] != model["priority"]:
        return "priority_gap"
    if human["decision"] != model["decision"]:
        return "decision_gap"
    if human["match_fit"] != model["match_fit"]:
        return "match_fit_gap"
    if human["recruitability"] != model["recruitability"]:
        return "recruitability_gap"
    if human["mismatch_type"] != model["mismatch_type"]:
        return "mismatch_type_gap"
    if human["primary_reason"] != model_reason:
        return "reason_bucket_gap"
    return ""


def compare_batch(
    human_labels: List[Dict[str, Any]],
    final_output: Dict[str, Any],
    expected_summary: Dict[str, Any],
    routing_error_count: int,
) -> Dict[str, Any]:
    normalized_humans = [normalize_human_label(item) for item in human_labels]
    model_candidates = final_output.get("top_recommendations", [])
    model_lookup = {
        normalize_candidate_output(candidate)["candidate_id"]: candidate
        for candidate in model_candidates
    }

    candidate_results: List[Dict[str, Any]] = []
    contact_matches = 0
    priority_matches = 0
    decision_matches = 0
    reason_matches = 0
    false_positive = 0
    false_negative = 0
    hard_mismatch_false_positive = 0
    low_fit_high_willingness_promoted = 0
    new_high_priority_false_positive = 0

    for human in normalized_humans:
        raw_model_candidate = model_lookup.get(human["candidate_id"], {})
        model = normalize_candidate_output(raw_model_candidate)
        model_reason = reason_bucket_from_output(raw_model_candidate)

        is_contact_match = human["should_contact"] == model["should_contact"]
        is_priority_match = human["priority"] == model["priority"]
        is_decision_match = human["decision"] == model["decision"]
        is_reason_match = human["primary_reason"] == model_reason

        if is_contact_match:
            contact_matches += 1
        if is_priority_match:
            priority_matches += 1
        if is_decision_match:
            decision_matches += 1
        if is_reason_match:
            reason_matches += 1

        if not human["should_contact"] and model["should_contact"]:
            false_positive += 1
        if human["should_contact"] and not model["should_contact"]:
            false_negative += 1
        if human["mismatch_type"] == "hard_mismatch" and model["should_contact"]:
            hard_mismatch_false_positive += 1
        if human["match_fit"] == "low" and model["willingness"] == "high" and model["decision"] in {"yes", "strong_yes"}:
            low_fit_high_willingness_promoted += 1
        if not human["should_contact"] and model["priority"] in {"A", "B"}:
            new_high_priority_false_positive += 1

        candidate_results.append(
            {
                "candidate_id": human["candidate_id"],
                "human_should_contact": human["should_contact"],
                "model_should_contact": model["should_contact"],
                "human_priority": human["priority"],
                "model_priority": model["priority"],
                "human_decision": human["decision"],
                "model_decision": model["decision"],
                "human_match_fit": human["match_fit"],
                "model_match_fit": model["match_fit"],
                "human_recruitability": human["recruitability"],
                "model_recruitability": model["recruitability"],
                "human_mismatch_type": human["mismatch_type"],
                "model_mismatch_type": model["mismatch_type"],
                "human_primary_reason": human["primary_reason"],
                "model_primary_reason": model_reason,
                "is_contact_match": is_contact_match,
                "is_priority_match": is_priority_match,
                "is_decision_match": is_decision_match,
                "is_reason_match": is_reason_match,
                "main_gap": _main_gap(human, model, model_reason),
            }
        )

    total = len(normalized_humans) or 1
    human_contact_ranked = sorted(
        [item for item in normalized_humans if item["should_contact"]],
        key=lambda item: (_priority_rank(item["priority"]), item["candidate_id"]),
    )
    human_top_ids = [item["candidate_id"] for item in human_contact_ranked][:3]
    model_sorted = sorted(
        [normalize_candidate_output(item) for item in model_candidates],
        key=lambda item: (_priority_rank(item["priority"]), item["candidate_id"]),
    )
    model_top_ids = [item["candidate_id"] for item in model_sorted if item["should_contact"]][:3]
    top3_hit_count = len(set(human_top_ids) & set(model_top_ids))
    top3_base = len(human_top_ids)

    metrics = {
        "contact_accuracy": round(contact_matches / total, 4),
        "priority_accuracy": round(priority_matches / total, 4),
        "decision_accuracy": round(decision_matches / total, 4),
        "top3_hit_rate": round(top3_hit_count / top3_base, 4) if top3_base else 0.0,
        "false_positive_rate": round(false_positive / total, 4),
        "false_negative_rate": round(false_negative / total, 4),
        "reason_accuracy": round(reason_matches / total, 4),
        "routing_error_count": int(routing_error_count),
    }

    hard_errors = {
        "hard_mismatch_false_positive": hard_mismatch_false_positive,
        "low_fit_high_willingness_promoted": low_fit_high_willingness_promoted,
        "routing_error_count": int(routing_error_count),
        "new_high_priority_false_positive": new_high_priority_false_positive,
    }

    return {
        "candidate_results": candidate_results,
        "counts": {
            "total_candidates": len(human_labels),
            "contact_matches": contact_matches,
            "priority_matches": priority_matches,
            "decision_matches": decision_matches,
            "reason_matches": reason_matches,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "top3_hit_count": top3_hit_count,
            "top3_base": top3_base,
        },
        "metrics": metrics,
        "hard_errors": hard_errors,
        "top3": {
            "human_top_ids": human_top_ids,
            "model_top_ids": model_top_ids,
            "hit_count": top3_hit_count,
        },
    }
