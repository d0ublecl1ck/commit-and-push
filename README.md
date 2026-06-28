# Commit&Push

A reusable skill for committing and pushing repo changes with one canonical set of commit rules.

## What it does

- Runs pre-checks in parallel: `git status`, `git diff`, `git log --oneline -5`
- Detects sync-only states and handles them with `git pull --rebase` plus `git push`
- Groups changes by conversation round — each distinct user request gets its own commit instead of one giant commit
- Stages only the files belonging to each round, not blindly `git add -A` everything
- Drafts Conventional Commit messages with required `type(scope): subject`
- Uses HEREDOC commit messages and adds bodies for non-trivial changes
- Re-commits per round when pre-commit hooks modify files
- Pushes once after all round commits succeed
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
