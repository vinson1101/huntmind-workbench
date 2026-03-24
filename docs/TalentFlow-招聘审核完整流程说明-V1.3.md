# TalentFlow 招聘审核系统 — 完整流程说明

> 版本：V1.3
> 最后更新：2026-03-24
> 负责人：HuntMind（AI 招聘决策 Agent）

---

## 一、系统定位

**TalentFlow** 是 HuntMind 的招聘执行后端，负责：
1. 简历读取与解析
2. 调用 HuntMind 进行 AI 评估决策
3. 生成结构化报告
4. 将结果写入飞书多维表格（HR 操作界面）

**核心原则**：所有简历最终汇入 `inbox/` 目录，pipeline 不区分来源，只按文件名扫描处理。

---

## 二、整体流程

```
阶段一：HR 准备
├── 1. 准备 JD（提供原始文本）
└── 2. 获取简历（两种方式）

阶段二：AI 处理
├── 3. JD 结构化解析
├── 4. 简历保存到 inbox
├── 5. 简历解析读入
├── 6. HuntMind AI 评估决策
└── 7. Pipeline 校验与报告生成

阶段三：结果输出
├── 8. 写入飞书多维表格（Runs 表 + Candidates 表）
└── 9. HR 在飞书中审核、联系候选人、填写反馈
```

---

## 三、阶段详解

### 阶段一：HR 准备（人工）

#### 1.1 准备 JD（文本）

HR 提供一段原始 JD 描述，示例：

```
公司：深圳某AI机器人创业公司
岗位：高级产品经理
地点：深圳南山
薪资：25-40K
硬性要求：5年以上B端产品经验，有从0到1搭建产品经验
加分项：有AI/硬件行业背景，有出海经验
```

> JD 可以是一段文字，AI 自动解析为结构化 JSON。

#### 1.2 获取简历（两种方式）

**方式A — 飞书云盘**
- HR 将候选人简历 PDF 上传到飞书云盘「简历」文件夹
- 告知 AI 该文件夹的 `folder_token`
- AI 自动下载到本地 `tmp/feishu_resumes/`，汇入 `inbox/`

**方式B — 聊天窗口直接发**
- HR 在飞书私信里直接发送 PDF 附件（单文件或多文件）
- AI 接收附件，保存到 `inbox/`

> **两种方式可以混合使用**，同一批候选人里部分来自飞书云盘、部分来自聊天窗口，最终都进入 `inbox/` 统一处理。

---

### 阶段二：AI 处理（自动）

#### 2.1 JD 结构化解析

AI 自动将 HR 提供的原始 JD 文本解析为结构化 JSON：

```json
{
  "title": "高级产品经理",
  "must_have": ["5年以上B端产品经验", "从0到1产品搭建经验"],
  "nice_to_have": ["AI/硬件行业背景", "出海经验"],
  "salary_range": "25-40K",
  "location": "深圳南山",
  "company_context": "深圳某AI机器人创业公司，商用清洁机器人赛道",
  "priority_focus": "skill"
}
```

字段说明：
| 字段 | 说明 | 来源 |
|------|------|------|
| title | 岗位名称 | 从 JD 文本提取 |
| must_have | 硬性要求（不满足即淘汰） | 从 JD 文本提取 |
| nice_to_have | 加分项 | 从 JD 文本提取 |
| salary_range | 薪资范围 | 从 JD 文本提取 |
| location | 工作地点 | 从 JD 文本提取 |
| company_context | 招聘单位背景 | 从 JD 文本提取（需 HR 包含） |
| priority_focus | 本次招聘侧重点 | 根据 JD 内容判断 |

#### 2.2 简历保存到 inbox

| 来源 | 处理方式 | source.platform | source.file_id |
|------|---------|----------------|----------------|
| 飞书云盘 | 调用 `load_feishu_resume_files()` 下载 | `"feishu"` | 飞书 file_token |
| 聊天窗口附件 | 接收附件保存到 inbox | `"local"` | 无 |

#### 2.3 简历解析读入

`resume_ingest.py` 扫描 `inbox/`，解析所有 PDF，生成 `batch_input.json`（包含候选人 ID、姓名、简历文本、来源信息）。

#### 2.4 HuntMind AI 评估决策

**7维评分体系**：

| 维度 | 权重 | 评估内容 |
|------|------|---------|
| 硬技能匹配 | 30% | 与 JD 硬技能要求的匹配程度 |
| 经验深度 | 25% | 相关领域工作年限 + 复杂度 |
| 创新潜能 | 15% | 项目成果、创新意识、学习能力 |
| 目标拆解执行 | 15% | 目标设定、拆解、执行力 |
| 团队融合 | 5% | 跨部门协作、沟通风格 |
| 意愿度 | 5% | 对岗位/薪资/地点的接受度 |
| 稳定性 | 5% | 离职原因、换工作频率、在职状态 |

**输出示例**：

```json
{
  "decision": "strong_yes",
  "total_score": 87.1,
  "priority": "A",
  "action_timing": "today",
  "reasons": ["3年B端产品经验匹配", "主导过大型项目", "薪资期望符合范围"],
  "risks": ["已婚末育，稳定性需观察"],
  "action": {
    "should_contact": true,
    "message_template": "您好X经理...",
    "verification_question": "您目前是在职状态吗？",
    "hook_message": "我注意到您曾主导过XXX项目..."
  }
}
```

**decision 决策标准**：
- `strong_yes`：核心技能完全匹配，建议立即联系
- `yes`：大部分匹配，值得联系
- `maybe`：部分匹配，作为备选
- `no`：核心不匹配，不建议联系

#### 2.5 Pipeline 校验与报告生成

1. **schema 校验**：`validate_model_output.py` 检查输出格式
2. **Sanitize**：清洗 Markdown 格式、截断超长文本
3. **加权计算**：按模板权重重算总分
4. **质量门禁**：检测 identity_conflict、low_variance、weak_ranking 等异常
5. **报告生成**：`final_output.json` + `owner_summary.md`

---

### 阶段三：结果输出

#### 3.1 写入飞书多维表格

自动写入两张表：

**Runs 表**（每批次一条）：
- 批次ID、JD信息、质量分、Top候选人名单、摘要

**Candidates 表**（每候选人一条）：
- 基础信息（姓名、ID、来源、简历链接）
- 决策结论（decision、priority、score、action_timing）
- 行动字段（推荐理由、风险提示、话术模板）
- 7维评分 + 证据摘要
- 身份冲突标记

**简历链接写入规则**：

| 来源 | batch_input 写入 | 简历链接 |
|------|-----------------|---------|
| 飞书云盘 | `file_id: "UL4rbKoR5oXSo..."` | `https://ucn43sn4odey.feishu.cn/file/{file_id}` |
| 聊天窗口 | `file_name: "张三.pdf"` | 空字符串 |

#### 3.2 飞书表格视图

每次发布后，HR 在飞书 UI 中设置过滤视图：
- 过滤条件：`批次ID` = 本次 run_id
- 排序：`排名` 升序

> 视图过滤设置目前需手动操作（API 权限限制）。

---

## 四、字段追踪

### 简历来源 → resume_link 链路

```
飞书云盘简历
    ↓ HR 告知 folder_token
load_feishu_resume_files(folder_token)
    ↓ 下载到 tmp/feishu_resumes/
    ↓ 记录 file_id = "UL4rbKoR5oXSo..."
    ↓ 写入 batch_input.candidates[i].source.file_id
    ↓
feishu_bitable_writer.py
    ↓ 读取 file_id
    ↓ 生成 resume_link = "https://ucn43sn4odey.feishu.cn/file/{file_id}"
    ↓ 写入「简历链接」列
```

```
聊天窗口简历
    ↓ HR 直接发送附件
保存到 inbox/ → 本地路径
    ↓ source.platform = "local"
    ↓ 无 file_id
    ↓ resume_link = ""（空）
```

---

## 五、飞书多维表格配置

| 项目 | 值 |
|------|-----|
| App Token | `AINFbZLOQaSo6rslOeZc95RTnPb` |
| App URL | https://ucn43sn4odey.feishu.cn/base/AINFbZLOQaSo6rslOeZc95RTnPb |
| Runs 表 ID | `tblv1QR1VRirZZGn` |
| Candidates 表 ID | `tblbiUBEv7rDWlli` |

**Runs 表字段**：批次ID / JD标题 / JD地点 / JD薪资范围 / 候选人数 / 建议联系人数 / Top候选人 / 质量分 / 质量标记 / 身份冲突数 / 平均分 / 输出版本 / 批次摘要 / batch_input路径 / final_output路径 / 创建时间 / 结果视图链接

**Candidates 表字段**：批次ID / 候选人ID / 排名 / 候选人姓名 / 规范姓名 / 简历链接 / 角色标签 / 来源平台 / 原始文件名 / 综合评分 / 决策结论 / 优先级 / 行动时机 / 建议联系 / 核心判断 / 推荐理由 / 风险提示 / 核实问题 / 钩子消息 / 联系话术模板 / 硬技能匹配 / 经验深度 / 创新潜能 / 目标拆解执行 / 团队融合 / 意愿度 / 稳定性 / 模板ID / 加权总分 / 证据摘要 / 身份冲突 / 身份处理方案 / 冲突字段 / 质量备注 / 跟进状态 / HR备注 / 面试结果 / 最终结果

---

## 六、HR 反馈字段

以下字段为 HR 专用，AI 不会覆盖：

| 字段 | 说明 |
|------|------|
| 跟进状态 | HR 填写（已联系 / 约面试 / 待回复 / 不合适） |
| HR备注 | HR 补充信息 |
| 面试结果 | HR 填写（通过 / 待定 / 不通过） |
| 最终结果 | HR 填写（入职 / 放弃 / 流程中） |

---

## 七、关键原则

1. **inbox 汇流**：所有简历最终进入 `inbox/`，pipeline 不区分来源
2. **source 追溯**：`source` 字段仅用于追溯和 resume_link 生成，不影响处理逻辑
3. **幂等写入**：同一批次重复发布不会丢失数据，HR 反馈字段不会被覆盖
4. **AI 只写结构化结果**：推荐理由、风险提示、话术模板等由 HuntMind 生成，不可由 HR 直接修改

---

## 八、当前状态

| 功能 | 状态 |
|------|------|
| 本地简历读取（inbox/） | ✅ 已实现 |
| 飞书云盘下载 | ✅ 已实现（`archive/feishu_folder_adapter.py`） |
| JD 结构化解析 | ⚠️ 待实现（需新增 `core/jd_parser.py`） |
| HuntMind AI 评估 | ✅ 已实现 |
| Pipeline（validate + runner + report） | ✅ 已实现 |
| 写入飞书多维表格 | ✅ 已实现 |
| 简历链接（feishu 来源） | ✅ 已实现 |
| 手动反馈字段保留 | ✅ 已实现 |
| 飞书视图自动过滤设置 | ⚠️ 受 API 权限限制，需手动设置 |

---

## 九、联系方式

- **系统**：TalentFlow（GitHub: vinson1101/talentflow）
- **AI 决策 Agent**：HuntMind
- **飞书多维表格**：https://ucn43sn4odey.feishu.cn/base/AINFbZLOQaSo6rslOeZc95RTnPb
