from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_asset_content(path: Path, asset_type: str) -> Any:
    if asset_type == "json":
        return _load_json(path)
    if asset_type == "yaml":
        with open(path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    return _load_text(path)


def _load_asset_group(index_path: Path) -> Dict[str, Any]:
    manifest = _load_json(index_path)
    assets_payload: List[Dict[str, Any]] = []
    for asset in manifest.get("assets", []):
        relative_path = asset.get("path", "")
        resolved_path = PROJECT_ROOT / relative_path
        assets_payload.append(
            {
                "id": asset.get("id", ""),
                "type": asset.get("type", "text"),
                "path": relative_path,
                "resolved_path": str(resolved_path),
                "description": asset.get("description", ""),
                "content": _load_asset_content(resolved_path, asset.get("type", "text")),
            }
        )
    return {
        "pack_role": manifest.get("pack_role", ""),
        "description": manifest.get("description", ""),
        "assets": assets_payload,
    }


def load_context_payload(
    *,
    project_root: Path | None = None,
    tenant_profile_path: Path | None = None,
) -> Dict[str, Any]:
    root = Path(project_root or PROJECT_ROOT)
    guidance_root = root / "guidance"
    tenant_path = tenant_profile_path or root / "tenant" / "tenant_preference_profile.json"

    taxonomy_assets = _load_asset_group(guidance_root / "taxonomy_assets" / "index.json")
    template_assets = _load_asset_group(guidance_root / "template_assets" / "index.json")

    core_rule_pack_path = guidance_root / "core_rule_pack.json"
    core_rule_pack = _load_json(core_rule_pack_path)
    loaded_core_assets: List[Dict[str, Any]] = []
    for asset in core_rule_pack.get("assets", []):
        relative_path = asset.get("path", "")
        resolved_path = root / relative_path
        loaded_core_assets.append(
            {
                "id": asset.get("id", ""),
                "type": asset.get("type", "text"),
                "path": relative_path,
                "resolved_path": str(resolved_path),
                "description": asset.get("description", ""),
                "content": _load_asset_content(resolved_path, asset.get("type", "text")),
            }
        )

    tenant_preference_profile: Dict[str, Any] = {}
    if Path(tenant_path).exists():
        tenant_preference_profile = _load_json(Path(tenant_path))

    return {
        "service_layer_access": {
            "mode": "local_embedded",
            "future_remote_supported": True,
            "api_key_env": "SERVICE_LAYER_API_KEY",
            "remote_base_url_env": "SERVICE_LAYER_BASE_URL",
            "configured_api_key": bool(os.getenv("SERVICE_LAYER_API_KEY")),
            "note": "Enhancement-only access layer. Not a blocking interception layer.",
        },
        "service_experience_pack": {
            "taxonomy_assets": taxonomy_assets,
            "template_assets": template_assets,
            "core_rule_pack": {
                "pack_role": core_rule_pack.get("pack_role", ""),
                "description": core_rule_pack.get("description", ""),
                "hard_guardrails": core_rule_pack.get("hard_guardrails", []),
                "assets": loaded_core_assets,
            },
        },
        "tenant_preference_profile": tenant_preference_profile,
    }
