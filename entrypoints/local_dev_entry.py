from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from pipelines.process_local_folder import process_local_folder
from core.runtime import RunMode


def run_local_dev(
    *,
    folder_path: str,
    jd_data: Dict[str, object],
    file_types: Optional[list[str]] = None,
    run_dir: Optional[Path] = None,
):
    """开发入口：允许使用 TalentFlow 自带 fallback evaluator。"""
    return process_local_folder(
        folder_path=folder_path,
        jd_data=jd_data,
        file_types=file_types,
        run_dir=run_dir,
        evaluator=None,
        run_mode=RunMode.LOCAL_DEV.value,
    )
