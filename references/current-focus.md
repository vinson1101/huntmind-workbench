# 当前阶段目标

## 状态
- 主链路已通（batch_input → validate → sanitize → report → quality_gate）
- 已完成 P4 质量门禁重构
- 已完成 P5 7维评分体系落地

---

## 当前阶段：校准阶段

**只做三件事：**

1. **修 core_judgement 分数与 total_score 同步**
   - core_judgement 中的数字必须与最终 total_score 一致，或直接不写具体分数
   - 禁止出现"综合评分82分"但 total_score=56 的严重脱节

2. **复核模板选择逻辑**
   - 当前几乎所有候选人都命中 senior_product_complex
   - 需考虑 candidate_role 对模板选择的影响（如 transition_to_product 的优先级）
   - 下一步再优化，非当前优先

3. **用固定 12 人样本和 HR 判断对齐**
   - 回归集已沉淀：`evals/golden_set/product_manager_batch_001/`
   - 包含：jd.json、batch_input.json、huntmind_output.json、final_output.json、12份PDF
   - 后续所有改动先跑这套黄金集，对照 expected_review.md 验证

---

## 当前不做

- ❌ backfill
- ❌ 演示/评分算法
- ❌ 再改 batch_input / validate / runner 主流程
- ❌ 临时对话记忆推进，所有结论必须落文件

---

## 回归测试标准

每次改动后，用回归集跑 pipeline，验证：

| 检查项 | 预期 |
|--------|------|
| Top3 是否为 邢威峰/李蓓/孙铜 | ✅ |
| A 档是否包含上述6人 | ✅ |
| 张金莎/许罗栋/滕锋帅/杨淑婷 是否不在 A | ✅ |
| dimension_evidence 是否为真实内容 | ✅ |
| 12人分数是否各不相同 | ✅ |
| action_timing 是否按 decision 区分 | ✅ |
| quality_score 是否 ≥ 85 | ✅ |

---

*最后更新：2026-03-23*
