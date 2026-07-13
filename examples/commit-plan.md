# Commit Plan Example

This example shows the visible plan that should appear before staging.

## Worktree

```text
 M README.md
 M src/validation.ts
 M tests/validation.test.ts
?? .env
?? debug.log
```

## Plan

```text
Commit 1 — feat(validation): add URL validation
  src/validation.ts
  tests/validation.test.ts

Commit 2 — docs(readme): document validation behavior
  README.md

Ignored
  debug.log — local runtime artifact; add the narrowest shared ignore rule

Blocked
  .env — secret-like file; never stage without explicit approval
```

## Expected outcome

```text
Repository: example-app
  a1b2c3d feat(validation): add URL validation
  d4e5f6a docs(readme): document validation behavior
  Pushed: origin/feature/url-validation
  Blocked: .env
  Local-only: debug.log
```

The exact SHAs vary. The grouping, blocked-file behavior, and per-repository push summary are the contract.
