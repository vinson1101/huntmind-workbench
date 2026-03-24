# Archive — 已废弃/被替代的脚本

此目录存放已被新流程取代的旧脚本，保留用于参考，不参与当前主路径。

## 已归档

| 文件 | 状态 | 说明 |
|------|------|------|
| `run_huntmind_local_folder.py` | ⚠️ DEPRECATED | 曾试图让 TalentFlow 自己调用模型，已废弃 |
| `run_openclaw_local_folder.py` | ⚠️ DEPRECATED | 对应 OpenClaw 旧版入口，已废弃 |
| `local_dev_entry.py` | ⚠️ DEPRECATED | 旧开发入口，已被 pipelines/ 取代 |
| `skill_entry.py` | ⚠️ DEPRECATED | 旧 skill 兼容层，已收敛到 SKILL.md |
| `feishu_folder_adapter.py` | 🔁 已替代 | 核心逻辑在 archive，但 `pipelines/process_feishu_folder.py` 尚未完全整合（TODO），当前通过 `archive/feishu_folder_adapter.py` 的 `load_feishu_resume_files()` 手动调用 |
| `test_feishu_ingest.py` | 🧪 测试文件 | 保留用于参考飞书接入测试 |

---

**主路径入口**：`pipelines/process_local_folder.py`
**执行约束**：`SKILL.md` Section 12 Execution Contract
