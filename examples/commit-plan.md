# Commit Plan Example

This example shows the visible plan that should appear before staging. Every path
is labeled with its provenance, and paths from other sessions or unknown origins
are excluded unless the user selects them.

## Worktree

```text
 M README.md
 M src/validation.ts
 M tests/validation.test.ts
 M src/unrelated.ts
?? .env
?? debug.log
```

## Plan

```text
Commit 1 — feat(validation): add URL validation            [current session]
  src/validation.ts
  tests/validation.test.ts

Commit 2 — docs(readme): document validation behavior      [current session]
  README.md

Not selected (other / unknown)
  src/unrelated.ts — other session; excluded unless you select it

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
  Not selected: src/unrelated.ts (other session)
  Blocked: .env
  Local-only: debug.log
```

The exact SHAs vary. The grouping, provenance labels, scope selection, blocked-file
behavior, and per-repository push summary are the contract.
