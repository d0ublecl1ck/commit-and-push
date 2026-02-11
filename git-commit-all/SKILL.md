---
name: git-commit-all
description: Strict workflow and safety constraints for "commit all files without asking for confirmation." Use when the user wants to commit all changes, run parallel pre-checks (git status / git diff / git log --oneline -5), write commit messages via HEREDOC, avoid signing/pushing/config changes, handle untracked files and pre-commit modifications, and optionally create a PR via gh only when explicitly requested.
---

# Git Commit All

## Workflow (order is mandatory)

0) **No questions unless exceptional**
- Do not ask the user any questions
- Proceed autonomously unless an error or exceptional condition occurs

1) **Pre-commit checks (must run in parallel)**
- Run in parallel: `git status`, `git diff`, `git log --oneline -5`
- Summarize results before proceeding

2) **First commit special rule**
- If `git log --oneline -5` is empty or reports no commits (e.g., `fatal: your current branch ... does not have any commits yet`), treat this as the first commit
- For the first commit, do not ask the user for requirements; inspect current changes and project context and create the initial commit

3) **Commit all files without confirmation**
- Never ask the user which files to commit
- Always commit all changes, including untracked files (`git add -A`)
- Do not create empty commits

4) **Commit**
- Use HEREDOC for the commit message
- Commit message must include a concrete summary of changes
- Draft the commit message yourself based on the diff and follow the commit message convention
- Never include any signature lines:
  - `Generated with [Claude Code](https://claude.ai/code)`
  - `Co-Authored-By: Claude <noreply@anthropic.com>`
- If commit fails due to large files (e.g., file-size limits on local/remote policies), stop and ask the user for instructions before proceeding

5) **Handle pre-commit changes**
- If pre-commit hooks modify files, re-commit to include those changes

6) **Auto push after successful commit**
- Automatically push to the tracked remote branch after a successful commit
- If no upstream is configured, push with `-u origin <current-branch>`
- If push fails, treat it as an exceptional condition and ask the user for instructions

## Safety constraints (hard rules)

- Never update any git config
- Never run interactive git commands (e.g., `rebase -i`)

## Branching and PRs (only if user explicitly requests a PR)

- Before creating a PR, check current branch status and diffs
- PR description must include `Summary` and `Test plan`
- Create PRs with `gh` only; do not change git config

## Commit message example

```
feat(course): Improve course learning page update and navigation
- Handle missing update manager in WeChat mini-programs while keeping failure prompts
- Revise course navigation button copy and styles; add previous/next for pinyin/Chinese courses
- Auto-expand fill-in answers after completion; remove redundant "view" button
- Refine rounded corner visuals on option labels
```
