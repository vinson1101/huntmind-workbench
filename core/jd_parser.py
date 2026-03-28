from __future__ import annotations

import re
from typing import Any, Dict, List


DEFAULT_JD_FIELDS = {
    "title": "",
    "must_have": [],
    "nice_to_have": [],
    "salary_range": "",
    "location": "",
    "company_context": "",
    "priority_focus": "",
    "base_location": "",
    "seniority_level": "",
    "reporting_line": "",
    "language_requirements": [],
    "eligibility_constraints": [],
    "travel_or_relocation": "",
    "industry_context": "",
    "domain_tags": [],
}

LOCATION_HINTS = [
    "北京",
    "上海",
    "深圳",
    "广州",
    "杭州",
    "宁波",
    "香港",
    "新加坡",
    "成都",
    "苏州",
    "南京",
]
LANGUAGE_HINTS = ["英语", "英文", "普通话", "粤语", "日语", "韩语"]
ELIGIBILITY_HINTS = ["签证", "身份", "工作资格", "合法工作", "IANG", "香港身份", "居留"]
DOMAIN_HINTS = ["区块链", "crypto", "web3", "交易所", "钱包", "ai", "saas", "金融", "电商", "医疗", "汽车"]
SENIORITY_HINTS = {
    "intern": ["实习"],
    "junior": ["专员", "助理", "初级", "junior"],
    "mid": ["经理", "主管", "mid"],
    "senior": ["高级", "资深", "总监", "senior"],
}


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _clean_str_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [_clean_text(item) for item in value if _clean_text(item)]
    text = _clean_text(value)
    if not text:
        return []
    return [part.strip() for part in re.split(r"[\n,;，；、]+", text) if part.strip()]


def _infer_salary_range(text: str) -> str:
    match = re.search(r"(\d{1,2}\s*[-~到至]\s*\d{1,2}\s*[kKwW万])", text)
    if match:
        return match.group(1).replace(" ", "")
    match = re.search(r"(\d{1,2}\s*[kKwW万])", text)
    return match.group(1).replace(" ", "") if match else ""


def _infer_location(text: str) -> str:
    for hint in LOCATION_HINTS:
        if hint in text:
            return hint
    return ""


def _infer_seniority(text: str) -> str:
    lowered = text.lower()
    for level, hints in SENIORITY_HINTS.items():
        if any(hint.lower() in lowered for hint in hints):
            return level
    return ""


def _infer_reporting_line(text: str) -> str:
    match = re.search(r"(汇报对象|汇报线|report to|reporting to)[:：]?\s*([^\n。；;]{1,40})", text, flags=re.IGNORECASE)
    if match:
        return _clean_text(match.group(2))
    return ""


def _infer_language_requirements(text: str) -> List[str]:
    lowered = text.lower()
    return [hint for hint in LANGUAGE_HINTS if hint.lower() in lowered]


def _infer_eligibility_constraints(text: str) -> List[str]:
    lowered = text.lower()
    return [hint for hint in ELIGIBILITY_HINTS if hint.lower() in lowered]


def _infer_travel_or_relocation(text: str) -> str:
    lowered = text.lower()
    for hint in ["可出差", "接受出差", "接受搬迁", "relocation", "travel", "onsite", "驻场"]:
        if hint.lower() in lowered:
            return hint
    return ""


def _infer_domain_tags(text: str) -> List[str]:
    lowered = text.lower()
    return [hint for hint in DOMAIN_HINTS if hint.lower() in lowered]


def normalize_jd_data(jd_data: Any) -> Dict[str, Any]:
    if isinstance(jd_data, str):
        jd_data = {"title": jd_data}
    if not isinstance(jd_data, dict):
        jd_data = {}

    normalized: Dict[str, Any] = dict(DEFAULT_JD_FIELDS)
    for key in ("title", "salary_range", "location", "company_context", "priority_focus"):
        normalized[key] = _clean_text(jd_data.get(key, ""))

    normalized["must_have"] = _clean_str_list(jd_data.get("must_have"))
    normalized["nice_to_have"] = _clean_str_list(jd_data.get("nice_to_have"))

    description_parts = [
        normalized["title"],
        _clean_text(jd_data.get("description", "")),
        _clean_text(jd_data.get("industry_context", "")),
        " ".join(normalized["must_have"]),
        " ".join(normalized["nice_to_have"]),
    ]
    merged_text = "\n".join(part for part in description_parts if part)

    normalized["base_location"] = _clean_text(jd_data.get("base_location")) or normalized["location"] or _infer_location(merged_text)
    normalized["salary_range"] = normalized["salary_range"] or _infer_salary_range(merged_text)
    normalized["seniority_level"] = _clean_text(jd_data.get("seniority_level")) or _infer_seniority(merged_text)
    normalized["reporting_line"] = _clean_text(jd_data.get("reporting_line")) or _infer_reporting_line(merged_text)
    normalized["language_requirements"] = _clean_str_list(jd_data.get("language_requirements")) or _infer_language_requirements(merged_text)
    normalized["eligibility_constraints"] = _clean_str_list(jd_data.get("eligibility_constraints")) or _infer_eligibility_constraints(merged_text)
    normalized["travel_or_relocation"] = _clean_text(jd_data.get("travel_or_relocation")) or _infer_travel_or_relocation(merged_text)
    normalized["industry_context"] = _clean_text(jd_data.get("industry_context"))
    normalized["domain_tags"] = _clean_str_list(jd_data.get("domain_tags")) or _infer_domain_tags(merged_text)

    return normalized
