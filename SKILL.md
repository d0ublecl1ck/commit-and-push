---
name: commit-and-push
description: Safely group intended repository changes into auditable Conventional Commits and push them. Use only when the user explicitly asks to use `commit-and-push` or `cap`, or explicitly instructs the agent to commit and push. Covers dirty worktrees, multiple repositories, first commits, sync-only branches, hooks, ignore rules, secrets, upstream setup, and optional PR creation. Do not use for code changes, review, debugging, planning, vague shipping intent, commit-message drafting alone, or commit-only requests.
---

# commit-and-push

Turn the current conversation's intended changes into focused Conventional Commits, then push them safely.

## Activation Boundary (hard rule)

- This skill is opt-in only.
- Never invoke this skill proactively, implicitly, by default, or because it seems helpful.
- Use it only when the user explicitly asks to use `commit-and-push` or `cap`, or explicitly instructs the agent to commit and push.
- A request to draft a commit message, commit without push, ship vaguely, review, debug, plan, or implement does not activate this skill.
- A confirmation question such as “ready?” or “is everything done?” is not execution permission.

## Safety Invariants

- Never change Git configuration outside disposable verification fixtures.
- Never use destructive commands such as `git reset --hard`, `git clean -fd`, or force push unless the user explicitly authorizes that exact action.
- Never use interactive Git commands such as `git rebase -i`.
- Never commit `.env`, credentials, private keys, tokens, cookies, `node_modules/`, `.venv/`, `__pycache__/`, or large binaries without explicit approval.
- Never overwrite, revert, or discard changes that were not produced by the current task.
- Never create an empty commit unless explicitly requested.
- Create a PR only when explicitly requested.

## Mandatory Workflow

### 1. Discover repository boundaries

Before any staging or commit:

1. Determine whether the current workspace is one repository, a worktree, or a directory containing multiple independent repositories.
2. Discover repositories from Git metadata; do not rely on machine-specific absolute paths or hard-coded project names.
3. Treat each repository independently for status checks, staging, hooks, synchronization, commits, and push outcomes.
4. If repository ownership is ambiguous, stop and ask which repositories are in scope.

### 2. Run preflight checks in parallel

For every repository, run these read-only checks in parallel:

```bash
git status --short --branch
git diff --stat && git diff
git diff --cached --stat && git diff --cached
git log --oneline -5
git remote -v
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}'
```

The upstream query may fail when no upstream exists; record that state instead of treating it as a fatal error.

Summarize before changing the index:

- repository and branch;
- tracked, staged, and untracked changes;
- upstream and ahead/behind state;
- likely conversation-round groups;
- files blocked by safety rules.

### 3. Classify exceptional states

#### First commit

If `git log --oneline -5` reports no commits, inspect all intended files and create the initial commit without asking routine questions.

#### Sync-only

Treat a repository as sync-only only when all are true:

- the worktree and index are clean;
- upstream is ahead and local has no unpublished commits;
- the repository already has commits.

Run `git fetch`, verify divergence with `git rev-list --left-right --count HEAD...@{upstream}`, then use `git pull --ff-only` and `git push`; do not create a new commit. If both sides have commits, classify the state as diverged rather than sync-only and ask before rebasing.

#### No changes

If there are no intended changes and the branch is already synchronized, report “nothing to commit or push” and stop without an empty commit.

#### Detached HEAD or unresolved conflicts

Stop and report the exact state. Do not invent a branch, resolve conflicts, or push from detached HEAD without user direction.

### 4. Build a commit plan

Review conversation history and map changed files to the user request or conversation round that caused them.

- One distinct change-producing round is one commit unit.
- If one file was modified across rounds, assign it to the latest round that modified it.
- If conversation provenance is unavailable, group by coherent intent visible in the diff.
- Keep unrelated changes separate even when they live in the same repository.
- Do not use `git add -A` across all groups.

Before staging, present a concise plan:

```text
Commit 1 — feat(validation): add URL validation
  src/validation.ts
  tests/validation.test.ts

Commit 2 — docs(readme): document validation behavior
  README.md

Blocked
  .env — secret-like file; never stage without explicit approval
```

Proceed autonomously after the plan unless an exceptional condition or ambiguous file ownership requires a question.

### 5. Guard secrets and local junk

Inspect untracked and staged files before every commit unit.

Local-only junk includes `.DS_Store`, `*.pyc`, `__pycache__/`, editor swaps, temporary logs, coverage output, build caches, and local virtual environments.

- Add the narrowest appropriate pattern to a repository `.gitignore` when the rule should be shared.
- Use `.git/info/exclude` only for deliberately machine-local exclusions.
- If a junk file is already tracked, show the exact path, add its ignore rule, then use `git rm --cached -- <path>` and verify the local file still exists before committing. Never use plain `git rm` for this case.
- Commit shared ignore-rule changes with the conversation round that exposed the junk.
- Never auto-ignore source, assets, fixtures, migrations, lockfiles, or ownership-ambiguous files.

Secret-like files are blocked, not merely ignored. Stop and ask if the user explicitly wants one committed.

### 6. Stage and commit each unit

For each commit unit, in chronological order:

1. Stage only that unit's intended paths.
2. Inspect `git diff --cached --stat` and `git diff --cached`.
3. Confirm no blocked file or unrelated hunk is staged.
4. Draft the message from the staged diff.
5. Commit with a HEREDOC.

Commit message contract:

- Format: `type(scope): subject`.
- Scope is required and kebab-case.
- Subject is present-tense imperative, concrete, concise, and has no trailing period.
- Add a body for non-trivial changes to explain how and why.
- Use trailers only when they add traceability.
- Use `!` or `BREAKING CHANGE:` for breaking changes.
- Never add generated-by signatures or synthetic co-author lines.

```bash
git commit -m "$(cat <<'EOF'
fix(auth): use constant-time key comparison

Replace direct equality to avoid timing differences when checking API keys.
EOF
)"
```

If a hook modifies files, inspect those edits, restage only files belonging to the same unit, and retry that unit. If a hook introduces unrelated or unsafe changes, stop and report them.

### 7. Synchronize and push

After all commit units in a repository succeed:

1. Run `git fetch` and re-check the worktree, index, upstream, and exact divergence with `git rev-list --left-right --count HEAD...@{upstream}`.
2. If the worktree or index contains unexpected changes, stop before synchronization.
3. If upstream is ahead and local has no unpublished commits, run `git pull --ff-only`.
4. If both sides have commits, do not rewrite local history automatically. Report the divergence and ask before any rebase.
5. Push once to the tracked branch after synchronization is safe.
6. If no upstream exists, use `git push -u origin <current-branch>`.
7. Never force push implicitly.

A push failure is exceptional: report the command, error, committed local SHAs, and unpushed branch; then ask what to do.

### 8. Report outcomes

Summarize per repository:

- commit SHA and subject for each unit;
- pushed branch and remote;
- skipped, blocked, or uncommitted files;
- hook, rebase, or push exceptions.

## Optional Pull Request

Only when the user explicitly requests a PR:

1. Verify GitHub CLI authentication and current branch state.
2. Reuse an existing open PR for the branch when appropriate.
3. Otherwise create one with `gh pr create`.
4. Include `## Summary` and `## Test plan`.
5. Do not merge, tag, release, or deploy without separate explicit authorization.

## References

- `references/commit_examples.md` — extended Conventional Commit examples.
- `examples/commit-plan.md` — a visible before/after commit plan.
- `scripts/verify_skill.py` — deterministic offline fixture verification.
