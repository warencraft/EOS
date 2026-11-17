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
        self.status = Path(self._tmp.name) / "spravy"
        self.client = TestClient(create_app(ROOT, self.intake, self.status))

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

    def test_new_job_with_upload_preview_and_path_safety(self):
        r = self.client.post("/nova", data={"nazov": "Fiktívna nová", "kto": "Marco", "priecinok": "vykresy"},
                             files=[("subory", ("výkres 1.pdf", b"%PDF-1.4 fiktivny", "application/pdf")),
                                    ("subory", ("../manifest.json", b"{}", "application/json"))],
                             follow_redirects=False)
        self.assertEqual(r.status_code, 303)
        ref, preskocene = r.headers["location"].rsplit("/", 1)[1].split("?")
        self.assertRegex(ref, r"^JOB-\d{4}-\d{4}$")
        self.assertNotIn(ref, {"JOB-2026-9001", "JOB-2026-9002"})  # ďalšie voľné číslo, nič neprepíše
        self.assertIn("manifest.json", self.client.get(f"/zakazka/{ref}?{preskocene}").text)
        z = json.loads((self.intake / ref / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(f["path"] for f in z["files"]), ["vykresy/výkres 1.pdf"])
        self.assertEqual(z["title"], "Fiktívna nová")
        self.assertIn("<iframe", self.client.get(f"/zakazka/{ref}").text)
        r = self.client.get(f"/zakazka/{ref}/subor/vykresy/v%C3%BDkres%201.pdf")
        self.assertEqual((r.status_code, r.headers["content-type"]), (200, "application/pdf"))
        self.assertTrue(r.headers["content-disposition"].startswith("inline"))
        for zly in ("manifest.json", "vykresy/manifest.json", "../JOB-2026-9001/manifest.json", "%2E%2E/x.pdf"):
            self.assertEqual(self.client.get(f"/zakazka/{ref}/subor/{zly}").status_code, 404, zly)
        self.assertEqual(self.client.post("/nova", data={"nazov": " ", "kto": "Marco"}).status_code, 422)
        self.assertEqual(job_intake.cmd_check(self.intake / ref)[0], [])

    def test_calculation_from_template_job_and_row_editing(self):
        r = self.client.post("/zakazka/JOB-2026-9002/kalkulacia/nova",
                             data={"mnozstvo": "4", "vzor": "JOB-2026-9001", "pracaEurH": ""}, follow_redirects=False)
        self.assertEqual(r.status_code, 303)
        self.assertIn("Skopírované z JOB-2026-9001", self.client.get("/zakazka/JOB-2026-9002").text)
        base = "/zakazka/JOB-2026-9002"
        r = self.client.post(f"{base}/pridaj/operacie", data={"diel": "Diel A", "proces": "Proces Z", "a": "10",
                                                              "b": "4", "polozkaPonuky": "Priame mzdy"})
        self.assertIn("Proces Z", r.text)
        self.client.post(f"{base}/pole/material/M1/kg", data={"hodnota": "25"})
        self.client.post(f"{base}/odober/nakup/N2")
        self.client.post(f"{base}/mnozstvo", data={"mnozstvo": "5"})
        self.assertIn("nie je nezáporné číslo", self.client.post(f"{base}/mnozstvo", data={"mnozstvo": "0"}).text)
        self.assertEqual(self.client.post(f"{base}/pole/operacie/O1/proces", data={"hodnota": "1"}).status_code, 404)
        k = json.loads((self.intake / "_eos" / "kalkulacie" / "JOB-2026-9002.json").read_text(encoding="utf-8"))
        self.assertEqual((k["mnozstvo"], k["material"][0]["kg"], [n["id"] for n in k["nakup"]]), (5.0, 25.0, ["N1"]))
        self.assertEqual(k["operacie"][-1]["id"], "O4")
        self.assertEqual(self.client.post(f"{base}/kalkulacia/nova", data={"mnozstvo": "1"}).status_code, 409)
        r = self.client.post("/zakazka/JOB-2026-9001/kalkulacia/nova", data={"mnozstvo": "1", "pracaEurH": "1"})
        self.assertEqual(r.status_code, 409)

    def test_empty_calculation_needs_valid_numbers(self):
        r = self.client.post("/zakazka/JOB-2026-9002/kalkulacia/nova", data={"mnozstvo": "0", "pracaEurH": "30"})
        self.assertEqual(r.status_code, 422)
        r = self.client.post("/zakazka/JOB-2026-9002/kalkulacia/nova", data={"mnozstvo": "3", "pracaEurH": "30"},
                             follow_redirects=False)
        self.assertEqual(r.status_code, 303)
        self.assertIn("Zatiaľ bez operácií", self.client.get("/zakazka/JOB-2026-9002").text)

    def test_cross_site_posts_are_rejected(self):
        for h in ({"Origin": "https://zla-stranka.example"}, {"Sec-Fetch-Site": "cross-site"}):
            r = self.client.post("/zakazka/JOB-2026-9001/sadzba", data={"pracaEurH": "99"}, headers=h)
            self.assertEqual(r.status_code, 403, h)
        self.assertEqual(self.stored()["sadzby"]["pracaEurH"], 30.0)
        r = self.client.post("/zakazka/JOB-2026-9001/sadzba", data={"pracaEurH": "35"},
                             headers={"Origin": "http://127.0.0.1:8000", "Sec-Fetch-Site": "same-origin"})
        self.assertEqual((r.status_code, self.stored()["sadzby"]["pracaEurH"]), (200, 35.0))

    def test_status_board_split_reply_resolve_and_privacy(self):
        r = self.client.post("/stav", data={"autor": "robino", "pre": "marco", "typ": "otazka",
                                            "tema": "Hustota ocele", "text": "Z ktorého katalógu?"},
                             follow_redirects=False)
        self.assertEqual(r.status_code, 303)
        (id_,) = [p.stem for p in self.status.glob("*.json")]
        self.client.post("/stav", data={"autor": "marco", "typ": "feedback", "text": "Z normy.", "odpovedNa": id_})
        odpoved = next(json.loads(p.read_text(encoding="utf-8")) for p in self.status.glob("*.json") if p.stem != id_)
        self.assertEqual((odpoved["autor"], odpoved["pre"], odpoved["tema"]), ("marco", "robino", "Re: Hustota ocele"))
        stranka = self.client.get("/stav").text
        marco, robino = stranka.split('id="h-robino"')
        self.assertIn("Hustota ocele", marco)
        self.assertNotIn("Hustota ocele", robino)
        self.assertIn("Z normy.", marco)
        self.assertIn('class="badge">1<', self.client.get("/").text)
        self.client.post(f"/stav/{id_}/vyriesit", data={"kto": "marco"})
        self.assertNotIn("Hustota ocele", self.client.get("/stav").text)
        self.assertIn("Hustota ocele", self.client.get("/stav?vsetky=1").text)
        r = self.client.post("/stav", data={"autor": "robino", "pre": "marco", "typ": "info", "tema": "x",
                                            "text": "Fiktívna zákazka sa posunie."})
        self.assertEqual(r.status_code, 422)
        self.assertEqual(len(list(self.status.glob("*.json"))), 2)
        self.assertEqual(self.client.post("/stav/nieco/vyriesit", data={"kto": "marco"}).status_code, 404)


if __name__ == "__main__":
    unittest.main()
