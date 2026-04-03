---
name: Commit&Push
description: Strict workflow and safety constraints for committing and pushing all changes without confirmation, while drafting Conventional Commit messages with required type and scope, HEREDOC bodies, hook handling, sync-only detection, and optional PR creation via gh when explicitly requested. This skill is opt-in only and must never be invoked proactively; use it only when the user explicitly asks to use Commit&Push or explicitly requests commit and push execution.
---

# Commit&Push

Commit all repo changes, write a proper Conventional Commit message, and push safely.

## Activation Boundary (hard rule)

- This skill is opt-in only
- Never invoke this skill proactively, implicitly, by default, or because it seems helpful
- Use this skill only when the user explicitly requests `Commit&Push` or explicitly instructs the agent to commit and push changes
- If the user asks only for code changes, review, debugging, planning, or implementation, do not use this skill
- Do not reinterpret vague shipping intent as permission to use this skill; require an explicit user request for commit and push execution

## Workflow (order is mandatory)

0) **No questions unless exceptional**
- Do not ask the user any questions
- Proceed autonomously unless an error or exceptional condition occurs

0.5) **Detect single-repo vs multi-repo workspace**
- Before any git action, determine whether the current workspace is a single Git repository or a workspace containing multiple independent Git repositories
- If the current workspace matches this multi-repo layout, do not run one combined root-level git workflow:
  - `openspec`: `/Users/d0ublecl1ck/evaluation/openspec`
  - `evaluation_admin`: `/Users/d0ublecl1ck/evaluation/evaluation_admin`
  - `evaluation_server`: `/Users/d0ublecl1ck/evaluation/evaluation_server`
- In that multi-repo layout, run the full Commit&Push workflow separately for each repository
- Treat each repository as an independent unit for pre-checks, staging, commit, hook handling, pull/rebase, push, and failure handling
- Summarize status and outcome per repository

1) **Pre-commit checks (must run in parallel)**
- Run in parallel: `git status`, `git diff`, `git log --oneline -5`
- Summarize results before proceeding
- If `git status --short --branch` shows both `ahead` and `behind` (e.g., `master...origin/master [ahead 1, behind 1]`), `git diff` is empty, `git log --oneline -5` is non-empty (not first commit), and `git status` reports `nothing to commit, working tree clean`, treat this as a sync-only state
- In sync-only state, run `git pull --rebase` first, then `git push`; do not create a new commit

2) **First commit special rule**
- If `git log --oneline -5` is empty or reports no commits (e.g., `fatal: your current branch ... does not have any commits yet`), treat this as the first commit
- For the first commit, do not ask the user for requirements; inspect current changes and project context and create the initial commit

3) **Commit all files without confirmation**
- Never ask the user which files to commit
- Always commit all changes, including untracked files (`git add -A`)
- Do not create empty commits
- Never commit `.env`, credentials, secrets, `node_modules/`, `__pycache__/`, `.venv/`, or large binary files without explicit approval

4) **Draft the commit message before commit**
- Use Conventional Commits format: `type(scope): subject`
- Scope is required and must be kebab-case
- Subject must use present-tense imperative wording, state what changed, avoid vague phrasing, and end without a period
- Keep the subject concise and preferably within 50 characters after the colon
- Use a HEREDOC for every commit message, including simple commits
- Add a body for non-trivial changes to explain how and why
- Use git trailers when they materially help, such as `Fixes #N`, `Closes #N`, or `Co-authored-by: Name <email>`
- For breaking changes, use `type(scope)!: subject` or add a `BREAKING CHANGE:` footer
- Never include signature lines such as `Generated with ...` or `Co-Authored-By: Claude ...`

5) **Commit**
- Draft the message yourself from the diff, not from filenames alone
- Use one focused commit per repository for the current batch of changes
- If commit fails due to large files or policy limits, stop and ask the user for instructions before proceeding

6) **Handle pre-commit changes**
- If pre-commit hooks modify files, stage the modified files and create a replacement commit that includes those changes
- Reuse the same commit intent while updating the body if the hook materially changed behavior

7) **Auto push after successful commit**
- Automatically push to the tracked remote branch after a successful commit
- If no upstream is configured, push with `-u origin <current-branch>`
- If the remote branch is ahead of local, prefer `git pull --rebase` before retrying push
- If push fails, treat it as an exceptional condition and ask the user for instructions

## Commit message conventions

### Types

| Type | Purpose |
|------|---------|
| `feat` | New feature or functionality |
| `fix` | Bug fix or issue resolution |
| `refactor` | Code refactoring without behavior change |
| `perf` | Performance improvements |
| `test` | Test additions or modifications |
| `ci` | CI/CD configuration changes |
| `docs` | Documentation updates |
| `chore` | Maintenance, dependencies, tooling |
| `style` | Code formatting or lint-only changes |
| `security` | Security fixes or hardening |

### Scope

- Always include a scope in parentheses
- Use concise kebab-case nouns such as `auth`, `api`, `config`, `tests`, `validation`, or `cookie-service`

### Subject

- Use imperative verbs such as `add`, `fix`, `refactor`, `remove`, `improve`, `prevent`, or `implement`
- Describe the concrete change, not a generic intention
- Do not use vague subjects like `update code`, `fix bug`, `make changes`, or `add stuff`

### Body

- Leave one blank line after the subject
- Explain how the change works and why it was made
- Use short bullet points when multiple details need to be grouped
- Wrap lines reasonably, around 72 characters when practical
- Add task, requirement, or review-comment references only when they add useful traceability

### Examples

Good:

```text
feat(validation): add URLValidator with domain whitelist
fix(auth): use hmac.compare_digest for key comparison
refactor(template): consolidate filename sanitization
test(security): add path traversal prevention tests
```

Bad:

```text
update validation code
feat: add stuff
fix(auth): fix bug
chore: make changes
feat(security): improve things.
```

## Commit message templates

### Simple commit

```bash
git commit -m "$(cat <<'EOF'
fix(auth): use hmac.compare_digest for key comparison
EOF
)"
```

### Complex commit

```bash
git commit -m "$(cat <<'EOF'
feat(validation): add URLValidator with domain whitelist

Implement URLValidator class supporting:
- Domain whitelist enforcement for supported domains
- Dangerous scheme blocking for unsafe inputs
- URL parsing with embedded credentials handling

Addresses Requirement 31: Input validation
Part of Task 5.1: Input Validation Utilities
EOF
)"
```

### Review-comment follow-up

```bash
git commit -m "$(cat <<'EOF'
fix(api): address review comment on retry handling

Tighten retry classification so only transient failures retry.
Addresses review comment #123456789.
EOF
)"
```

## Branching and PRs (only if user explicitly requests a PR)

- Before creating a PR, check current branch status and diffs
- PR description must include `Summary` and `Test plan`
- Create PRs with `gh` only; do not change git config
- Reuse commit bodies as source material for the PR description when helpful

Example:

```bash
gh pr create --title "feat(security): implement input validation" --body "$(cat <<'EOF'
## Summary
- Add input validation utilities and security hardening
- Prevent path traversal in template processing
- Improve API key authentication handling

## Test plan
- Run project test suite
- Verify security regression coverage
EOF
)"
```

## Safety constraints (hard rules)

- Never update any git config
- Never run interactive git commands such as `rebase -i`
- Never create empty commits unless the user explicitly requests one

## References

- `references/commit_examples.md` for extended examples by type
