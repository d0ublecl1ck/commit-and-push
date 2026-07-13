from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
README = ROOT / "README.md"


class SkillContractTests(unittest.TestCase):
    def test_public_files_exist(self) -> None:
        required = [
            ROOT / "LICENSE",
            ROOT / "examples" / "commit-plan.md",
            ROOT / "examples" / "install-check.txt",
            ROOT / "scripts" / "verify_skill.py",
            ROOT / ".github" / "workflows" / "verify.yml",
            ROOT / ".claude-plugin" / "marketplace.json",
        ]
        self.assertEqual([], [str(path.relative_to(ROOT)) for path in required if not path.exists()])

    def test_skill_has_consistent_name_and_explicit_activation(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^name: commit-and-push$")
        self.assertIn("explicitly asks to use `commit-and-push` or `cap`", text)
        self.assertIn("Never invoke this skill proactively", text)

    def test_skill_contains_no_private_absolute_paths(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"/Users/[^/]+/")
        self.assertNotRegex(text, r"[A-Za-z]:\\Users\\")

    def test_readme_matches_activation_boundary(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("npx skills add d0ublecl1ck/commit-and-push", text)
        self.assertIn("只有明确要求 `commit and push`、`提交并推送` 或 `cap` 才会触发", text)
        self.assertNotIn("Mentioning `Commit&Push` explicitly also triggers", text)
        self.assertIn("## 安全边界", text)
        self.assertIn("## 验证与测试", text)

    def test_marketplace_manifest_is_valid(self) -> None:
        data = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual("commit-and-push", data["name"])
        self.assertTrue(data["plugins"])


class GitFixtureTests(unittest.TestCase):
    def git(self, repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            check=check,
            text=True,
            capture_output=True,
        )

    def test_verifier_covers_dirty_sync_and_secret_scenarios(self) -> None:
        result = subprocess.run(
            ["python3", str(ROOT / "scripts" / "verify_skill.py"), "--json"],
            check=True,
            text=True,
            capture_output=True,
        )
        report = json.loads(result.stdout)
        self.assertEqual("pass", report["status"])
        names = {case["name"] for case in report["cases"]}
        self.assertEqual(
            {"dirty_worktree", "first_commit", "secret_guard", "sync_only", "untracked_junk"},
            names,
        )
        self.assertTrue(all(case["status"] == "pass" for case in report["cases"]))


if __name__ == "__main__":
    unittest.main()
