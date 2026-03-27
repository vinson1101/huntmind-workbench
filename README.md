# huntmind-workbench

`huntmind-workbench` is the engineering workbench around HuntMind.

It is not the HuntMind agent itself. HuntMind remains the decision-making agent with its own soul, identity, memory, and orchestration.

## Boundary

- `HuntMind`: agent and decision owner
- `TalentFlow`: one process skill inside this workbench
- `Paid enhancement layer`: owner of taxonomy, template rules, routing hints, and customer-specific decision boosts

## Current Shape

This repository is `single repo, multi-skill`.

Current modules:
- `skills/talentflow`: resume ingestion, normalization, batch building, validation, finalization
- `references/`: decision contracts and output constraints
- `evals/`: calibration and regression assets
- `enhancement/`: temporary local stubs for the future paid enhancement layer

Planned modules:
- `skills/search`

## TalentFlow Skill

`TalentFlow` is a workflow skill, not an enhancement service.

It is responsible for:
- reading resumes from local or temporary folders
- parsing and normalizing candidate data
- building `batch_input.json`
- validating and sanitizing HuntMind outputs
- generating `final_output.json`, `quality_meta.json`, `final_report.md`, and `owner_summary.md`

It does not own:
- company industry classification
- JD to 5-template routing ownership
- taxonomy / template / hints authority
- agent memory or learning logic
- model ownership

## Enhancement Layer

The future paid enhancement layer is separate from `TalentFlow`.

Its job is to provide:
- better company and JD classification
- stronger routing and hit accuracy
- taxonomy and template rule access
- decision hints and customer-specific boosts

The local files under `enhancement/` are only temporary stubs for interface shaping. They do not mean those capabilities belong to `TalentFlow`.

## Repository Rename

The local worktree now uses the name `huntmind-workbench`.

If the GitHub repository is still named `talentflow`, update the remote later with:

```bash
git remote set-url origin <new-repo-url>
```
