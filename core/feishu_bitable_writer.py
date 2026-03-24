"""
core/feishu_bitable_writer.py

将 TalentFlow 的最终结果写入飞书多维表格。
本模块是纯数据转换层，不直接调用飞书工具，而是通过 OpenClaw 的 feishu_bitable_* 工具执行写入。

职责边界：
- 读取 final_output.json、quality_meta.json、run_meta.json、owner_summary.md
- 将数据映射为飞书多维表格的记录格式
- 返回构造好的 records 列表，供调用者通过 feishu_bitable_* 工具写入
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

RUN_TABLE_NAME = "Runs"
CANDIDATES_TABLE_NAME = "Candidates"

# Runs 表字段定义（field_name → type）
# type: 1=文本, 2=数字, 3=单选, 4=多选, 5=日期, 7=复选框, 11=人员, 13=电话, 15=超链接, 1001=创建时间
RUN_FIELDS: Dict[str, int] = {
    "批次ID": 1,
    "JD标题": 1,
    "JD地点": 1,
    "JD薪资范围": 1,
    "候选人数": 2,
    "建议联系人数": 2,
    "Top候选人": 1,
    "质量分": 2,
    "质量标记": 1,
    "身份冲突数": 2,
    "平均分": 2,
    "输出版本": 1,
    "批次摘要": 1,
    "batch_input路径": 1,
    "final_output路径": 1,
    "创建时间": 5,
}

# Candidates 表字段定义
CANDIDATE_FIELDS: Dict[str, int] = {
    # 基础识别
    "批次ID": 1,
    "候选人ID": 1,
    "候选人姓名": 1,
    "规范姓名": 1,
    "角色标签": 1,
    "来源平台": 1,
    "原始文件名": 1,
    # AI 决策主字段
    "排名": 2,
    "综合评分": 2,
    "决策结论": 1,
    "优先级": 1,
    "行动时机": 1,
    "建议联系": 7,
    "核心判断": 1,
    "推荐理由": 1,
    "风险提示": 1,
    "核实问题": 1,
    "钩子消息": 1,
    "联系话术模板": 1,
    # 7维评分
    "硬技能匹配": 2,
    "经验深度": 2,
    "创新潜能": 2,
    "目标拆解执行": 2,
    "团队融合": 2,
    "意愿度": 2,
    "稳定性": 2,
    "模板ID": 1,
    "加权总分": 2,
    "证据摘要": 1,
    # 质量与身份
    "身份冲突": 7,
    "身份处理方案": 1,
    "冲突字段": 1,
    "质量备注": 1,
    # 人工跟进字段（预留，不覆盖）
    "跟进状态": 1,
    "HR负责人": 1,
    "HR备注": 1,
    "面试结果": 1,
    "拒绝原因": 1,
    "人工优先级": 1,
    "人工覆盖说明": 1,
    "最终结果": 1,
}

# 飞书字段类型映射到名称（用于日志输出）
FIELD_TYPE_NAMES = {
    1: "文本",
    2: "数字",
    3: "单选",
    4: "多选",
    5: "日期",
    7: "复选框",
    11: "人员",
    13: "电话",
    15: "超链接",
    17: "附件",
    1001: "创建时间",
    1002: "修改时间",
}


# ---------------------------------------------------------------------------
# 数据转换工具
# ---------------------------------------------------------------------------

def array_to_text(arr: Any, separator: str = "；") -> str:
    """将列表转为分隔符分隔的文本，用于表格展示（spec 默认用 ； 分隔）。"""
    if not arr:
        return ""
    if isinstance(arr, list):
        return separator.join(str(x) for x in arr)
    return str(arr)


def now_ms() -> int:
    """返回当前时间的毫秒时间戳。"""
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def extract_run_id_from_path(final_output_path: str) -> str:
    """从 final_output.json 路径中提取 run_id。"""
    # 路径格式: .../runs/run_20260323_214437/final_output.json
    m = re.search(r'run_(\d{8}_\d{6})', final_output_path)
    if m:
        return f"run_{m.group(1)}"
    # fallback: 用当前时间戳
    return f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


# ---------------------------------------------------------------------------
# Runs 表数据构建
# ---------------------------------------------------------------------------

def build_run_record(
    run_id: str,
    final_output_path: str,
    batch_input_path: str,
    quality_meta: Dict[str, Any],
    owner_summary: str,
    jd: Dict[str, Any],
    final_output: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    根据 Runs 表字段定义，从各数据源构造一条 Runs 记录。

    Args:
        run_id: 批次ID
        final_output_path: final_output.json 的绝对路径
        batch_input_path: batch_input.json 的绝对路径
        quality_meta: quality_meta.json 内容
        owner_summary: owner_summary.md 原文
        jd: batch_input.json 中的 jd 对象

    Returns:
        符合 Runs 表字段的 dict，key=field_name，value=字段值
    """
    # top_recommendations 中排名前 3~5 名（spec: 取前 3~5 名）
    top_recs = (final_output or {}).get("top_recommendations", [])
    top_3_5 = top_recs[:5]  # 取前5名
    top_names = [c.get("candidate_name", "") for c in top_3_5]
    top_candidate_names = "；".join(top_names)

    record = {
        "批次ID": run_id,
        "JD标题": jd.get("title", ""),
        "JD地点": jd.get("location", ""),
        "JD薪资范围": jd.get("salary_range", ""),
        "候选人数": quality_meta.get("candidate_count", 0),
        "建议联系人数": _calc_contact_count(final_output),
        "Top候选人": top_candidate_names,
        "质量分": quality_meta.get("quality_score", 0),
        "质量标记": quality_meta.get("quality_flag", ""),
        "身份冲突数": quality_meta.get("identity_conflict_count", 0),
        "平均分": round(quality_meta.get("avg_score", 0), 2),
        "输出版本": "v1",
        "批次摘要": owner_summary[:5000] if owner_summary else "",
        "batch_input路径": batch_input_path,
        "final_output路径": final_output_path,
        "创建时间": now_ms(),
    }
    return record


def _generate_quality_note(
    c: Dict[str, Any],
    total_score: float,
) -> str:
    """
    根据 spec 第9节规则自动生成 quality_note。
    - identity conflict 提示
    - 文案分数不同步检测（core_judgement 中提的分数 vs total_score）
    - evidence 占位检测
    """
    notes = []
    im = c.get("identity_meta", {})
    de = c.get("structured_score", {}).get("dimension_evidence", {})

    # 9.1 identity 冲突
    if im.get("has_conflict") is True:
        name = c.get("candidate_name", "候选人")
        notes.append(f"identity conflict: {name} 存在身份冲突")

    # 9.2 文案分数不同步（core_judgement 中提的分数 vs total_score）
    judgment = c.get("core_judgement", "")
    import re as _re
    scores_in_judgment = _re.findall(r"(\d+(?:\.\d+)?)\s*分", judgment)
    if scores_in_judgment:
        judgment_score = float(scores_in_judgment[0])
        if abs(judgment_score - total_score) > 1.0:
            notes.append("judgement score mismatch")

    # 9.3 evidence 明显占位检测
    generic_pattern = _re.compile(r"^[\u4e00-\u9fa5a-zA-Z_]+\u7ef4\u5ea6\u8bc4\u4f30$")
    for k, v in de.items():
        if v and generic_pattern.match(str(v).strip()):
            notes.append("dimension evidence too generic")
            break

    return "；".join(notes)


def _calc_contact_count(final_output: Dict[str, Any]) -> int:
    """统计 final_output 中 should_contact=true 的人数（spec 要求）。"""
    recs = final_output.get("top_recommendations", [])
    return sum(1 for r in recs if r.get("action", {}).get("should_contact") is True)


# ---------------------------------------------------------------------------
# Candidates 表数据构建
# ---------------------------------------------------------------------------

def build_candidate_records(
    run_id: str,
    final_output: Dict[str, Any],
    batch_input: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    根据 Candidates 表字段定义，从 final_output.json 和 batch_input.json 构造候选人记录列表。

    Args:
        run_id: 批次ID
        final_output: final_output.json 内容（dict）
        batch_input: batch_input.json 内容（dict）

    Returns:
        List[Dict]，每条为一条候选人记录
    """
    candidates_out = final_output.get("top_recommendations", [])
    candidates_in = batch_input.get("candidates", [])

    # 建立 candidate_id → batch_input 记录的映射（用于 source_file_name）
    in_map = {c.get("candidate_id", ""): c for c in candidates_in}

    records = []
    for c in candidates_out:
        candidate_id = c.get("candidate_id", "")

        # 从 batch_input 按 candidate_id 查找对应记录（spec: 优先 candidate_id 匹配）
        in_c = in_map.get(candidate_id, {})
        # fallback: 用 candidate_name 匹配
        if not in_c:
            for c2 in batch_input.get("candidates", []):
                if c2.get("name") == c.get("candidate_name"):
                    in_c = c2
                    break

        src = in_c.get("source", {})
        source_platform = src.get("platform", "")
        source_file_name = src.get("file_name", "")

        # resume_link: 飞书直传/云目录文件写入打开链接，非飞书来源则为空
        # 注意：飞书多维表格 URL 字段类型有域名验证限制，
        # 故使用文本类型字段存储链接，格式为 https://ucn43sn4odey.feishu.cn/file/{token}
        resume_link = ""
        if source_platform == "feishu":
            file_id = src.get("file_id", "")
            if file_id:
                resume_link = f"https://ucn43sn4odey.feishu.cn/file/{file_id}"
        # 其他平台（local/dingtalk 等）暂不生成链接

        # structured_score
        ss = c.get("structured_score", {})
        ds = ss.get("dimension_scores", {})
        de = ss.get("dimension_evidence", {})

        # 7维 evidence 拼接（spec: 硬技能：...；经验深度：...）
        dim_labels = {
            "hard_skill_match": "硬技能",
            "experience_depth": "经验深度",
            "innovation_potential": "创新潜能",
            "execution_goal_breakdown": "目标拆解执行",
            "team_fit": "团队融合",
            "willingness": "意愿度",
            "stability": "稳定性",
        }
        evidence_parts = [f"{dim_labels[k]}：{de.get(k, '')}" for k in dim_labels.keys() if de.get(k)]
        dimension_evidence_summary = "；".join(evidence_parts)

        # identity_meta
        im = c.get("identity_meta", {})
        identity_resolution = im.get("resolution", "unchanged")

        # action
        action = c.get("action", {})

        record = {
            # 基础识别
            "批次ID": run_id,
            "候选人ID": candidate_id,
            "候选人姓名": c.get("candidate_name", ""),
            "规范姓名": im.get("canonical_name", c.get("candidate_name", "")),
            "角色标签": c.get("role_label", ""),
            "来源平台": source_platform,
            "原始文件名": source_file_name,
            "简历链接": resume_link,
            # AI 决策主字段
            "排名": c.get("rank", 0),
            "综合评分": round(c.get("total_score", 0), 2),
            "决策结论": c.get("decision", ""),
            "优先级": c.get("priority", ""),
            "行动时机": c.get("action_timing", ""),
            "建议联系": action.get("should_contact", False),
            "核心判断": c.get("core_judgement", ""),
            "推荐理由": array_to_text(c.get("reasons", [])),
            "风险提示": array_to_text(c.get("risks", [])),
            "核实问题": action.get("verification_question", ""),
            "钩子消息": action.get("hook_message", ""),
            "联系话术模板": action.get("message_template", ""),
            # 7维评分
            "硬技能匹配": round(ds.get("hard_skill_match", 0), 2),
            "经验深度": round(ds.get("experience_depth", 0), 2),
            "创新潜能": round(ds.get("innovation_potential", 0), 2),
            "目标拆解执行": round(ds.get("execution_goal_breakdown", 0), 2),
            "团队融合": round(ds.get("team_fit", 0), 2),
            "意愿度": round(ds.get("willingness", 0), 2),
            "稳定性": round(ds.get("stability", 0), 2),
            "模板ID": ss.get("template_id", ""),
            "加权总分": round(ss.get("weighted_total", 0), 2),
            "证据摘要": dimension_evidence_summary[:3000],
            # 质量与身份
            "身份冲突": bool(im.get("has_conflict", False)),
            "身份处理方案": identity_resolution,
            "冲突字段": array_to_text(im.get("conflict_fields", [])),
            "质量备注": _generate_quality_note(c, c.get("total_score", 0)),
            # 人工跟进字段（预留，不覆盖）
            "跟进状态": "",
            "HR备注": "",
            "面试结果": "",
            "最终结果": "",
        }
        records.append(record)

    return records


# ---------------------------------------------------------------------------
# 批量写入辅助：字段过滤（只保留表定义的字段）
# ---------------------------------------------------------------------------

def filter_fields(record: Dict[str, Any], field_definitions: Dict[str, int]) -> Dict[str, Any]:
    """只保留在 field_definitions 中定义了的字段，去掉多余字段。"""
    return {k: v for k, v in record.items() if k in field_definitions}


def filter_run_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return filter_fields(record, RUN_FIELDS)


def filter_candidate_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return filter_fields(record, CANDIDATE_FIELDS)


# ---------------------------------------------------------------------------
# 核心读取函数（供调用者使用）
# ---------------------------------------------------------------------------

def load_run_sources(run_dir: str) -> Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any], str, Dict[str, Any]]:
    """
    从 run 目录加载所有数据源。

    Returns:
        (run_id, final_output, quality_meta, batch_input, owner_summary, jd)

    Raises:
        FileNotFoundError: 必需文件缺失
    """
    run_path = Path(run_dir)

    final_output_path = run_path / "final_output.json"
    quality_meta_path = run_path / "quality_meta.json"
    batch_input_path = run_path / "batch_input.json"
    owner_summary_path = run_path / "owner_summary.md"

    if not final_output_path.exists():
        raise FileNotFoundError(f"final_output.json not found: {final_output_path}")
    if not quality_meta_path.exists():
        raise FileNotFoundError(f"quality_meta.json not found: {quality_meta_path}")
    if not batch_input_path.exists():
        raise FileNotFoundError(f"batch_input.json not found: {batch_input_path}")
    if not owner_summary_path.exists():
        raise FileNotFoundError(f"owner_summary.md not found: {owner_summary_path}")

    with open(final_output_path, "r", encoding="utf-8") as f:
        final_output = json.load(f)

    with open(quality_meta_path, "r", encoding="utf-8") as f:
        quality_meta = json.load(f)

    with open(batch_input_path, "r", encoding="utf-8") as f:
        batch_input = json.load(f)

    with open(owner_summary_path, "r", encoding="utf-8") as f:
        owner_summary = f.read()

    run_id = extract_run_id_from_path(str(final_output_path.resolve()))
    jd = batch_input.get("jd", {})

    return run_id, final_output, quality_meta, batch_input, owner_summary, jd


def build_all_records(run_dir: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    从 run 目录构建 Runs 表单条记录 + Candidates 表所有记录。

    Returns:
        (run_record, candidate_records)
        run_record: Runs 表的单条记录
        candidate_records: Candidates 表的记录列表
    """
    run_id, final_output, quality_meta, batch_input, owner_summary, jd = load_run_sources(run_dir)

    # 解析 run_id 中的时间（用于 batch_input_path / final_output_path）
    fo_resolved = str((Path(run_dir) / "final_output.json").resolve())
    bi_resolved = str((Path(run_dir) / "batch_input.json").resolve())

    run_record = build_run_record(
        run_id=run_id,
        final_output_path=fo_resolved,
        batch_input_path=bi_resolved,
        quality_meta=quality_meta,
        owner_summary=owner_summary,
        jd=jd,
        final_output=final_output,
    )
    run_record = filter_run_record(run_record)

    candidate_records_raw = build_candidate_records(
        run_id=run_id,
        final_output=final_output,
        batch_input=batch_input,
    )
    candidate_records = [filter_candidate_record(r) for r in candidate_records_raw]

    return run_record, candidate_records
