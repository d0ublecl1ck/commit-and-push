# Commit&Push

A reusable skill for committing and pushing repo changes with one canonical set of commit rules.

## What it does

- Runs pre-checks in parallel: `git status`, `git diff`, `git log --oneline -5`
- Detects sync-only states and handles them with `git pull --rebase` plus `git push`
- Always stages all changes, including untracked files, with `git add -A`
- Drafts Conventional Commit messages with required `type(scope): subject`
- Uses HEREDOC commit messages and adds bodies for non-trivial changes
- Re-commits when pre-commit hooks modify files
- Pushes automatically after a successful commit
- Supports optional PR creation with `gh` when explicitly requested

## When to use

Use when you want the agent to commit changes, or commit and push changes, without extra confirmation while keeping commit messages disciplined and consistent.

## How to trigger

Use natural language such as:

- `commit and push all files without asking`
- `帮我写一个规范的 commit message`
- `直接提交并推送当前全部改动`

Mentioning `Commit&Push` explicitly also triggers this skill.

## Safety notes

- Never modifies git config
- Never uses interactive git commands
- Never commits secrets or sensitive local artifacts
- Creates PRs with `gh` only when explicitly requested
