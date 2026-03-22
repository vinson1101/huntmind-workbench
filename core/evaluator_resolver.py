from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from core import evaluator as fallback_evaluator
from core.runtime import RunMode, RuntimeContext


BatchEvaluator = Callable[[Dict[str, Any]], str]


class MissingEvaluatorError(RuntimeError):
    """产品主路径缺少外部 evaluator 时抛出。"""


@dataclass(frozen=True)
class ResolvedEvaluator:
    evaluator: BatchEvaluator
    runtime_context: RuntimeContext


def resolve_batch_evaluator(
    evaluator: Optional[BatchEvaluator],
    *,
    run_mode: str,
) -> ResolvedEvaluator:
    normalized_mode = _normalize_run_mode(run_mode)

    if evaluator is not None:
        return ResolvedEvaluator(
            evaluator=evaluator,
            runtime_context=RuntimeContext(
                run_mode=normalized_mode,
                decision_owner="huntmind",
                evaluator_source="injected",
                model_identity="huntmind",
            ),
        )

    if normalized_mode in {
        RunMode.LOCAL_DEV.value,
        RunMode.TEST.value,
        RunMode.EMERGENCY_DEBUG.value,
    }:
        return ResolvedEvaluator(
            evaluator=fallback_evaluator.evaluate_batch,
            runtime_context=RuntimeContext(
                run_mode=normalized_mode,
                decision_owner="talentflow_fallback",
                evaluator_source="fallback_llm",
                model_identity="talentflow_fallback_llm",
            ),
        )

    raise MissingEvaluatorError(
        "run_mode=external 时必须显式注入 evaluator；"
        "TalentFlow 在产品主路径下不允许默认 fallback 到本地 LLM evaluator。"
    )


def _normalize_run_mode(run_mode: str) -> str:
    if not run_mode:
        return RunMode.EXTERNAL.value

    try:
        return RunMode(run_mode).value
    except ValueError as exc:
        allowed = ", ".join(mode.value for mode in RunMode)
        raise ValueError(f"Invalid run_mode '{run_mode}'. Allowed values: {allowed}") from exc
