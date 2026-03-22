# 输出契约（Output Contract）

本文件定义 HuntMind 在招聘决策阶段输出结果必须满足的结构约束。

## 基本要求

- 输出必须是一个合法 JSON object
- 不允许输出 Markdown、解释、前后缀或额外文本
- 所有字段必须符合既定输出结构
- 不允许遗漏 required 字段

## 顶层字段

输出必须包含：
- `overall_diagnosis`
- `top_recommendations`
- `batch_advice`

## recommendation 字段要求

每个 recommendation 必须包含：
- `candidate_id`
- `rank`
- `total_score`
- `decision`
- `priority`
- `action_timing`
- `core_judgement`
- `reasons`
- `risks`
- `score_breakdown`
- `action`

## action 字段要求

每个 `action` 必须包含：
- `should_contact`
- `hook_message`
- `verification_question`
- `message_template`
- `deep_questions`

## decision 合法枚举

`decision` 只能是：
- `strong_yes`
- `yes`
- `maybe`
- `no`

## rank / score 规则

- `rank` 必须从 1 开始递增
- `rank=1` 表示当前批次最值得优先联系的人
- `total_score` 使用 0-100 分

## score_breakdown 要求

必须输出 `score_breakdown`，包含：
- `hard_skill`
- `experience`
- `stability`
- `potential`
- `conversion`

各项应为 0-100 之间的整数或小数。

## 结构 vs 守门

本文件定义语言层约束；
真正的结构合法性与字段完整性，必须再由脚本校验：
- `scripts/validate_model_output.py`
- `scripts/quality_gate.py`
