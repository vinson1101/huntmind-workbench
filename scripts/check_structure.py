#!/usr/bin/env python3
"""Validate the huntmind-workbench repository structure."""

import sys
from pathlib import Path


def check_structure() -> int:
    project_root = Path(__file__).resolve().parent.parent

    print("Checking huntmind-workbench structure")
    print(f"Project root: {project_root}\n")

    required_dirs = [
        "configs",
        "docs",
        "core",
        "adapters",
        "pipelines",
        "runs",
        "outputs",
        "archive",
        "skills",
        "skills/talentflow",
        "enhancement",
    ]

    required_files = [
        "README.md",
        "requirements.txt",
        ".env.example",
        "configs/system_prompt.md",
        "configs/input.schema.json",
        "configs/output.schema.json",
        "docs/candidate_ingestion_spec.md",
        "core/__init__.py",
        "core/resume_ingest.py",
        "core/runner.py",
        "core/candidate_store.py",
        "core/batch_builder.py",
        "core/final_reporter.py",
        "adapters/__init__.py",
        "adapters/feishu_adapter.py",
        "adapters/local_adapter.py",
        "pipelines/__init__.py",
        "pipelines/process_feishu_folder.py",
        "pipelines/process_local_folder.py",
        "archive/feishu_folder_adapter.py",
        "archive/test_feishu_ingest.py",
        "skills/talentflow/SKILL.md",
        "enhancement/local_provider.py",
    ]

    missing_dirs = [path for path in required_dirs if not (project_root / path).is_dir()]
    missing_files = [path for path in required_files if not (project_root / path).is_file()]

    if not missing_dirs and not missing_files:
        print("Structure is complete.")
        return 0

    print("Structure is incomplete.")
    if missing_dirs:
        print("\nMissing directories:")
        for path in missing_dirs:
            print(f"- {path}")

    if missing_files:
        print("\nMissing files:")
        for path in missing_files:
            print(f"- {path}")

    return 1


if __name__ == "__main__":
    sys.exit(check_structure())
