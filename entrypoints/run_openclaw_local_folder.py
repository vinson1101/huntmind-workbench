"""
DEPRECATED — 本文件已废弃，不应再被使用。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  本入口已被废弃，不再代表 TalentFlow 的正确使用方式。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

错误设计：
    此入口曾体现"TalentFlow 自己调用模型"的旧架构。
    HuntMind 是 AI 招聘员工本体，TalentFlow 是其 skill backend。
    TalentFlow 不负责模型选择、API key、base_url、prompt、memory。

正确主路径：
    Step A) python pipelines/process_local_folder.py ./resumes --jd ./jd.json
            → 生成 runs/run_xxx/batch_input.json

    Step B) HuntMind 读取 batch_input.json，自主做招聘判断
            → 生成 runs/run_xxx/huntmind_output.json

    Step C) python scripts/validate_model_output.py runs/run_xxx/batch_input.json runs/run_xxx/huntmind_output.json

    Step D) python scripts/finalize_report.py runs/run_xxx runs/run_xxx/huntmind_output.json

    Step E) python scripts/quality_gate.py runs/run_xxx/final_output.json

    完整文档见：SKILL.md 或 README.md

如需本地开发测试 evaluators，请参考 scripts/ 目录中的独立工具。
"""
