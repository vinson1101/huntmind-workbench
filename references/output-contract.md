# Output Contract

HuntMind output must be valid JSON and must include:

- `overall_diagnosis`
- `top_recommendations`
- `batch_advice`

Each recommendation must include:

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

`structured_score` is the preferred score container.

## structured_score

Expected fields:
- `template_id`
- `dimension_scores`
- `dimension_evidence`
- optional `weight_snapshot`
- optional `weighted_total`

Valid template ids are currently:
- `product_manager`
- `rd_engineer`
- `ops_manager`
- `sales_director`
- `hr_director`

Old template ids such as `senior_product_complex` are no longer canonical.
