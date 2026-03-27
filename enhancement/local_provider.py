from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class TemplateRouteResult:
    template_id: str
    score: int
    matched_terms: List[str]
    excluded_by: List[str]
    reasons: List[str]


class EnhancementProvider(ABC):
    @abstractmethod
    def get_taxonomy_mapping(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_template_rules(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_decision_hints(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def resolve_template_route(self, jd_title: str) -> TemplateRouteResult:
        raise NotImplementedError


class LocalEnhancementProvider(EnhancementProvider):
    """Temporary local stub for the future paid enhancement layer."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root or PROJECT_ROOT)

    def get_taxonomy_mapping(self) -> Dict[str, Any]:
        with open(self.project_root / "data" / "sequence_lookup.json", "r", encoding="utf-8") as handle:
            return json.load(handle)

    def get_template_rules(self) -> Dict[str, Any]:
        with open(self.project_root / "configs" / "scoring_templates.yaml", "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def get_decision_hints(self) -> Dict[str, Any]:
        with open(self.project_root / "configs" / "decision_hints.yaml", "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def resolve_template_route(self, jd_title: str) -> TemplateRouteResult:
        templates_cfg = self.get_template_rules()
        templates = templates_cfg.get("templates", {})
        default_template = templates_cfg.get("default_template", "product_manager")
        direct_terms = templates_cfg.get("routing", {}).get("direct_terms", {})
        taxonomy_cfg = self.get_taxonomy_mapping()
        l3_to_template = taxonomy_cfg.get("l3_to_template", {})
        l4_to_l3 = taxonomy_cfg.get("l4_to_l3", {})

        normalized_title = (jd_title or "").strip().lower()
        if not normalized_title:
            return TemplateRouteResult(default_template, 0, [], [], ["empty_jd_title"])

        template_scores: Dict[str, int] = {template_id: 0 for template_id in templates}
        matched_terms: Dict[str, List[str]] = {template_id: [] for template_id in templates}
        excluded_terms: Dict[str, List[str]] = {template_id: [] for template_id in templates}
        reasons: Dict[str, List[str]] = {template_id: [] for template_id in templates}

        for template_id, terms in direct_terms.items():
            for term in terms or []:
                if term and term.lower() in normalized_title:
                    template_scores[template_id] = template_scores.get(template_id, 0) + 8
                    matched_terms[template_id].append(term)
                    reasons[template_id].append(f"direct:{term}")

        for term, l3 in sorted(l4_to_l3.items(), key=lambda item: len(item[0]), reverse=True):
            normalized_term = str(term or "").strip().lower()
            template_id = l3_to_template.get(l3)
            if not normalized_term or not template_id or template_id not in template_scores:
                continue
            if normalized_term in normalized_title:
                template_scores[template_id] += 4
                matched_terms[template_id].append(term)
                reasons[template_id].append(f"taxonomy:{term}")

        for template_id, template_cfg in templates.items():
            routing = template_cfg.get("routing", {})
            for term in routing.get("strong_signals", []) or []:
                if term and term.lower() in normalized_title:
                    template_scores[template_id] += 3
                    matched_terms[template_id].append(term)
                    reasons[template_id].append(f"strong:{term}")
            for term in routing.get("weak_signals", []) or []:
                if term and term.lower() in normalized_title:
                    template_scores[template_id] += 1
                    matched_terms[template_id].append(term)
                    reasons[template_id].append(f"weak:{term}")
            for term in routing.get("exclude_signals", []) or []:
                if term and term.lower() in normalized_title:
                    template_scores[template_id] -= 6
                    excluded_terms[template_id].append(term)
                    reasons[template_id].append(f"exclude:{term}")

        ranked_templates = sorted(
            template_scores.items(),
            key=lambda item: (item[1], len(matched_terms.get(item[0], []))),
            reverse=True,
        )
        selected_template, selected_score = ranked_templates[0] if ranked_templates else (default_template, 0)
        if selected_score <= 0:
            selected_template = default_template

        return TemplateRouteResult(
            template_id=selected_template,
            score=template_scores.get(selected_template, 0),
            matched_terms=matched_terms.get(selected_template, []),
            excluded_by=excluded_terms.get(selected_template, []),
            reasons=reasons.get(selected_template, []),
        )


class RemoteEnhancementProvider(EnhancementProvider):
    def get_taxonomy_mapping(self) -> Dict[str, Any]:
        raise NotImplementedError("Remote provider is reserved for the future paid enhancement layer.")

    def get_template_rules(self) -> Dict[str, Any]:
        raise NotImplementedError("Remote provider is reserved for the future paid enhancement layer.")

    def get_decision_hints(self) -> Dict[str, Any]:
        raise NotImplementedError("Remote provider is reserved for the future paid enhancement layer.")

    def resolve_template_route(self, jd_title: str) -> TemplateRouteResult:
        raise NotImplementedError("Remote provider is reserved for the future paid enhancement layer.")
