# HuntMind Decision Policy v2.1

## 1. 目的

本文件定义 HuntMind 在招聘决策中的显式判断规则。

它的作用不是替代 SOUL，而是把 SOUL 中的招聘判断原则，收敛为：

- 可执行
- 可结构化
- 可复核
- 可在 runner 中强制落地

本文件的目标是解决以下问题：

1. 避免“会分析，但不做明确决策”
2. 避免 `recruitability` 与 `willingness` 混用
3. 避免 `decision` 脱离 `match_fit × recruitability` 矩阵
4. 避免 `hard_mismatch` 被高意愿或漂亮话术掩盖
5. 让招聘判断具备稳定的收敛逻辑

---

## 2. 决策总原则

HuntMind 的最终决策，不由单一维度决定，而由以下四个核心变量共同决定：

1. `match_fit`
2. `recruitability`
3. `willingness`
4. `mismatch_type`

其中：

- `match_fit` 和 `recruitability` 决定主决策矩阵
- `mismatch_type` 和 `hard_constraints` 决定是否需要强制降级
- `willingness` 只作为辅助信息，不得替代 `recruitability`

---

## 3. 决策输出目标

每位候选人必须最终收敛为以下结构化决策之一：

- `strong_yes`
- `yes`
- `maybe`
- `no`

并同步给出：

- `priority`
- `action_timing`
- `reasons`
- `risks`
- `message_template`
- `deep_questions`

---

## 4. 输入变量定义

### 4.1 `match_fit`

表示候选人与岗位要求的匹配度。

取值建议：

- `high`
- `medium`
- `low`

`match_fit` 来自结构化证据聚合，而不是主观印象。

---

### 4.2 `recruitability`

表示企业在当前现实约束下，将候选人推进并成功招到的现实可达性。

取值建议：

- `high`
- `medium`
- `low`

`recruitability` 必须优先看现实约束，而不是候选人主观兴趣。

---

### 4.3 `willingness`

表示候选人主观上是否可能愿意了解、沟通或接受该机会。

取值建议：

- `high`
- `medium`
- `low`
- `unknown`

`willingness` 只能作为辅助变量，不能推翻 `recruitability`。

---

### 4.4 `mismatch_type`

表示错配类型。

取值建议：

- `hard_mismatch`
- `recoverable`
- `none`

其中：

#### `hard_mismatch`

明显硬错配，例如：

- 核心职能不匹配
- 核心硬条件缺失
- 经验方向明显错误
- 明显不具备最低进入门槛

#### `recoverable`

存在缺口，但仍可能通过转型、补能力、信息核验来推进，例如：

- 相邻岗位转型
- 行业切换但职能匹配
- 经验不足但轨迹合理
- 条件接近但需进一步核验

#### `none`

没有明显错配，进入正常决策矩阵。

---

### 4.5 `hard_constraints`

表示硬约束触发情况。

常见包括：

- 地点绝对不可行
- 薪资严重不匹配
- 必须语言/身份/签证条件不满足
- 最低年限严重不满足
- 必须行业或必须客户关系完全缺失（且不可恢复）

`hard_constraints` 一旦明确触发，优先级高于普通矩阵判断。

---

## 5. 7维度与决策矩阵的关系

HuntMind 可以继续使用已有的 7 维度评估体系，但必须明确：

> **7维度是底层评估层，不是最终决策层。**

正确关系如下：

7维度 / 结构化证据
→ 形成 `match_fit`
→ 形成 `recruitability`
→ 辅助判断 `willingness`
→ 判断 `mismatch_type`
→ 进入 decision matrix
→ 输出最终 `decision`

### 5.1 7维度的作用

7维度负责回答：

- 这个人在哪些方面匹配
- 哪些地方存在缺口
- 风险点在哪里
- 是否属于可恢复错配

### 5.2 决策矩阵的作用

决策矩阵负责回答：

- 在当前招聘现实里，这个人最终应不应该推进

因此：

- 7维度 ≠ 最终决策
- 决策矩阵 ≠ 重新分析一遍所有信息
- 两者是上下层关系，不冲突

---

## 6. `match_fit` 判断规则

`match_fit` 不能完全由模型自由发挥，必须基于结构化证据聚合。

建议至少参考以下来源：

1. must_have 命中情况
2. nice_to_have 覆盖情况
3. 核心职能是否匹配
4. 岗位方向是否匹配
5. 行业/赛道相关性
6. 年限/层级合理性
7. 是否存在 `hard_mismatch` / `recoverable`

### 6.1 `match_fit = high`

通常满足以下条件中的多数：

- must_have 大部分命中
- 核心职能匹配
- 岗位方向匹配
- 行业/场景相关
- 关键证据充分且可信
- 无明显硬错配

### 6.2 `match_fit = medium`

通常适用于：

- 部分 must_have 命中
- 存在一定缺口
- 方向大体相关
- 需要通过核验进一步确认
- 可能属于 `recoverable`

### 6.3 `match_fit = low`

通常适用于：

- must_have 大量缺失
- 职能明显不对
- 岗位方向错误
- 关键证据薄弱
- 存在明显硬错配或严重偏离

---

## 7. `recruitability` 判断规则

`recruitability` 必须独立判断，不得由 `willingness` 代替。

### 7.1 四子维结构

建议拆成四个子维度：

#### A. `compensation_feasibility`

薪资可达性

看：

- JD 薪资范围
- 候选人当前/期望薪资
- 薪资弹性
- 市场溢价可能性

#### B. `location_feasibility`

地点可行性

看：

- base location
- 是否支持远程
- 是否需要搬迁
- 是否长期出差
- 候选人当前城市与可迁移意愿

#### C. `seniority_fit`

层级承接度

看：

- 岗位层级
- 候选人当前层级
- 是否过高/过低
- 是否能接受该岗位现实上下级结构

#### D. `eligibility_constraint`

资格硬条件

看：

- 身份/签证/合法工作资格
- 语言要求
- 特定行业合规或资质要求
- 特殊地域限制

---

### 7.2 `recruitability = high`

通常满足：

- 薪资基本可承接
- 地点可行
- 层级匹配
- 无明显硬资格障碍

### 7.3 `recruitability = medium`

通常满足：

- 存在一些现实阻力
- 但仍可通过沟通、调包、迁移、进一步核验推进

### 7.4 `recruitability = low`

通常满足：

- 薪资明显不现实
- 地点明显不可行
- 层级严重失衡
- 资格硬条件受阻
- 即使候选人可能愿意聊，也很难真正推进成功

---

## 8. `willingness` 判断规则

`willingness` 是辅助维度，不是主决策维度。

### 8.1 可以参考的信号

- 简历轨迹是否显示转岗意愿
- 当前岗位阶段是否适合跳槽
- 背景是否自然承接该机会
- 沟通切入点是否明确
- 是否具备明显动机信号

### 8.2 不得做的事

- 不得因为候选人“可能愿意聊”，就把 `recruitability` 判高
- 不得让高 `willingness` 覆盖 `hard_mismatch`
- 不得让高 `willingness` 自动推高最终 `decision`

### 8.3 正确作用

`willingness` 主要用于：

- 调整沟通优先级
- 辅助判断 action timing
- 影响 message_template 和 hook 设计
- 在 `match_fit` 和 `recruitability` 接近时，作为轻量排序因子

---

## 9. `mismatch_type` 判断规则

### 9.1 `hard_mismatch`

触发示例：

- 职能完全错位
- 缺少岗位最核心硬门槛
- 行业/客户关系为硬要求且明显缺失
- 层级差距极大且不可恢复
- 关键资格硬约束不满足

**规则：一旦是 `hard_mismatch`，最终 decision 不得高于 `no`。**

---

### 9.2 `recoverable`

触发示例：

- 相邻岗位转型
- 行业切换但职能相近
- 缺口存在但可以通过核验确认
- 经验略弱但轨迹合理
- 条件略有偏差但仍可能推进

**规则：`recoverable` 允许进入 `maybe` 或保守 `yes`，但必须附带明确核验问题。**

---

### 9.3 `none`

说明无明显错配，进入正常矩阵判断。

---

## 10. 决策执行顺序

HuntMind / runner 必须按以下顺序执行：

1. 判断 `hard_constraints`
2. 判断 `mismatch_type`
3. 判断 `match_fit`
4. 判断 `recruitability`
5. 参考 `willingness`
6. 应用 `decision_matrix`
7. 输出最终 `decision / priority / action_timing`

---

## 11. 决策矩阵（核心）

### 11.1 前置强约束

#### 规则 A：硬错配优先

如果：

- `mismatch_type = hard_mismatch`
  或
- 明确触发 `hard_constraints`

则：

- `decision = no`
- `priority = N`
- `action_timing = do_not_contact`

该规则优先级最高。

---

### 11.2 常规矩阵

#### Case 1

- `match_fit = high`
- `recruitability = high`
- `mismatch_type = none`

默认：

- `decision = strong_yes`
- `priority = A`
- `action_timing = today`

---

#### Case 2

- `match_fit = high`
- `recruitability = medium`
- `mismatch_type = none`

默认：

- `decision = yes`
- `priority = A 或 B`
- `action_timing = today / this_week`

说明：

- 很值得联系，但现实阻力需要在沟通中尽快确认

---

#### Case 3

- `match_fit = medium`
- `recruitability = high`
- `mismatch_type = none 或 recoverable`

默认：

- `decision = yes 或 maybe`
- `priority = B`
- `action_timing = this_week`

说明：

- 招得到，但是否值得投入要看缺口是否关键

---

#### Case 4

- `match_fit = medium`
- `recruitability = medium`
- `mismatch_type = recoverable`

默认：

- `decision = maybe`
- `priority = C`
- `action_timing = hold / this_week_optional`

说明：

- 可以作为备选，但必须附带明确核验点

---

#### Case 5

- `match_fit = high`
- `recruitability = low`

默认：

- `decision = maybe 或 no`
- `priority = C 或 N`
- `action_timing = hold`

说明：

- 纸面上很匹配，但现实上很难招得到，不能直接判高优先级

---

#### Case 6

- `match_fit = low`
- `recruitability = high`

默认：

- `decision = no 或 maybe`
- `priority = N 或 C`
- `action_timing = do_not_contact / hold`

说明：

- 好招不等于值得招

---

#### Case 7

- `match_fit = low`
- `recruitability = medium/low`

默认：

- `decision = no`
- `priority = N`
- `action_timing = do_not_contact`

---

## 12. `strong_yes / yes / maybe / no` 的标准

### 12.1 `strong_yes`

必须同时满足大部分条件：

- `match_fit` 高
- `recruitability` 高
- 无硬错配
- 风险可控
- 证据充分
- 值得立即联系

---

### 12.2 `yes`

适用于：

- 大部分条件满足
- 存在小风险但可接受
- 值得推进
- 不一定是最优，但明确值得联系

---

### 12.3 `maybe`

适用于：

- 部分匹配
- 信息不足
- 存在 `recoverable`
- 存在明显现实阻力
- 可以作为备选，但不应高优先级推进

---

### 12.4 `no`

适用于：

- 核心不匹配
- `recruitability` 过低
- 存在 `hard_mismatch`
- 风险过高，不值得投入联系成本

---

## 13. `priority` 与 `action_timing` 映射规则

### 13.1 `priority`

建议映射：

- `A`：立即推进
- `B`：值得推进
- `C`：备选观察
- `N`：不推进

### 13.2 `action_timing`

建议映射：

- `today`
- `this_week`
- `hold`
- `do_not_contact`

### 13.3 默认关系

- `strong_yes` → `A` + `today`
- `yes` → `A/B` + `today/this_week`
- `maybe` → `C` + `hold/this_week`
- `no` → `N` + `do_not_contact`

---

## 14. 输出解释要求

### 14.1 `reasons`

必须解释：

- 为什么匹配
- 哪些证据支撑推进
- 哪些现实因素支持可达性

### 14.2 `risks`

必须解释：

- 哪些地方可能影响推进
- 哪些风险需要核验
- 哪些现实因素降低 recruitability

### 14.3 `deep_questions`

如果存在：

- `recoverable`
- 低可达性
- 信息缺口
- 关键 must_have 不确定

则必须生成针对性核验问题。

---

## 15. 缺信息时的处理原则

当 JD 或简历信息不足时：

### 可以保守下调

- `recruitability`
- `match_fit`
- `priority`

### 不可以做的事

- 不得凭空脑补关键字段
- 不得因为信息不全就自动乐观
- 不得用高 `willingness` 填补信息缺口

### 正确做法

- 显式说明“不确定性”
- 将其体现到 `risks` 或 `deep_questions`
- 必要时降为 `maybe`

---

## 16. Runner 落地要求（实现约束）

实现层建议显式存在以下逻辑：

- `_judge_mismatch_type()`
- `_apply_hard_constraints()`
- `_compute_match_fit()`
- `_compute_recruitability()`
- `_apply_decision_matrix()`

### 原则

- 最终 `decision / priority / action_timing` 必须可由结构化变量复核
- 不允许完全依赖模型自由输出最终决策
- 如 runner 覆盖模型结果，必须留下 override trace

---

## 17. 一致性要求

本文件必须与以下内容保持一致：

- `SOUL.md`
- `output.schema.json`
- `system_prompt.md`
- `runner.py`

若出现冲突，以“更保守、更可执行、更可复核”的版本为准，并尽快同步修订。

---

## 18. 一句话总结

> HuntMind 的最终招聘判断，必须由结构化的 `match_fit × recruitability` 矩阵收敛得出，并受 `mismatch_type` 与硬约束保护；`willingness` 只能辅助推进，不能替代现实可达性。
