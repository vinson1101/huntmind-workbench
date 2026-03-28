# Judge

这个目录只放一个固定裁判脚本，用来判断某次规则修改后系统有没有变好。

它做的事情很简单：

1. 读取固定测试集
2. 用当前版本 runner 重新收敛输出
3. 和参考标签对比
4. 计算固定指标
5. 输出一个清晰结论

## 运行方式

```bash
python -m evals.judge.run_judge --config evals/judge/config.json
```

## 默认支持的 4 类测试

- `product`
- `frontend_dev`
- `blockchain_lead`
- `sales_director`

其中：

- `product` 优先复用现有 `evals/golden_set/product_manager_batch_001`
- 其余 3 类先走脚本内置 fixture，避免要求手工迁目录

## 输出结果

结果默认写到：

```text
evals/results/<timestamp>/
```

每个 batch 会产出：

- `final_output.json`
- `compare.json`
- `summary.json`

全局会产出：

- `report.json`

## 重点看什么

- `contact_accuracy`
- `top3_hit_rate`
- `priority_accuracy`
- `false_positive_rate`
- `reason_accuracy`
- 4 个硬错误数量

## 当前限制

- 这个脚本是裁判，不会自动 patch 代码
- `product_manager_batch_001` 当前人工标签仍是初始草稿，结果只能用于趋势判断，不能当最终真值
- 其余 3 类当前是内置小样本 fixture，后续可以逐步替换成正式 batch
