# 飞书多维表格字段映射文档（V1）

> 本文档定义 TalentFlow 输出结果写入飞书多维表格的字段映射规则。
> 对应代码：`core/feishu_bitable_writer.py`
>
> **V1 原则**：
> - `final_output.json` 是候选人决策真相
> - `quality_meta.json` / `owner_summary.md` / `batch_input.json` 是批次补充来源
> - `run_meta.json` 存在时优先读取，不存在时 fallback
> - 飞书多维表格是 HR / 业务侧使用界面
> - 当前只做标准字段写入，不做客户自定义字段映射

---

## 1. 数据来源

| 来源文件 | 用途 |
|---------|------|
| `final_output.json` | 候选人决策主数据（top_recommendations） |
| `quality_meta.json` | 批次质量元数据 |
| `batch_input.json` | JD 信息、候选人输入（含 source 字段） |
| `owner_summary.md` | HR 可读摘要 |
| `run_meta.json` | run_id / created_at（存在时优先） |

---

## 2. Runs 表字段映射

| 飞书字段 | 类型 | 数据来源 | 说明 |
|---------|------|---------|------|
| `run_id` | 文本 | `run_meta.run_id`，无则解析 final_output 路径 | 格式：`run_YYYYMMDD_HHMMSS` |
| `jd_title` | 文本 | `batch_input.jd.title` | 岗位名称 |
| `jd_location` | 文本 | `batch_input.jd.location` | 城市/地点 |
| `jd_salary_range` | 文本 | `batch_input.jd.salary_range` | 薪资范围 |
| `candidate_count` | 数字 | `quality_meta.candidate_count` | 候选人总数 |
| `contact_count` | 数字 | 统计 `final_output.top_recommendations[i].action.should_contact = true` 的人数 | 建议联系人数 |
| `top_candidate_names` | 文本 | `final_output.top_recommendations[0:5]` 的 `candidate_name`，用 `；` 分隔 | 前5名候选人 |
| `quality_score` | 数字 | `quality_meta.quality_score` | 批次质量分（0-100） |
| `quality_flag` | 文本 | `quality_meta.quality_flag` | ok / warning / fail |
| `identity_conflict_count` | 数字 | `quality_meta.identity_conflict_count`，无则统计 final_output | 身份冲突人数 |
| `avg_score` | 数字 | `quality_meta.avg_score`（保留2位小数） | 平均分 |
| `output_version` | 文本 | 固定值 `"talentflow-v1"` | 输出版本标记 |
| `owner_summary` | 文本 | `owner_summary.md` 原文（截断至5000字） | HR 摘要 |
| `batch_input_path` | 文本 | batch_input.json 绝对路径 | 追溯用 |
| `final_output_path` | 文本 | final_output.json 绝对路径 | 追溯用 |
| `created_at` | 日期 | `run_meta.created_at`，无则当前时间（毫秒时间戳） | 批次创建时间 |

---

## 3. Candidates 表字段映射

### 3.1 基础识别字段

| 飞书字段 | 类型 | 数据来源 | 说明 |
|---------|------|---------|------|
| `run_id` | 文本 | 同 Runs 表 | 关联所属批次 |
| `candidate_id` | 文本 | `final_output.top_recommendations[i].candidate_id` | 系统唯一 ID |
| `candidate_name` | 文本 | `candidate_name`，无则取 `name` | 展示姓名 |
| `canonical_name` | 文本 | `identity_meta.canonical_name`，无则 `candidate_name` | 归一姓名 |
| `role_label` | 文本 | `role_label` | 候选人角色标签 |
| `source_platform` | 文本 | `batch_input.candidates[i].source.platform` | 如 local / feishu / dingtalk |
| `source_file_name` | 文本 | `batch_input.candidates[i].source.file_name` | 原始简历文件名 |

> **匹配规则**：`candidate_id` 精确匹配 → `candidate_name` 匹配 → `canonical_name` 匹配

### 3.2 AI 决策主字段

| 飞书字段 | 类型 | 数据来源 | 说明 |
|---------|------|---------|------|
| `rank` | 数字 | `rank` | 最终排名（1-N） |
| `total_score` | 数字 | `total_score`（脚本重算后，保留2位小数） | 综合评分 |
| `decision` | 文本 | `decision` | strong_yes / yes / maybe / no |
| `priority` | 文本 | `priority` | A / B / C |
| `action_timing` | 文本 | `action_timing` | today / this_week / optional / no_action |
| `should_contact` | 复选框 | `action.should_contact` | 是否建议联系（true/false） |
| `core_judgement` | 文本 | `core_judgement` | 核心判断文本 |
| `reasons` | 文本 | `reasons[]` → `；` 分隔 | 理由列表 |
| `risks` | 文本 | `risks[]` → `；` 分隔 | 风险列表 |
| `verification_question` | 文本 | `action.verification_question` | 首轮验证问题 |
| `hook_message` | 文本 | `action.hook_message` | 开场钩子 |
| `message_template` | 文本 | `action.message_template` | 推荐联系话术 |

### 3.3 7维评分字段

| 飞书字段 | 类型 | 数据来源 | 说明 |
|---------|------|---------|------|
| `hard_skill_match` | 数字 | `structured_score.dimension_scores.hard_skill_match` | 硬技能匹配 |
| `experience_depth` | 数字 | `structured_score.dimension_scores.experience_depth` | 经验深度 |
| `innovation_potential` | 数字 | `structured_score.dimension_scores.innovation_potential` | 创新潜能 |
| `execution_goal_breakdown` | 数字 | `structured_score.dimension_scores.execution_goal_breakdown` | 目标拆解执行 |
| `team_fit` | 数字 | `structured_score.dimension_scores.team_fit` | 团队融合 |
| `willingness` | 数字 | `structured_score.dimension_scores.willingness` | 意愿度 |
| `stability` | 数字 | `structured_score.dimension_scores.stability` | 稳定性 |
| `template_id` | 文本 | `structured_score.template_id` | 命中的评分模板 |
| `weighted_total` | 数字 | `structured_score.weighted_total` | 模板加权后总分 |
| `dimension_evidence_summary` | 文本 | `structured_score.dimension_evidence` 7维拼接 | 证据摘要 |

**`dimension_evidence_summary` 拼接格式**：

```
硬技能：...；经验深度：...；创新潜能：...；目标拆解执行：...；团队融合：...；意愿度：...；稳定性：...
```

### 3.4 身份与质量字段

| 飞书字段 | 类型 | 数据来源 | 说明 |
|---------|------|---------|------|
| `has_identity_conflict` | 复选框 | `identity_meta.has_conflict` | 是否存在身份冲突 |
| `identity_resolution` | 文本 | `identity_meta.resolution` | unchanged / corrected / flagged |
| `conflict_fields` | 文本 | `identity_meta.conflict_fields[]` → `；` 分隔 | 冲突字段列表 |
| `quality_note` | 文本 | 规则自动生成（见第5节） | 人工复核提示 |

### 3.5 人工跟进字段（预留，不自动覆盖）

| 飞书字段 | 说明 |
|---------|------|
| `follow_up_status` | HR 跟进状态 |
| `hr_owner` | HR 负责人 |
| `hr_comment` | HR 备注 |
| `interview_result` | 面试结果 |
| `reject_reason` | 拒绝原因 |
| `manual_priority` | 人工优先级 |
| `manual_override_note` | 人工覆盖说明 |
| `final_outcome` | 最终结果 |

---

## 4. 字段格式化规则

| 规则 | 说明 |
|------|------|
| 数组转文本 | `reasons`、`risks`、`conflict_fields`、`top_candidate_names` 用 `；` 分隔 |
| 浮点分数 | `total_score`、`weighted_total`、7维分数保留2位小数 |
| 布尔值 | `should_contact`、`has_identity_conflict` → 复选框（true/false） |
| 空值处理 | 文本字段写空字符串 `""`，数字字段写 `None`（不写 0） |
| 文本截断 | `owner_summary` 截断至5000字，`dimension_evidence_summary` 截断至3000字 |

---

## 5. quality_note 自动生成规则

出现以下情况时自动写入提示（用 `；` 分隔多条）：

| 异常类型 | 判断条件 | 写入内容 |
|---------|---------|---------|
| identity 冲突 | `identity_meta.has_conflict = true` | `identity conflict: {name} 存在身份冲突` |
| 文案分数不同步 | `core_judgement` 中提取的分数与 `total_score` 差值 > 1.0 | `judgement score mismatch` |
| evidence 占位 | 任何维度 evidence 匹配正则 `^[\u4e00-\u9fa5a-zA-Z_]+\u7ef4\u5ea6\u8bc4\u4f30$` | `dimension evidence too generic` |

无异常时写入空字符串。

---

## 6. 唯一键与写入策略

| 表 | 唯一键 | 重复发布行为 |
|---|--------|------------|
| Runs | `run_id` | **UPSERT**：同一 `run_id` 存在则更新，不重复新增 |
| Candidates | `run_id + candidate_id` | **UPSERT**：同一 run 中重复发布则更新该行；不同 run 允许保留多条 |

> 实现方式：先 list 查询是否存在 → 存在则 batch_update，不存在则 batch_create。

---

## 7. 飞书多维表格配置信息

| 项目 | 值 |
|------|-----|
| App Token | `AINFbZLOQaSo6rslOeZc95RTnPb` |
| App 名称 | TalentFlow Results |
| App URL | https://ucn43sn4odey.feishu.cn/base/AINFbZLOQaSo6rslOeZc95RTnPb |
| Runs 表 ID | `tbl5gnhs4x8iAJon` |
| Candidates 表 ID | `tblGKQ2DFMrJ2Cqd` |

---

*最后更新：2026-03-24（V1 spec 对齐版）*
