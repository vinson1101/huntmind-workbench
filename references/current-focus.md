# Current Focus

## Immediate Goal

Enter the pre-production debt-paydown phase.

## P0: Template Balance

Fix routing imbalance so the 5 fixed templates stay distinct:

- `product_manager`
- `rd_engineer`
- `ops_manager`
- `sales_director`
- `hr_director`

What matters now:
- keep template boundaries explicit
- avoid product/general swallowing unrelated JDs
- maintain a manual `JD -> template` calibration set
- inspect route evidence, not just final template ids

Supporting assets:
- `evals/template_routing_gold.jsonl`
- `scripts/template_route_stats.py`
- `configs/scoring_templates.yaml`

## P1: Enhancement-Layer Interface Shaping

Do not scatter-read taxonomy, template rules, or decision hints across process code.

Current temporary shape:
- `enhancement/local_provider.py`

This is only a local stub for the future paid enhancement layer.
It does not make those capabilities part of `TalentFlow`.
