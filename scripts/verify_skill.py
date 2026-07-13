#!/usr/bin/env python3
"""Run deterministic offline contract checks for commit-and-push."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SECRET_NAME_PATTERNS = (
    re.compile(r"^\.env(?:\..+)?$"),
    re.compile(r"^(?:id_rsa|id_ed25519|credentials\.json|service-account\.json)$"),
    re.compile(r".*\.(?:pem|p12|pfx|key)$"),
    re.compile(r"(?i).*(?:credential|private[-_]?key|secret|token|password).*$"),
)
SECRET_CONTENT_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|authorization|bearer)\s*[:=]?\s*['\"]?[A-Za-z0-9_./+\-=]{12,}"),
    re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,})"),
    re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
)
JUNK_PATTERNS = ("*.pyc", "*.log", ".DS_Store")


def run(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], check=check, text=True, capture_output=True)


def init_repo(path: Path, with_commit: bool = True) -> None:
    run(path, "init", "-q")
    run(path, "config", "user.name", "Fixture Bot")
    run(path, "config", "user.email", "fixture@example.invalid")
    if with_commit:
        (path / "README.md").write_text("fixture\n", encoding="utf-8")
        run(path, "add", "README.md")
        run(path, "commit", "-q", "-m", "chore(test): initialize fixture")
        run(path, "branch", "-M", "main")


def result(name: str, passed: bool, evidence: str) -> dict[str, str]:
    return {"name": name, "status": "pass" if passed else "fail", "evidence": evidence}


def is_secret(path: Path) -> bool:
    if any(pattern.match(path.name) for pattern in SECRET_NAME_PATTERNS):
        return True
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")[:1_000_000]
    except OSError:
        return False
    return any(pattern.search(content) for pattern in SECRET_CONTENT_PATTERNS)


def is_junk(path: Path) -> bool:
    return path.is_file() and any(path.match(pattern) for pattern in JUNK_PATTERNS)


def staged_paths(repo: Path) -> list[str]:
    output = run(repo, "diff", "--cached", "--name-only").stdout
    return [line for line in output.splitlines() if line]


def verify_dirty_worktree(root: Path) -> dict[str, str]:
    repo = root / "dirty"
    repo.mkdir()
    init_repo(repo)
    (repo / "README.md").write_text("fixture\nchanged\n", encoding="utf-8")
    (repo / "feature.py").write_text("print('ok')\n", encoding="utf-8")
    status = run(repo, "status", "--porcelain").stdout.splitlines()
    return result("dirty_worktree", status == [" M README.md", "?? feature.py"], repr(status))


def verify_first_commit(root: Path) -> dict[str, str]:
    repo = root / "first"
    repo.mkdir()
    init_repo(repo, with_commit=False)
    count = run(repo, "rev-list", "--count", "HEAD", check=False)
    return result("first_commit", count.returncode != 0, f"rev-list exit={count.returncode}")


def verify_secret_guard(root: Path) -> dict[str, str]:
    repo = root / "secret"
    nested = repo / "config"
    nested.mkdir(parents=True)
    init_repo(repo)
    files = {
        repo / ".env.local": "API_KEY=abcdefghijklmnop\n",
        nested / "service-account.json": "{}\n",
        nested / "notes.txt": "client_secret = abcdefghijklmnop\n",
        nested / "password.txt": "not-used-for-detection\n",
        nested / "jwt.txt": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abcdefghijklmnop\n",
        nested / "safe.txt": "public documentation\n",
    }
    for path, content in files.items():
        path.write_text(content, encoding="utf-8")
    run(repo, "add", "config/notes.txt")
    detected = sorted(str(path.relative_to(repo)) for path in files if is_secret(path))
    staged_secrets = sorted(path for path in staged_paths(repo) if is_secret(repo / path))
    expected = [".env.local", "config/jwt.txt", "config/notes.txt", "config/password.txt", "config/service-account.json"]
    passed = detected == expected and staged_secrets == ["config/notes.txt"]
    return result("secret_guard", passed, f"detected={detected}; staged={staged_secrets}")


def verify_sync_only(root: Path) -> dict[str, str]:
    remote = root / "remote.git"
    remote.mkdir()
    run(remote, "init", "--bare", "-q")
    first = root / "sync-a"
    first.mkdir()
    init_repo(first)
    run(first, "remote", "add", "origin", str(remote))
    run(first, "push", "-q", "-u", "origin", "main")
    second = root / "sync-b"
    run(root, "clone", "-q", str(remote), str(second))
    run(second, "config", "user.name", "Fixture Bot")
    run(second, "config", "user.email", "fixture@example.invalid")
    (first / "local.txt").write_text("local\n", encoding="utf-8")
    run(first, "add", "local.txt")
    run(first, "commit", "-q", "-m", "feat(local): add local change")
    (second / "remote.txt").write_text("remote\n", encoding="utf-8")
    run(second, "add", "remote.txt")
    run(second, "commit", "-q", "-m", "feat(remote): add remote change")
    run(second, "push", "-q")
    run(first, "fetch", "-q", "origin")
    counts = run(first, "rev-list", "--left-right", "--count", "HEAD...@{upstream}").stdout.strip()
    porcelain = run(first, "status", "--porcelain").stdout
    passed = counts == "1\t1" and porcelain == ""
    return result("sync_only", passed, f"divergence={counts}; clean={porcelain == ''}")


def verify_untracked_junk(root: Path) -> dict[str, str]:
    repo = root / "junk"
    repo.mkdir()
    init_repo(repo)
    tracked = repo / "debug.log"
    tracked.write_text("junk\n", encoding="utf-8")
    run(repo, "add", "debug.log")
    run(repo, "commit", "-q", "-m", "chore(test): add tracked junk")
    (repo / ".DS_Store").write_text("junk\n", encoding="utf-8")
    (repo / "cache.pyc").write_bytes(b"junk")
    candidates = sorted(path.name for path in repo.iterdir() if is_junk(path))
    run(repo, "rm", "--cached", "--", "debug.log")
    retained = tracked.exists() and "debug.log" in staged_paths(repo)
    passed = candidates == [".DS_Store", "cache.pyc", "debug.log"] and retained
    return result("untracked_junk", passed, f"candidates={candidates}; retained={retained}")


def verify_structure() -> list[dict[str, str]]:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    return [
        result("skill_name", bool(re.search(r"(?m)^name: commit-and-push$", skill)), "frontmatter name"),
        result("no_private_paths", not bool(re.search(r"/Users/[^/]+/|[A-Za-z]:\\\\Users\\\\", skill)), "SKILL.md path scan"),
        result("explicit_activation", "Never invoke this skill proactively" in skill, "activation boundary"),
        result("readme_install", "npx skills add d0ublecl1ck/commit-and-push" in readme, "install command"),
    ]


def build_report() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="commit-and-push-") as temp:
        root = Path(temp)
        cases = [
            verify_dirty_worktree(root),
            verify_first_commit(root),
            verify_secret_guard(root),
            verify_sync_only(root),
            verify_untracked_junk(root),
        ]
    structure = verify_structure()
    status = "pass" if all(item["status"] == "pass" for item in cases + structure) else "fail"
    return {"status": status, "cases": cases, "structure": structure}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for group in ("structure", "cases"):
            print(f"[{group}]")
            for item in report[group]:
                print(f"{item['status'].upper():4} {item['name']}: {item['evidence']}")
        print(f"\nResult: {report['status'].upper()}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
