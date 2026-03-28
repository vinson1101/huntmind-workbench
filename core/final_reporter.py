from __future__ import annotations

import ast
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

FEISHU_TABLE_URL = "https://ucn43sn4odey.feishu.cn/base/AINFbZLOQaSo6rslOeZc95RTnPb"


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _try_parse_dict_like(value: Any) -> Optional[Dict[str, Any]]:
    if isinstance(value, dict):
        return value

    text = _clean_text(value)
    if not text:
        return None

    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(text)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            continue
    return None


def _normalize_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [_clean_text(item) for item in value if _clean_text(item)]


class FinalReporter:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_final_report(
        self,
        candidates: List[Dict[str, Any]],
        meta: Dict[str, Any],
        filename: Optional[str] = None,
    ) -> Path:
        report_content = self._build_report_content(candidates, meta)
        report_name = filename or f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = self.output_dir / report_name
        report_path.write_text(report_content, encoding="utf-8")
        return report_path

    def save_owner_summary(
        self,
        candidates: List[Dict[str, Any]],
        jd_title: str = "待确认",
        jd_location: str = "待确认",
        jd_salary: str = "待确认",
        filename: str = "owner_summary.md",
    ) -> Path:
        summary = self.generate_owner_summary(
            candidates,
            jd_title=jd_title or "待确认",
            jd_location=jd_location or "待确认",
            jd_salary=jd_salary or "待确认",
        )
        summary_path = self.output_dir / filename
        summary_path.write_text(summary, encoding="utf-8")
        return summary_path

    def generate_owner_summary(
        self,
        candidates: List[Dict[str, Any]],
        jd_title: str = "待确认",
        jd_location: str = "待确认",
        jd_salary: str = "待确认",
    ) -> str:
        stats = self._load_summary_stats(candidates)
        a_candidates = [c for c in candidates if c.get("priority") == "A" and c.get("decision") in {"strong_yes", "yes"}]
        b_candidates = [c for c in candidates if c.get("priority") == "B" and c.get("decision") in {"strong_yes", "yes"}]
        c_candidates = [c for c in candidates if c.get("decision") == "maybe"]
        no_candidates = [c for c in candidates if c.get("decision") == "no"]
        today_candidates = [c for c in candidates if c.get("action_timing") == "today"]
        this_week_candidates = [c for c in candidates if c.get("action_timing") == "this_week"]

        def _fmt(candidate: Dict[str, Any]) -> str:
            score = round(float(candidate.get("total_score") or 0), 1)
            return f"{self._display_name(candidate)}({score})"

        def _fmt_list(items: List[Dict[str, Any]]) -> str:
            return " / ".join(_fmt(item) for item in items) if items else "-"

        lines = [
            f"【招聘决策报告】{jd_title} · {jd_location} · {jd_salary}",
            "",
            f"本批次共处理 {stats['total_processed']} 份简历。",
            "",
            "| 档位 | 人数 | 候选人 |",
            "|---|---:|---|",
            f"| A / strong_yes | {len(a_candidates)} | {_fmt_list(a_candidates)} |",
            f"| B / yes | {len(b_candidates)} | {_fmt_list(b_candidates)} |",
            f"| C / maybe | {len(c_candidates)} | {_fmt_list(c_candidates)} |",
            f"| N / no | {len(no_candidates)} | {_fmt_list(no_candidates)} |",
            "",
            "**今日优先联系**",
        ]

        if today_candidates:
            for candidate in today_candidates:
                lines.append(f"- {self._display_name(candidate)}: {self._summary_judgement(candidate)}")
        else:
            lines.append("- -")

        lines.extend(["", "**本周建议联系**"])
        if this_week_candidates:
            for candidate in this_week_candidates:
                lines.append(f"- {self._display_name(candidate)}: {self._summary_judgement(candidate)}")
        else:
            lines.append("- -")

        lines.extend(["", "**结论**"])
        if a_candidates or b_candidates:
            lines.append(f"- 建议优先推进 {len(a_candidates) + len(b_candidates)} 位 strong_yes/yes 候选人。")
        elif c_candidates:
            lines.append(f"- 当前无可直接推进人选，保留 {len(c_candidates)} 位 maybe 候选人待进一步核验。")
        else:
            lines.append("- 当前批次建议继续搜索。")

        lines.extend(
            [
                "",
                f"**run_id** {self.output_dir.name}",
                f"**生成时间** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"**飞书表格** {FEISHU_TABLE_URL}",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"

    def _build_report_content(self, candidates: List[Dict[str, Any]], meta: Dict[str, Any]) -> str:
        stats = self._load_summary_stats(candidates)
        lines = [
            "# 招聘决策报告",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        lines.extend(self._format_jd_section(meta.get("jd")))

        if meta.get("company"):
            lines.extend(self._format_company_section(meta.get("company")))

        lines.extend(
            [
                "## 整体诊断",
                "",
                self._build_overall_diagnosis(meta, candidates, stats),
                "",
                "## 批量建议",
                "",
                self._build_batch_advice(meta, candidates),
                "",
                "## 候选人汇总",
                "",
                f"- 总处理数: {stats['total_processed']}",
                f"- 值得联系: {sum(1 for c in candidates if c.get('decision') in {'strong_yes', 'yes'})}",
                f"- 备选观察: {sum(1 for c in candidates if c.get('decision') == 'maybe')}",
                "",
                "---",
                "",
                "## 详细评估",
                "",
            ]
        )

        for index, candidate in enumerate(candidates, 1):
            lines.extend(self._build_candidate_section(candidate, index))
            lines.extend(["---", ""])

        return "\n".join(lines).rstrip() + "\n"

    def _build_candidate_section(self, candidate: Dict[str, Any], idx: int) -> List[str]:
        lines: List[str] = []
        display_name = self._display_name(candidate)
        role_label = self._role_label(candidate)
        heading = display_name if not role_label else f"{display_name} · {role_label}"

        lines.extend(
            [
                f"### {idx}. {heading}",
                "",
                f"- **决策**: {self._decision_label(candidate.get('decision'))}",
                f"- **总分**: {int(float(candidate.get('total_score', 0) or 0))}/100",
                f"- **优先级**: {candidate.get('priority', '-')}",
                f"- **联系时机**: {self._timing_label(candidate.get('action_timing'))}",
            ]
        )

        match_fit = _clean_text(candidate.get("match_fit"))
        recruitability = _clean_text(candidate.get("recruitability"))
        mismatch_type = _clean_text(candidate.get("mismatch_type"))
        if match_fit:
            lines.append(f"- **Match Fit**: {match_fit}")
        if recruitability:
            lines.append(f"- **Recruitability**: {recruitability}")
        if mismatch_type:
            lines.append(f"- **Mismatch Type**: {mismatch_type}")

        if _clean_text(candidate.get("match_fit_reason")):
            lines.append(f"- **Match Reason**: {_clean_text(candidate.get('match_fit_reason'))}")

        recruitability_breakdown = candidate.get("recruitability_breakdown", {})
        if isinstance(recruitability_breakdown, dict) and recruitability_breakdown:
            lines.extend(["", "**Recruitability Breakdown**:"])
            for key in (
                "compensation_feasibility",
                "location_feasibility",
                "seniority_fit",
                "eligibility_constraint",
            ):
                item = recruitability_breakdown.get(key, {})
                if not isinstance(item, dict):
                    continue
                level = _clean_text(item.get("level"))
                reason = _clean_text(item.get("reason"))
                if level or reason:
                    text = f"- {key}: {level}" if level else f"- {key}"
                    if reason:
                        text += f" | {reason}"
                    lines.append(text)

        override_trace = candidate.get("override_trace") or []
        if isinstance(override_trace, list) and override_trace:
            lines.extend(["", "**Runner Override Trace**:"])
            for trace in override_trace[:3]:
                text = _clean_text(trace)
                if text:
                    lines.append(f"- {text}")

        lines.extend(["", "**核心判断**:", f"- {self._summary_judgement(candidate)}"])

        reasons = _normalize_list(candidate.get("reasons"))
        if reasons:
            lines.extend(["", "**评估理由**:"])
            for reason in reasons[:3]:
                lines.append(f"- {reason}")

        risks = [_clean_text(self._normalize_risk(risk)) for risk in candidate.get("risks") or [] if _clean_text(self._normalize_risk(risk))]
        if risks:
            lines.extend(["", "**风险分析**:"])
            for risk in risks[:3]:
                lines.append(f"- {risk}")

        action = candidate.get("action", {})
        hook_message = _clean_text(action.get("hook_message"))
        verification_question = _clean_text(action.get("verification_question"))
        message_template = _clean_text(action.get("message_template"))
        deep_questions = _normalize_list(action.get("deep_questions"))

        if hook_message:
            lines.extend(["", "**钩子话术**:", f"- {hook_message}"])
        if verification_question:
            lines.extend(["", "**验证问题**:", f"- {verification_question}"])
        if message_template:
            lines.extend(["", "**完整联系话术**:", "```", message_template, "```"])
        if deep_questions:
            lines.extend(["", "**深问问题**:"])
            for question in deep_questions[:3]:
                lines.append(f"- {question}")

        lines.append("")
        return lines

    def _load_summary_stats(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        batch_input_path = self.output_dir / "batch_input.json"
        total_processed = len(candidates)
        total_received = len(candidates)
        total_excluded = 0
        excluded_list: List[str] = []

        if batch_input_path.exists():
            try:
                batch_input = json.loads(batch_input_path.read_text(encoding="utf-8"))
                source_candidates = batch_input.get("candidates", [])
                excluded = batch_input.get("excluded", [])
                if isinstance(source_candidates, list):
                    total_processed = len(source_candidates)
                if isinstance(excluded, list):
                    total_excluded = len(excluded)
                    total_received = total_processed + total_excluded
                    excluded_list = [
                        _clean_text(item.get("file_name") or item.get("reason") or "unknown")
                        for item in excluded
                        if isinstance(item, dict)
                    ]
            except Exception:
                pass

        return {
            "total_processed": total_processed,
            "recommended_count": len(candidates),
            "total_received": total_received,
            "total_excluded": total_excluded,
            "excluded_list": excluded_list,
        }

    def _display_name(self, candidate: Dict[str, Any]) -> str:
        for key in ("name", "candidate_name", "resume_name", "parsed_name", "full_name"):
            value = _clean_text(candidate.get(key))
            if value:
                return value
        return _clean_text(candidate.get("candidate_id")) or "未知候选人"

    def _role_label(self, candidate: Dict[str, Any]) -> str:
        for key in ("role_label", "title", "job_title"):
            value = _clean_text(candidate.get(key))
            if value:
                return value
        return ""

    def _decision_label(self, decision: Any) -> str:
        mapping = {
            "strong_yes": "strong_yes（强推）",
            "yes": "yes（值得联系）",
            "maybe": "maybe（备选）",
            "no": "no（不推进）",
        }
        return mapping.get(_clean_text(decision), _clean_text(decision) or "未评估")

    def _timing_label(self, timing: Any) -> str:
        mapping = {
            "today": "今天联系",
            "this_week": "本周联系",
            "optional": "可选 / 观察",
        }
        return mapping.get(_clean_text(timing), "待确认")

    def _summary_judgement(self, candidate: Dict[str, Any]) -> str:
        display_name = self._display_name(candidate)
        decision = _clean_text(candidate.get("decision"))
        match_fit = _clean_text(candidate.get("match_fit"))
        recruitability = _clean_text(candidate.get("recruitability"))

        if decision == "no":
            return f"{display_name} 当前不满足推进条件，match_fit={match_fit}，recruitability={recruitability}。"
        if decision == "maybe":
            return f"{display_name} 具备一定相关性，但仍需核验关键约束，match_fit={match_fit}，recruitability={recruitability}。"
        return f"{display_name} 具备推进价值，match_fit={match_fit}，recruitability={recruitability}。"

    def _normalize_risk(self, risk: Any) -> str:
        parsed = _try_parse_dict_like(risk)
        if parsed is not None:
            return _clean_text(parsed.get("description") or parsed.get("risk") or parsed.get("text"))
        if isinstance(risk, dict):
            return _clean_text(risk.get("description") or risk.get("risk") or risk.get("text"))
        return _clean_text(risk)

    def _build_overall_diagnosis(self, meta: Dict[str, Any], candidates: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
        contact_candidates = [candidate for candidate in candidates if candidate.get("decision") in {"strong_yes", "yes"}]
        maybe_candidates = [candidate for candidate in candidates if candidate.get("decision") == "maybe"]

        role_counts: Dict[str, int] = {}
        for candidate in candidates:
            role = self._role_label(candidate) or "未标注岗位"
            role_counts[role] = role_counts.get(role, 0) + 1

        role_mix = " / ".join(role for role, _ in sorted(role_counts.items(), key=lambda item: (-item[1], item[0]))[:3])
        role_part = f"候选人背景主要来自 {role_mix}。" if role_mix else ""

        return (
            f"本批次共处理 {stats['total_processed']} 份简历，其中 {len(contact_candidates)} 位值得联系，"
            f"{len(maybe_candidates)} 位作为备选。{role_part}"
        ).strip()

    def _build_batch_advice(self, meta: Dict[str, Any], candidates: List[Dict[str, Any]]) -> str:
        today_candidates = [candidate for candidate in candidates if candidate.get("action_timing") == "today"]
        this_week_candidates = [candidate for candidate in candidates if candidate.get("action_timing") == "this_week"]
        maybe_candidates = [candidate for candidate in candidates if candidate.get("decision") == "maybe"]

        advice_parts = []
        if today_candidates:
            advice_parts.append(f"优先推进 today 档 {len(today_candidates)} 位候选人")
        if this_week_candidates:
            advice_parts.append(f"本周完成 this_week 档 {len(this_week_candidates)} 位候选人的初筛")
        if maybe_candidates:
            advice_parts.append(f"对 {len(maybe_candidates)} 位 maybe 候选人重点核验职责边界和现实约束")

        if advice_parts:
            return "；".join(advice_parts) + "。"

        original = _clean_text(meta.get("batch_advice"))
        if original:
            return original
        return "建议先完成推荐池候选人的首轮沟通，再根据验证结果决定是否继续推进。"

    def _format_jd_section(self, jd: Any) -> List[str]:
        parsed = self._normalize_object(jd)
        lines = ["## 职位描述", ""]

        if not isinstance(parsed, dict):
            text = _clean_text(jd)
            if text:
                lines.extend([text, ""])
            return lines

        title = _clean_text(parsed.get("title"))
        location = _clean_text(parsed.get("base_location") or parsed.get("location"))
        salary_range = _clean_text(parsed.get("salary_range"))
        company_context = _clean_text(parsed.get("company_context"))
        seniority_level = _clean_text(parsed.get("seniority_level"))
        reporting_line = _clean_text(parsed.get("reporting_line"))
        travel_or_relocation = _clean_text(parsed.get("travel_or_relocation"))
        industry_context = _clean_text(parsed.get("industry_context"))
        language_requirements = _normalize_list(parsed.get("language_requirements"))
        eligibility_constraints = _normalize_list(parsed.get("eligibility_constraints"))
        domain_tags = _normalize_list(parsed.get("domain_tags"))

        if title:
            lines.append(f"- 职位: {title}")
        if location:
            lines.append(f"- 工作地点: {location}")
        if salary_range:
            lines.append(f"- 薪资范围: {salary_range}")
        if company_context:
            lines.append(f"- 公司背景: {company_context}")
        if seniority_level:
            lines.append(f"- Seniority: {seniority_level}")
        if reporting_line:
            lines.append(f"- Reporting Line: {reporting_line}")
        if travel_or_relocation:
            lines.append(f"- Travel / Relocation: {travel_or_relocation}")
        if industry_context:
            lines.append(f"- Industry Context: {industry_context}")
        if language_requirements:
            lines.append("- Language Requirements: " + " / ".join(language_requirements))
        if eligibility_constraints:
            lines.append("- Eligibility Constraints: " + " / ".join(eligibility_constraints))
        if domain_tags:
            lines.append("- Domain Tags: " + " / ".join(domain_tags))

        must_have = _normalize_list(parsed.get("must_have"))
        nice_to_have = _normalize_list(parsed.get("nice_to_have"))

        if must_have:
            lines.extend(["", "### Must Have"])
            lines.extend(f"- {item}" for item in must_have)
        if nice_to_have:
            lines.extend(["", "### Nice To Have"])
            lines.extend(f"- {item}" for item in nice_to_have)

        lines.append("")
        return lines

    def _format_company_section(self, company: Any) -> List[str]:
        parsed = self._normalize_object(company)
        lines = ["## 企业信息", ""]

        if isinstance(parsed, dict):
            for key, value in parsed.items():
                text = _clean_text(value)
                if text:
                    lines.append(f"- {key}: {text}")
        else:
            text = _clean_text(company)
            if text:
                lines.append(text)

        lines.append("")
        return lines

    def _normalize_object(self, value: Any) -> Any:
        if isinstance(value, dict):
            return value

        text = _clean_text(value)
        if not text:
            return {}

        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(text)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                continue

        return value
