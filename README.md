# TalentFlow - 招聘决策 Skill / Pipeline

> HuntMind 驱动的招聘决策流水线，而不是独立 AI HR 本体

---

## 🎯 项目定位

TalentFlow 是 **HuntMind 的招聘决策流水线 / skill**，负责：

- 多渠道简历摄入（飞书、本地目录等）
- PDF / 文本解析与候选人标准化
- batch_input 构建与 schema 校验
- 调用外部 evaluator 完成候选人评估
- 生成 final_output / final_report / owner_summary 等产物

**TalentFlow 不是默认持有模型身份的 AI HR。**

在产品主路径中：
- **HuntMind** 是 AI native 招聘专员 / 决策主体
- **TalentFlow** 是执行流水线 / skill
- **招聘判断权默认属于 HuntMind，而不是 TalentFlow**

---

## 🧭 产品 / 工程边界

### HuntMind 负责
- 持有模型身份、persona、memory、策略
- 组织 JD / 公司背景 / 招聘上下文
- 注入 evaluator
- 对外承担招聘决策主体身份

### TalentFlow 负责
- 文件扫描 / 下载 / 解析
- schema 对齐与运行时校验
- 批处理与产物落盘
- 调用 evaluator 并衔接 runner / reporter

### fallback evaluator 的定位
TalentFlow 仍保留 fallback evaluator，但 **只允许用于**：
- `local_dev`
- `test`
- `emergency_debug`

它**不再是默认产品路径**，也不再代表 TalentFlow 是独立 AI HR。

---

## 📁 当前关键目录

```text
talentflow/
├── adapters/
├── configs/
├── core/
│   ├── batch_builder.py
│   ├── candidate_store.py
│   ├── evaluator.py              # fallback evaluator 实现
│   ├── evaluator_resolver.py     # evaluator 解析与模式门控
│   ├── final_reporter.py
│   ├── resume_ingest.py
│   ├── runner.py
│   └── runtime.py                # RunMode / RuntimeContext
├── entrypoints/
│   ├── local_dev_entry.py        # 开发入口，允许 fallback
│   └── skill_entry.py            # 产品入口，必须注入 evaluator
├── pipelines/
│   ├── process_feishu_folder.py
│   └── process_local_folder.py
└── skills/
```

---

## 🚀 运行模式

TalentFlow 当前支持以下运行模式：

- `external`：产品主路径，**必须显式注入 evaluator**
- `local_dev`：本地开发，允许 fallback evaluator
- `test`：测试模式，允许 fallback evaluator
- `emergency_debug`：应急排障，允许 fallback evaluator

### 最重要的默认行为
`process_local_folder(..., run_mode="external")` 是默认行为。

这意味着：
- 没有注入 evaluator 时，**不会再自动回退到 TalentFlow 自带 evaluator**
- 只有显式进入 `local_dev/test/emergency_debug`，才允许 fallback

---

## ✅ 推荐用法

### 1. 产品主路径：由 HuntMind 注入 evaluator

```python
from entrypoints.skill_entry import run_talentflow_skill

result = run_talentflow_skill(
    folder_path="/data/resumes",
    jd_data=jd_data,
    evaluator=huntmind_evaluator,
)
```

### 2. 本地开发：显式使用开发入口

```python
from entrypoints.local_dev_entry import run_local_dev

result = run_local_dev(
    folder_path="/data/resumes",
    jd_data=jd_data,
)
```

### 3. CLI：本地开发模式

```bash
python pipelines/process_local_folder.py /data/resumes \
  --jd company_jd.json \
  --run-mode local_dev
```

---

## 📊 run_meta 新增字段

每次运行都会在 `run_meta.json` 中记录：

- `run_mode`
- `decision_owner`
- `evaluator_source`
- `model_identity`
- `fallback_allowed`

这样可以明确区分：
- 这次是不是由 HuntMind 做判断
- 这次是不是开发态 fallback 运行
- 哪些结果可作为产品验证，哪些只适用于调试

---

## 📌 当前架构决策

1. **HuntMind 是唯一默认招聘决策主体**
2. **TalentFlow 是招聘决策 skill / pipeline**
3. **TalentFlow 保留 fallback evaluator，但仅限受控场景**
4. **产品主路径必须外部注入 evaluator**
5. **所有运行产物必须记录 decision owner 与 evaluator source**

---

## 📝 状态

- 本地闭环：已跑通
- 输出层：已完成一轮修复
- 当前阶段：收敛产品边界，落实 HuntMind 接管默认决策权

---

**创建时间**：2026年3月22日  
**当前方向**：从“可独立评估的工具”收敛为“HuntMind 驱动的招聘 skill”
