"""ADR-0019: príjem podkladov reálnej zákazky mimo gitu (scripts/job_intake.py).

Testy pracujú iba s fiktívnymi súbormi v dočasnom priečinku.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import job_intake
from tests.validation_support import ROOT


class JobIntakeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.intake = Path(self._tmp.name)
        self.job = job_intake.cmd_new("JOB-2026-9001", "Fiktívna zákazka", "test-suite", intake=self.intake)

    def tearDown(self):
        self._tmp.cleanup()

    def put(self, rel, content=b"fictional"):
        path = self.job / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def manifest(self):
        return json.loads((self.job / "manifest.json").read_text(encoding="utf-8"))

    def test_gitignore_keeps_job_files_out_of_git(self):
        lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("intake/*", lines)
        self.assertIn("!intake/README.md", lines)
        ignored = subprocess.run(["git", "check-ignore", "-q", "intake/JOB-2026-9001/vykresy/a.pdf"], cwd=ROOT)
        kept = subprocess.run(["git", "check-ignore", "-q", "intake/README.md"], cwd=ROOT)
        self.assertEqual((ignored.returncode, kept.returncode), (0, 1))

    def test_new_creates_folders_and_safe_defaults(self):
        self.assertEqual({p.name for p in self.job.iterdir() if p.is_dir()}, set(job_intake.FOLDERS))
        manifest = self.manifest()
        self.assertEqual((manifest["confidentiality"], manifest["aiProcessingAllowed"], manifest["files"]),
                         ("confidential", False, []))
        self.assertEqual(job_intake.cmd_check(self.job), ([], []))
        with self.assertRaises(SystemExit):
            job_intake.cmd_new("JOB-2026-9001", "Fiktívna zákazka", "test-suite", intake=self.intake)
        with self.assertRaises(SystemExit):
            job_intake.cmd_new("JOB-26-1", "Zlé ID", "test-suite", intake=self.intake)

    def test_scan_records_category_hash_and_unclassified_source(self):
        self.put("vykresy/fiktivny-vykres.pdf", b"drawing")
        self.put("poznamka.txt", b"note")
        self.put("vykresy/.DS_Store", b"system")
        report = job_intake.cmd_scan(self.job)
        self.assertEqual(report, {"added": ["poznamka.txt", "vykresy/fiktivny-vykres.pdf"], "changed": [], "missing": []})
        entries = {e["path"]: e for e in self.manifest()["files"]}
        self.assertEqual(entries["vykresy/fiktivny-vykres.pdf"]["category"], "drawing")
        self.assertEqual(entries["poznamka.txt"]["category"], "other")
        self.assertEqual(entries["vykresy/fiktivny-vykres.pdf"]["sha256"], job_intake.sha256(self.job / "vykresy/fiktivny-vykres.pdf"))
        self.assertIsNone(entries["poznamka.txt"]["sourceClass"])
        errors, warnings = job_intake.cmd_check(self.job)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 2)

    def test_check_detects_changed_missing_and_unlisted_files(self):
        drawing = self.put("vykresy/a.pdf", b"v1")
        self.put("ponuka/b.pdf", b"quote")
        job_intake.cmd_scan(self.job)
        drawing.write_bytes(b"v2")
        (self.job / "ponuka/b.pdf").unlink()
        self.put("merania/c.pdf", b"measurement")
        errors, _ = job_intake.cmd_check(self.job)
        self.assertEqual(len(errors), 3)
        for word in ("a.pdf sa zmenil", "chýba súbor ponuka/b.pdf", "merania/c.pdf nie je v manifeste"):
            self.assertTrue(any(word in e for e in errors), (word, errors))
        report = job_intake.cmd_scan(self.job)
        self.assertEqual(report, {"added": ["merania/c.pdf"], "changed": ["vykresy/a.pdf"], "missing": ["ponuka/b.pdf"]})

    def test_check_rejects_invalid_manifest_values(self):
        self.put("vykresy/a.pdf")
        job_intake.cmd_scan(self.job)
        cases = {
            "unknown-source-class": (lambda m: m["files"][0].update(sourceClass="X"), "manifest files/0/sourceClass"),
            "path-escape": (lambda m: m["files"][0].update(path="../a.pdf"), "manifest files/0/path"),
            "unknown-field": (lambda m: m.update(customerPrice=1), "manifest $: Additional properties"),
            "ai-flag-missing": (lambda m: m.pop("aiProcessingAllowed"), "'aiProcessingAllowed' is a required property"),
            "job-ref-mismatch": (lambda m: m.update(jobRef="JOB-2026-9002"), "nezodpovedá názvu priečinka"),
            "duplicate-entry": (lambda m: m["files"].append(dict(m["files"][0])), "duplicitný záznam vykresy/a.pdf"),
        }
        original = self.manifest()
        for name, (change, expected) in cases.items():
            with self.subTest(case=name):
                manifest = json.loads(json.dumps(original))
                change(manifest)
                job_intake.save_manifest(self.job, manifest)
                errors, _ = job_intake.cmd_check(self.job)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn(expected, errors[0])
        job_intake.save_manifest(self.job, original)
        self.assertEqual(job_intake.cmd_check(self.job)[0], [])

    def test_no_job_files_are_tracked_in_git(self):
        self.assertEqual(job_intake.tracked_intake_files(), [])


if __name__ == "__main__":
    unittest.main()
