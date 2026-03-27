from __future__ import annotations

from typing import Any, Dict

from enhancement.local_provider import LocalEnhancementProvider, TemplateRouteResult


_PROVIDER = LocalEnhancementProvider()


def identify_sequence(jd_title: str) -> str:
    """Return the 5-template route for a JD title."""
    return _PROVIDER.resolve_template_route(jd_title).template_id


def identify_sequence_with_meta(jd_title: str) -> TemplateRouteResult:
    """Return the selected template plus route evidence."""
    return _PROVIDER.resolve_template_route(jd_title)


def describe_route(jd_title: str) -> Dict[str, Any]:
    result = identify_sequence_with_meta(jd_title)
    return {
        "template_id": result.template_id,
        "score": result.score,
        "matched_terms": list(result.matched_terms),
        "excluded_by": list(result.excluded_by),
        "reasons": list(result.reasons),
    }
