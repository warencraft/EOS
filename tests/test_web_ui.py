"""ADR-0021: lokálne UI v0 (scripts/web) nad fiktívnou zákazkou v dočasnom intake/.

Potrebuje voliteľné závislosti `ui` (fastapi, jinja2, httpx); bez nich sa testy preskočia.
"""
import json
import tempfile
import unittest
from pathlib import Path

from scripts import job_intake
from tests.test_kalkulacia import fiktivna_kalkulacia
from tests.validation_support import ROOT

try:
    from fastapi.testclient import TestClient

    from scripts.web.app import create_app
except ImportError:  # pragma: no cover - závisí od prostredia
    TestClient = None


@unittest.skipIf(TestClient is None, "UI závislosti nie sú nainštalované (pip install -e .[ui])")
class WebUiTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.intake = Path(self._tmp.name)
        job_intake.cmd_new("JOB-2026-9001", "Fiktívna zákazka", "test-suite", intake=self.intake)
        job_intake.cmd_new("JOB-2026-9002", "Fiktívna bez kalkulácie", "test-suite", intake=self.intake)
        kalk = self.intake / "_eos" / "kalkulacie"
        kalk.mkdir(parents=True)
        (kalk / "JOB-2026-9001.json").write_text(json.dumps(fiktivna_kalkulacia(), ensure_ascii=False), encoding="utf-8")
        self.client = TestClient(create_app(ROOT, self.intake))

    def tearDown(self):
        self._tmp.cleanup()

    def stored(self):
        return json.loads((self.intake / "_eos" / "kalkulacie" / "JOB-2026-9001.json").read_text(encoding="utf-8"))

    def test_job_list_shows_both_jobs_and_totals(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("JOB-2026-9001", r.text)
        self.assertIn("JOB-2026-9002", r.text)
        self.assertIn("131,00", r.text)
        self.assertIn("nesedí s ponukou", r.text)  # fiktívna ponuka 120 € ≠ výpočet 131 €

    def test_job_detail_renders_calculation_and_empty_state(self):
        self.assertIn("65,50 €", self.client.get("/zakazka/JOB-2026-9001").text)
        self.assertIn("nemá kalkuláciu", self.client.get("/zakazka/JOB-2026-9002").text)
        self.assertEqual(self.client.get("/zakazka/JOB-2026-9999").status_code, 404)
        self.assertEqual(self.client.get("/zakazka/nieco").status_code, 404)

    def test_editing_time_recalculates_saves_and_logs(self):
        r = self.client.post("/zakazka/JOB-2026-9001/operacia/O1", data={"casNaKusMin": "90"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("161,00 €", r.text)  # +30 min × 2 ks × 30 €/h = +30 €
        s = self.stored()
        self.assertEqual(s["operacie"][0]["casNaKusMin"], 90.0)
        self.assertEqual([z["pole"] for z in s["zmeny"]], ["operacie.O1.casNaKusMin"])

    def test_invalid_value_is_rejected_without_saving(self):
        r = self.client.post("/zakazka/JOB-2026-9001/operacia/O1", data={"casNaKusMin": "-5"})
        self.assertIn("nie je nezáporné číslo", r.text)
        self.assertEqual(self.stored()["zmeny"], [])

    def test_rate_toggle_and_unify(self):
        self.client.post("/zakazka/JOB-2026-9001/sadzba", data={"pracaEurH": "40"})
        self.client.post("/zakazka/JOB-2026-9001/nakup/N2/zapocitat")
        self.client.post("/zakazka/JOB-2026-9001/operacia/O2/sadzba")
        s = self.stored()
        self.assertEqual(s["sadzby"]["pracaEurH"], 40.0)
        self.assertTrue(s["nakup"][1]["zapocitat"])
        self.assertIsNone(s["operacie"][1]["sadzbaEurH"])
        self.assertEqual(len(s["zmeny"]), 3)

    def test_import_rejects_file_outside_manifest(self):
        r = self.client.post("/zakazka/JOB-2026-9002/import", data={"subor": "../../etc/passwd"})
        self.assertEqual(r.status_code, 400)

    def test_model_page_lists_entities_and_gaps(self):
        r = self.client.get("/model")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Čo model ešte nevie", r.text)
        self.assertIn("Materiál", r.text)

    def test_calculations_stay_outside_job_folders(self):
        problems, _ = job_intake.cmd_check(self.intake / "JOB-2026-9001")
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
