from __future__ import annotations

import json
from typing import Any, Dict

from pipelines.process_local_folder import process_local_folder


class HuntMindDecisionHandler:
    """Adapt HuntMind's recruiting decision capability to TalentFlow's decision_handler interface."""

    def __init__(self, huntmind_runtime: Any):
        self.huntmind_runtime = huntmind_runtime

    def __call__(self, batch_input: Dict[str, Any]) -> str:
        result = self.huntmind_runtime.evaluate_recruiting_batch(
            batch_input=batch_input,
            role="ai_hr",
            capability="recruiting_decision",
        )
        if isinstance(result, str):
            return result
        return json.dumps(result, ensure_ascii=False)


def run_talentflow_from_huntmind(
    *,
    huntmind_runtime: Any,
    folder_path: str,
    jd_data: Dict[str, Any],
):
    decision_handler = HuntMindDecisionHandler(huntmind_runtime)
    return process_local_folder(
        folder_path=folder_path,
        jd_data=jd_data,
        decision_handler=decision_handler,
        bot_name="huntmind",
    )


class FakeHuntMindRuntime:
    """Example contract only."""

    def evaluate_recruiting_batch(self, *, batch_input: Dict[str, Any], role: str, capability: str) -> Dict[str, Any]:
        raise NotImplementedError(
            "Implement evaluate_recruiting_batch in HuntMind and return JSON that TalentFlow runner can consume."
        )
