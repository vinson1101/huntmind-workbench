# TalentFlow - 招聘 Skill Backend / Pipeline

> TalentFlow 是 HuntMind 的招聘 skill backend，不是 AI 员工本体。

---

## 先写死的设计公约（后续代码必须遵守）

### 1. 身份边界
- **HuntMind 才是 AI 招聘员工本体**
- **TalentFlow 只是专为 AI 招聘设计的 skill backend / workflow backend**
- TalentFlow 可以是独立工程，但不能拥有独立 agent 身份

### 2. 职责边界
#### HuntMind 负责
- 决策主体身份
- 模型选择（GLM / Gemini / Claude / OpenAI 等）
- API 配置与调用
- memory / context / system prompt
- 招聘判断
- 决定什么时候调用招聘 skill

#### TalentFlow 负责
- 简历读取
- PDF / 文本解析与标准化
- `batch_input.json` 构建与校验
- 对 HuntMind 返回结果做结构化后处理
- 生成 `final_output / quality_meta / final_report / owner_summary / run_meta`

### 3. skill 不能反客为主
TalentFlow **不负责**：
- 选择模型
- 管 API key
- 管 base_url
- 决定 prompt
- 自己变成另一个 bot

TalentFlow 只接收 bot 提供的判断能力或判断结果。

### 4. 当前阶段高度收敛
当前目标不是做通用招聘平台，也不是提前做商业化平台层。
当前阶段只打透一个窄场景：

**一个 JD + 一批真实简历 + HuntMind 判断 + 稳定结构化输出**

### 5. 语言选择原则
当前 **不因为 skill 化而重写成 JS/TS**。
现有 Python 代码继续作为 skill backend 保留；
未来如果 HuntMind runtime 需要 JS/TS，只补薄适配层，不整体重写 TalentFlow。

### 6. prompt 迁移原则
`configs/system_prompt.md` 里的有效招聘规则不能直接丢掉。
后续要把它拆到：
- `SKILL.md`：路由、阶段流程、关键守门原则
- `references/*.md`：决策规则、输出 contract、转化话术、写作约束
- `scripts/*.py`：确定性校验与后处理

### 7. 模型负责判断，脚本负责守门
- HuntMind / bot 负责判断
- TalentFlow / scripts 负责输入准备、结构校验、质量门禁、报告生成

---

## 项目定位

TalentFlow 的职责很简单：

1. 读取本地目录 / 外部目录中的简历
2. 解析 PDF / 文本并标准化候选人信息
3. 构建并校验 `batch_input`
4. 将 `batch_input` 交给外部 bot 的 decision handler，或者等待 HuntMind 自己读取并判断
5. 对 bot 返回结果做结构化后处理并落盘

一句话：

**HuntMind 对外，TalentFlow 对内。**
**HuntMind 是能力体，TalentFlow 是招聘 skill backend。**

---

## 当前工作方式

### A. TalentFlow 做准备
```bash
python pipelines/process_local_folder.py ./resumes --jd ./jd.json
```

这一步会完成：
- 读取简历
- 解析并标准化
- 生成 `batch_input.json`
- 生成 `run_meta.json`

### B. HuntMind 做判断
HuntMind 读取 `batch_input.json`，完成招聘判断，产出 JSON 结果。

### C. TalentFlow 做后处理
TalentFlow 使用 `core.runner` 和 `core.final_reporter` 对 HuntMind 的结果做：
- JSON 结构校验
- 业务清洗与兜底
- 质量门禁
- 报告生成

---

## 为什么这样设计

因为用户面对的是：
- “帮我筛这批简历”
- “给这批候选人联系优先级”
- “生成招聘判断报告”

用户不应该面对：
- 哪个脚本先跑
- 模型怎么配
- API key 放哪里
- prompt 长什么样

这些都应该由 HuntMind 和 skill backend 在内部编排完成。

---

## 输出产物

运行目录保留这些产物：
- `candidates/`
- `batch_input.json`
- `run_meta.json`
- `final_output.json`（在完成判断并回传后生成）
- `quality_meta.json`（在完成判断并回传后生成）
- `final_report.md`（在完成判断并回传后生成）
- `owner_summary.md`（在完成判断并回传后生成）

---

## 当前主接口（暂行）

### Python 接口
```python
from pipelines.process_local_folder import process_local_folder

result = process_local_folder(
    folder_path="./resumes",
    jd_data=jd_data,
    decision_handler=bot_decide,
    bot_name="huntmind",
)
```

其中 `bot_decide(batch_input) -> str` 由外部 bot 提供。
返回值必须是 `core.runner` 可消费的 JSON 文本。

### CLI 接口
```bash
python pipelines/process_local_folder.py ./resumes --jd ./jd.json
```

默认只做 skill 准备，不自己调用模型。

---

## 下一步代码改造顺序

### Step 1
先把约定固化到 README（当前已完成）

### Step 2
新增 `SKILL.md` 骨架，明确：
- 触发条件
- 输入形态
- 阶段流程
- 失败处理
- 调用哪些 references / scripts

### Step 3
把 `configs/system_prompt.md` 拆到：
- `references/decision-policy.md`
- `references/output-contract.md`
- `references/conversion-guidelines.md`
- `references/writing-style-constraints.md`

### Step 4
把确定性逻辑沉到脚本：
- 输入校验
- 输出校验
- 质量门禁
- 报告生成

### Step 5
继续清理仓库里会误导人为“TalentFlow 自己会调模型”的旧入口和旧残留

---

## 结论

TalentFlow 现在的目标不是“变成 AI 招聘员工”。
它的目标是：

**成为一个干净、可复用、专为招聘场景服务的 skill backend / pipeline。**

而 AI 员工本体，始终应该是 HuntMind。
