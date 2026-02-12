# Commit&Push

A reusable agent skill that enforces a strict, safe workflow for committing and pushing all repo changes.

## What it does

- Runs pre-checks in parallel: `git status`, `git diff`, `git log --oneline -5`
- Always stages all changes (including untracked files) with `git add -A`
- Writes commit messages via HEREDOC (no signatures)
- Re-commits when pre-commit hooks modify files
- Pushes automatically after a successful commit
- Handles sync-only states (clean tree but branch ahead/behind) via `git pull --rebase` + `git push`

## When to use

Use when you want your agent to commit and push all current changes without extra confirmation, while following strict safety constraints.

## How to trigger

Use natural language such as:

- `commit and push all files without asking`
- `直接提交并推送当前全部改动`

Mentioning `Commit&Push` explicitly also triggers this skill.

## Installation

Place this folder under your agent skills directory, for example:

```bash
cp -R commit-and-push <your-agent-skills-dir>/
```

## Safety notes

- Never modifies git config
- Never uses interactive git commands
- Creates PRs with `gh` only when explicitly requested
