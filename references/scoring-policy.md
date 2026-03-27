# Scoring Policy

HuntMind outputs the raw 7-dimension judgment.
The process layer normalizes, weights, and finalizes the score.

## Model Responsibility

HuntMind should output:
- `structured_score.dimension_scores`
- `structured_score.dimension_evidence`
- decision, reasons, risks, and action fields

## Process Responsibility

The process layer:
- selects one of the 5 fixed templates
- applies industry adjustments when configured
- recomputes `weighted_total`
- derives legacy `score_breakdown`
- applies gates for priority control

## Fixed Templates

- `product_manager`
- `rd_engineer`
- `ops_manager`
- `sales_director`
- `hr_director`

## Gate Rules

- `hard_skill_match < 50` blocks `A`
- `willingness < 40` blocks `A`
- `experience_depth < min_experience_for_a` blocks `A`

## Important Boundary

Template rules and routing hints belong to the paid enhancement layer boundary.
The local process code may consume a local stub, but it does not own those rules long-term.
