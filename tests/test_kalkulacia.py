"""ADR-0021: pracovná kalkulácia zákazky (scripts/calc).

Všetky čísla, názvy a sadzby sú fiktívne. Testy overujú výpočet a import, nie technické hodnoty.
Import .xlsx potrebuje openpyxl (voliteľná závislosť `import`); bez nej sa tieto testy preskočia.
"""
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from scripts.calc import kalkulacia as K

try:
    import openpyxl
except ImportError:  # pragma: no cover - závisí od prostredia
    openpyxl = None


def fiktivna_kalkulacia():
    return {
        "formatVersion": "0.1.0", "jobRef": "JOB-2026-9001", "nazov": "Fiktívny výrobok", "zakaznik": "Fiktívny zákazník",
        "vykres": None, "materialPopis": None, "mnozstvo": 2, "terminDodania": None,
        "sadzby": {"pracaEurH": 30.0, "predajEurH": 50.0},
        "material": [{"id": "M1", "diel": "Diel A", "kg": 10.0, "eurZaKg": 2.0}],
        "operacie": [
            {"id": "O1", "diel": "Diel A", "proces": "Proces X", "casNaKusMin": 60.0, "kusov": 2, "sadzbaEurH": None},
            {"id": "O2", "diel": "Diel A", "proces": "Proces Y", "casNaKusMin": 30.0, "kusov": 2, "sadzbaEurH": 15.0},
            {"id": "O3", "diel": "Sada", "proces": "Proces X", "casNaKusMin": 6.0, "kusov": 2, "sadzbaEurH": None,
             "polozkaPonuky": K.TESNENIA},
        ],
        "nakup": [{"id": "N1", "nazov": "Kúpená položka", "eurZaKs": 5.0, "kusov": 4, "zapocitat": True},
                  {"id": "N2", "nazov": "Nezapočítaná", "eurZaKs": 7.0, "kusov": 1, "zapocitat": False}],
        "dalsie": [{"id": "D1", "nazov": "Dokumentácia", "eurZaKs": 10.0, "kusov": 1, "zapocitat": True,
                    "polozkaPonuky": K.DOKUMENTACIA}],
        "referencia": {"riadky": {K.MATERIAL: 20.0, K.PRACA: 75.0}, "spolu": 120.0, "zaKus": 60.0},
        "upozornenia": [], "zmeny": [],
    }


class VypocetTests(unittest.TestCase):
    def test_fictional_calculation_is_valid(self):
        self.assertEqual(K.chyby_formatu(fiktivna_kalkulacia()), [])

    def test_lines_follow_quote_order_and_rates(self):
        v = K.vypocitaj(fiktivna_kalkulacia())
        riadky = {r["nazov"]: r["suma"] for r in v["riadky"]}
        # práca: 120 min × 30 €/h = 60 € + 60 min × 15 €/h = 15 €
        self.assertEqual(riadky, {K.MATERIAL: 20.0, K.NAKUP: 20.0, K.TESNENIA: 6.0, K.PRACA: 75.0, K.DOKUMENTACIA: 10.0})
        self.assertEqual([r["nazov"] for r in v["riadky"]], [K.MATERIAL, K.NAKUP, K.TESNENIA, K.PRACA, K.DOKUMENTACIA])
        self.assertEqual((v["spolu"], v["zaKus"], v["hodinSpolu"], v["nezapocitane"]), (131.0, 65.5, 3.2, 7.0))
        self.assertTrue(v["operacie"]["O2"]["inaSadzba"])

    def test_uniform_rate_overrides_row_rates(self):
        v = K.vypocitaj(fiktivna_kalkulacia(), jednotna_sadzba=30.0)
        self.assertEqual(next(r["suma"] for r in v["riadky"] if r["nazov"] == K.PRACA), 90.0)
        self.assertFalse(v["operacie"]["O2"]["inaSadzba"])

    def test_comparison_reports_difference_to_quote(self):
        k = fiktivna_kalkulacia()
        diff = {p["nazov"]: p["rozdiel"] for p in K.porovnanie(k, K.vypocitaj(k))}
        self.assertEqual(diff, {K.MATERIAL: 0.0, K.PRACA: 0.0, "Spolu": 11.0})

    def test_change_is_logged_and_original_untouched(self):
        k = fiktivna_kalkulacia()
        nova = K.zmen(k, "operacie.O1.casNaKusMin", 90.0)
        self.assertEqual(k["operacie"][0]["casNaKusMin"], 60.0)
        self.assertEqual(nova["operacie"][0]["casNaKusMin"], 90.0)
        self.assertEqual([(z["pole"], z["povodne"], z["nove"]) for z in nova["zmeny"]],
                         [("operacie.O1.casNaKusMin", 60.0, 90.0)])
        self.assertEqual(K.zmen(nova, "operacie.O1.casNaKusMin", 90.0)["zmeny"], nova["zmeny"])
        self.assertEqual(K.zmen(k, "sadzby.pracaEurH", 40.0)["sadzby"]["pracaEurH"], 40.0)

    def test_change_rejects_unknown_target(self):
        with self.assertRaises(KeyError):
            K.zmen(fiktivna_kalkulacia(), "operacie.O99.casNaKusMin", 1.0)
        with self.assertRaises(KeyError):
            K.zmen(fiktivna_kalkulacia(), "zakaznik", "x")

    def test_format_rejects_unknown_field_and_bad_job_ref(self):
        k = deepcopy(fiktivna_kalkulacia())
        k["neznamy"] = 1
        k["jobRef"] = "JOB-26-1"
        chyby = " ".join(K.chyby_formatu(k))
        self.assertIn("neznamy", chyby)
        self.assertIn("jobRef", chyby)


H1 = {"B": "Číslo výkresu", "J": "Názov materiálu", "K": "Priemer", "N": "Dĺžka + 3mm prídavok na opracovanie",
      "Q": "Norma", "R": "Material", "V": "ks", "W": "Hmotnosť", "AH": "Jednotková cena", "AQ": "Cena  celkova",
      "AW": "SUS", "BE": "VRTANIE", "CH": "Čas/ celkom v min", "CK": "PRIAME MZDY (1hod/20€ )", "CM": " (1hod/50€ )"}
H3 = {"V": "zákazku", "AW": "Čas/1ks min", "BE": "Čas/1ks min", "CL": "Cena spolu", "AQ": "€", "W": "[kg]"}


class UpravyBezExceluTests(unittest.TestCase):
    def test_empty_calculation_rows_and_quantity(self):
        k = K.prazdna("JOB-2026-9002", nazov="Fiktívna", mnozstvo=2, praca_eur_h=30.0)
        self.assertEqual(K.chyby_formatu(k), [])
        self.assertEqual(K.vypocitaj(k)["spolu"], 0)
        k = K.pridaj(k, "operacie", {"diel": "Diel A", "proces": "Proces X", "casNaKusMin": 30.0, "kusov": 2,
                                     "sadzbaEurH": None})
        k = K.pridaj(k, "material", {"diel": "Diel A", "kg": 3.0, "eurZaKg": 2.0})
        k = K.pridaj(k, "nakup", {"nazov": "Kúpená", "eurZaKs": 4.0, "kusov": 1, "zapocitat": True})
        self.assertEqual([x["id"] for x in k["operacie"] + k["material"] + k["nakup"]], ["O1", "M1", "N1"])
        self.assertEqual(K.vypocitaj(k)["spolu"], 40.0)  # 30 + 6 + 4
        k = K.zmen(k, "mnozstvo", 4)
        self.assertEqual(K.vypocitaj(k)["zaKus"], 10.0)
        k = K.odober(k, "material", "M1")
        k = K.pridaj(k, "material", {"diel": "Diel B", "kg": 1.0, "eurZaKg": 1.0})
        self.assertEqual(k["material"][0]["id"], "M2")  # id sa po odobratí nepoužije znova
        self.assertEqual(K.chyby_formatu(k), [])
        self.assertEqual([z["pole"] for z in k["zmeny"]],
                         ["operacie.O1", "material.M1", "nakup.N1", "mnozstvo", "material.M1", "material.M2"])
        with self.assertRaises(KeyError):
            K.odober(k, "operacie", "O9")
        with self.assertRaises(KeyError):
            K.pridaj(k, "referencia", {})

    def test_copy_scales_counts_and_warns(self):
        zdroj = fiktivna_kalkulacia()
        k = K.skopiruj(zdroj, "JOB-2026-9003", nazov="Kópia", mnozstvo=4)
        self.assertEqual(K.chyby_formatu(k), [])
        self.assertEqual([o["kusov"] for o in k["operacie"]], [4, 4, 4])
        self.assertEqual(k["material"][0]["kg"], 20.0)
        self.assertEqual(k["nakup"][0]["kusov"], 8)
        self.assertEqual(k["dalsie"][0]["kusov"], 1)  # dokumentácia sa neprepočítava
        self.assertEqual((k["jobRef"], k["referencia"], k["zmeny"]), ("JOB-2026-9003", None, []))
        self.assertNotIn("zdroj", k)
        self.assertEqual([u["kod"] for u in k["upozornenia"]], ["kopia"])
        self.assertEqual(zdroj["operacie"][0]["kusov"], 2)  # vzor sa nezmenil


@unittest.skipIf(openpyxl is None, "openpyxl nie je nainštalované (pip install -e .[import])")
class ImportTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.subor = Path(self._tmp.name) / "fiktivna-sablona.xlsx"
        wb = openpyxl.Workbook()
        ns = wb.active
        ns.title = "Nesortovaný"
        for col, text in H1.items():
            ns[f"{col}1"] = text
        for col, text in H3.items():
            ns[f"{col}3"] = text
        # riadok 4: diel s materiálom a dvoma operáciami, ocenený 30 €/h (90 min → 45 €)
        for col, v in {"B": "Fiktívny diel A", "J": "Guľatina", "K": 10, "N": 100, "Q": "Fiktívna norma",
                       "R": "Fiktívna akosť", "V": 2, "W": 3.0, "AH": 2.0, "AQ": 6.0,
                       "AW": 30, "BE": 15, "CH": 90, "CL": 45.0}.items():
            ns[f"{col}4"] = v
        # riadok 5: iná sadzba 20 €/h (60 min → 20 €)
        for col, v in {"B": "Fiktívny diel B", "V": 2, "BE": 30, "CH": 60, "CL": 20.0}.items():
            ns[f"{col}5"] = v
        # riadok 6: zvyšok šablóny – iba hmotnosť
        ns["B6"], ns["W6"] = "Starý riadok", 50.0
        ns["A7"] = "Spolu"
        sp = wb.create_sheet("SPOJOVACÍ MAT. NÁRADIE ")
        for col, text in {"B": "Číslo výkresa", "R": "ks", "T": "ks", "AF": "Jednotková cena", "AO": "Cena  celkova"}.items():
            sp[f"{col}1"] = text
        sp["R3"], sp["T3"], sp["AO3"] = "rozpiska", "zákazku", "€"
        for r, (nazov, rozp, zak, cena, spolu) in enumerate([("Kúpená A", 4, 1, 3.0, 12.0), ("Kúpená B", 1, 1, 9.0, None)], 4):
            sp[f"B{r}"], sp[f"R{r}"], sp[f"T{r}"], sp[f"AF{r}"] = nazov, rozp, zak, cena
            if spolu:
                sp[f"AO{r}"] = spolu
        sp["A6"] = "Spolu"
        kal = wb.create_sheet("KALKULAČNÍ")
        for r, (label, value) in enumerate([("Zákazník :", None), ("Názov výrobku :", "Fiktívny výrobok"),
                                            ("Množstvo :", 2)], 4):
            kal[f"B{r}"] = label
            if value is not None:
                kal[f"C{r}"] = value
        for r, (label, value) in enumerate([("Priamy materiál", 6.0), ("Náradie - nakupovaný materiál", 12.0),
                                            ("Priame mzdy", 65.0), ("Celková cena 30 eur/hod", 90.0),
                                            ("Kusová cena", 45.0)], 12):
            kal[f"D{r}"], kal[f"G{r}"] = label, value
        wb.save(self.subor)

    def tearDown(self):
        self._tmp.cleanup()

    def test_import_reproduces_quote_and_flags_template_errors(self):
        from scripts.calc import import_sablona as I

        k = I.importuj(self.subor, "JOB-2026-9001", relativna_cesta="ponuka/fiktivna-sablona.xlsx")
        self.assertEqual(K.chyby_formatu(k), [])
        self.assertEqual((k["mnozstvo"], k["nazov"], k["sadzby"]), (2.0, "Fiktívny výrobok", {"pracaEurH": 30.0, "predajEurH": 50.0}))
        self.assertEqual([(o["diel"], o["proces"], o["casNaKusMin"], o["sadzbaEurH"]) for o in k["operacie"]],
                         [("Fiktívny diel A", "Sústruženie", 30, None), ("Fiktívny diel A", "Vŕtanie", 15, None),
                          ("Fiktívny diel B", "Vŕtanie", 30, 20.0)])
        self.assertEqual([(n["nazov"], n["kusov"], n["zapocitat"]) for n in k["nakup"]],
                         [("Kúpená A", 4.0, True), ("Kúpená B", 1.0, False)])
        v = K.vypocitaj(k)
        self.assertEqual((v["spolu"], v["zaKus"]), (83.0, 41.5))
        kody = sorted(u["kod"] for u in k["upozornenia"])
        self.assertEqual(kody, ["hlavicka_sadzby", "mnozstvo_nesedi", "nezapocitane", "rozdiel_ponuky",
                                "sadzba_rozdielna", "zakaznik_chyba", "zvysky_sablony"])
        rozdiel = next(u for u in k["upozornenia"] if u["kod"] == "rozdiel_ponuky")
        self.assertEqual(rozdiel["dopadEur"], -7.0)
        sadzba = next(u for u in k["upozornenia"] if u["kod"] == "sadzba_rozdielna")
        self.assertEqual((sadzba["bunka"], sadzba["dopadEur"]), ("Nesortovaný!CL5", -10.0))

    def test_non_template_file_is_rejected(self):
        from scripts.calc import import_sablona as I

        wb = openpyxl.Workbook()
        wb.active.title = "Hárok1"
        cudzi = Path(self._tmp.name) / "iny.xlsx"
        wb.save(cudzi)
        with self.assertRaises(I.ChybaImportu):
            I.importuj(cudzi, "JOB-2026-9001")
        with self.assertRaises(I.ChybaImportu):
            I.importuj(Path(self._tmp.name) / "x.pdf", "JOB-2026-9001")


if __name__ == "__main__":
    unittest.main()
