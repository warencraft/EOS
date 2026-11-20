"""The .claude/skills/ copy must match .agents/skills/ (scripts/sync_claude_skills.py)."""
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from scripts import sync_claude_skills as S
from tests.validation_support import ROOT


class ClaudeSkillsCopyTests(unittest.TestCase):
    def test_copy_matches_source(self):
        problems = S.differences(ROOT)
        self.assertEqual(problems, [], "Spusti: python scripts/sync_claude_skills.py\n" + "\n".join(problems))

    def test_every_skill_name_matches_its_folder(self):
        for skill in sorted((ROOT / S.SOURCE).glob("*/SKILL.md")):
            match = re.search(r"^name:\s*(\S+)\s*$", skill.read_text(encoding="utf-8"), re.M)
            with self.subTest(skill=skill.parent.name):
                self.assertIsNotNone(match, "chýba name vo frontmatter")
                self.assertEqual(match[1], skill.parent.name)

    def test_sync_creates_copy_removes_extra_files_and_ignores_crlf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / S.SOURCE / "eos-ukazka"
            source.mkdir(parents=True)
            (source / "SKILL.md").write_bytes(b"---\r\nname: eos-ukazka\r\n---\r\nText\r\n")
            stale = root / S.TARGET / "stary-skill" / "SKILL.md"
            stale.parent.mkdir(parents=True)
            stale.write_text("starý", encoding="utf-8")
            self.assertIn("navyše: stary-skill/SKILL.md", S.differences(root))
            S.sync(root)
            self.assertEqual(S.differences(root), [])
            self.assertFalse(stale.exists())
            self.assertEqual((root / S.TARGET / "eos-ukazka" / "SKILL.md").read_bytes(), b"---\nname: eos-ukazka\n---\nText\n")
            (source / "SKILL.md").write_text("zmenené", encoding="utf-8")
            self.assertEqual(S.differences(root), ["líši sa: eos-ukazka/SKILL.md"])


if __name__ == "__main__":
    unittest.main()
