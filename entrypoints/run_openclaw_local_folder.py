"""
用 OpenClaw / HuntMind 的配置注入 evaluator，运行 TalentFlow 本地简历处理。

适用场景：
- 你当前就在做真实简历、真实模型、近生产环境测试
- API 身份和模型配置已经放在 openclaw.json 里
- 不希望再额外用环境变量重复配置 API key

这个入口的语义是：
- 仍然走 TalentFlow 流水线
- 但 evaluator 以“外部注入”的方式进入
- 配置来源使用 OpenClaw / HuntMind 的 openclaw.json
- 因此运行模式为 external，而不是 local_dev fallback
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.evaluator import load_evaluator_config
from pipelines.process_local_folder import process_local_folder


class OpenClawInjectedEvaluator:
    def __init__(
        self,
        *,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        response_format: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        system_prompt_path: Optional[Path] = None,
        timeout: Optional[int] = None,
    ):
        self.config = load_evaluator_config(
            model=model,
            temperature=temperature,
            response_format=response_format,
            base_url=base_url,
            api_key=api_key,
            system_prompt_path=system_prompt_path,
            timeout=timeout,
        )

    def __call__(self, batch_input: Dict[str, Any]) -> str:
        system_prompt = self.config.system_prompt_path.read_text(encoding="utf-8")
        payload: Dict[str, Any] = {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(batch_input, ensure_ascii=False)},
            ],
        }

        if self.config.response_format == "json_object":
            payload["response_format"] = {"type": "json_object"}
        else:
            payload["response_format"] = {"type": self.config.response_format}

        response = requests.post(
            f"{self.config.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.config.timeout,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(f"OpenClaw evaluator request failed: {response.status_code} {response.text[:500]}") from exc

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            raise RuntimeError(
                f"OpenClaw evaluator response missing choices/message/content: {json.dumps(data, ensure_ascii=False)[:1000]}"
            ) from exc


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="用 OpenClaw / HuntMind 配置注入 evaluator 跑本地简历处理")
    parser.add_argument("folder_path", help="本地简历目录")
    parser.add_argument("--jd", required=True, help="职位描述 JSON 文件路径")
    parser.add_argument("--types", nargs="+", default=["pdf", "docx", "txt", "md"], help="文件类型")
    parser.add_argument("--run-dir", help="运行目录（可选）")
    parser.add_argument("--model", help="覆盖 openclaw.json 中的 model")
    parser.add_argument("--base-url", help="覆盖 openclaw.json 中的 base_url")
    parser.add_argument("--temperature", type=float, help="覆盖 openclaw.json 中的 temperature")
    parser.add_argument("--system-prompt", help="覆盖 system_prompt_path")
    parser.add_argument("--timeout", type=int, help="覆盖 timeout")

    args = parser.parse_args()

    with open(Path(args.jd), "r", encoding="utf-8") as f:
        jd_data = json.load(f)

    evaluator = OpenClawInjectedEvaluator(
        model=args.model,
        base_url=args.base_url,
        temperature=args.temperature,
        system_prompt_path=Path(args.system_prompt) if args.system_prompt else None,
        timeout=args.timeout,
    )

    result = process_local_folder(
        folder_path=args.folder_path,
        jd_data=jd_data,
        file_types=args.types,
        run_dir=Path(args.run_dir) if args.run_dir else None,
        evaluator=evaluator,
        run_mode="external",
    )

    print(
        json.dumps(
            {
                "run_dir": result["run_dir"],
                "scan_total": result["scan_result"]["total_files"],
                "ingest_stats": result["ingest_result"]["stats"],
                "batch_input_path": result["batch_input_path"],
                "run_meta_path": result["run_meta_path"],
                "candidate_paths": result["candidate_paths"],
                "final_output_path": result["final_output_path"],
                "final_report_path": result["final_report_path"],
                "quality_meta_path": result["quality_meta_path"],
                "owner_summary_path": result["owner_summary_path"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
