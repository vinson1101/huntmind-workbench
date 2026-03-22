from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RunMode(str, Enum):
    """TalentFlow 运行模式。"""

    EXTERNAL = "external"
    LOCAL_DEV = "local_dev"
    TEST = "test"
    EMERGENCY_DEBUG = "emergency_debug"


@dataclass(frozen=True)
class RuntimeContext:
    """运行时决策归属信息，用于写入 run_meta。"""

    run_mode: str
    decision_owner: str
    evaluator_source: str
    model_identity: str | None = None

    @property
    def fallback_allowed(self) -> bool:
        return self.run_mode in {
            RunMode.LOCAL_DEV.value,
            RunMode.TEST.value,
            RunMode.EMERGENCY_DEBUG.value,
        }
