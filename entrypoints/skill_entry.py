from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, Optional

from pipelines.process_local_folder import process_local_folder
from core.runtime import RunMode


BatchEvaluator = Callable[[Dict[str, Any]], str]


def run_talentflow_skill(
    *,
    folder_path: str,
    jd_data: Dict[str, Any],
    evaluator: BatchEvaluator,
    file_types: Optional[list[str]] = None,
    run_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """产品主入口：必须由外部（如 HuntMind）注入 evaluator。"""
    return process_local_folder(
        folder_path=folder_path,
        jd_data=jd_data,
        file_types=file_types,
        run_dir=run_dir,
        evaluator=evaluator,
        run_mode=RunMode.EXTERNAL.value,
    )
