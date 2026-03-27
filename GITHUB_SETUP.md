# GitHub Repository Notes

## Intended Repository Name

- repository name: `huntmind-workbench`
- owner: `vinson1101`
- local worktree: `D:\code project\huntmind-workbench`

## Current State

- the local project name has been changed to `huntmind-workbench`
- the GitHub repository may still be using the old `talentflow` name
- update `origin` after the GitHub-side rename is complete

## After GitHub Rename

```bash
git remote set-url origin <new-repo-url>
git remote -v
```

## Positioning

This repository is the HuntMind engineering workbench.

It is not the HuntMind agent itself, and it is not equal to the `TalentFlow` skill.

## Internal Boundary

- `HuntMind`: agent and decision owner
- `TalentFlow`: process skill
- `Paid enhancement layer`: taxonomy, routing, hints, and decision boosts
