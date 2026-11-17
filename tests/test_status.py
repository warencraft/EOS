"""ADR-0022: stavová nástenka (scripts/status) na fiktívnych správach v dočasnom priečinku."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import job_intake
from scripts.status import spravy as S
from scripts.status.__main__ import main


class NastenkaTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = Path(self._tmp.name)
        self.intake = tmp / "intake"
        self.intake.mkdir()
        job_intake.cmd_new("JOB-2026-9001", "Fiktívny valec (Fiktívna firma Alfa)", "test-suite", intake=self.intake)
        self.n = S.Nastenka(tmp / "spravy", intake=self.intake)

    def tearDown(self):
        self._tmp.cleanup()

    def test_new_message_is_valid_and_stored_as_own_file(self):
        s = self.n.pridaj(autor="agent", pre="marco", typ="kontrola", tema="Kontrola: nová entita Šablóna",
                          text="Over rozsah.", cas="2026-11-17T10:00:00Z")
        self.assertEqual(s["id"], "20261117T100000Z-agent-kontrola-nova-entita-sablona")
        self.assertEqual(S.chyby(s), [])
        self.assertTrue((self.n.priecinok / f"{s['id']}.json").is_file())
        druha = self.n.pridaj(autor="agent", pre="marco", typ="kontrola", tema="Kontrola: nová entita Šablóna",
                              text="Iná.", cas="2026-11-17T10:00:00Z")
        self.assertEqual(druha["id"], s["id"] + "-2")

    def test_invalid_values_are_rejected(self):
        for kw in ({"autor": "niekto"}, {"pre": "agent"}, {"typ": "iny"}, {"text": " "}):
            zaklad = {"autor": "robino", "pre": "marco", "typ": "otazka", "tema": "T", "text": "Text"}
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                self.n.pridaj(**{**zaklad, **kw})
        self.assertEqual(self.n.vsetky(), [])

    def test_customer_names_from_intake_are_blocked(self):
        with self.assertRaisesRegex(ValueError, "Fiktívna firma Alfa"):
            self.n.pridaj(autor="robino", pre="marco", typ="otazka", tema="Ponuka",
                          text="Volal fiktívna firma alfa kvôli cene.")
        self.assertEqual(self.n.vsetky(), [])
        self.n.pridaj(autor="robino", pre="marco", typ="otazka", tema="Ponuka", text="Pozri JOB-2026-9001.")

    def test_check_finds_tampered_files(self):
        s = self.n.pridaj(autor="marco", pre="robino", typ="feedback", tema="T", text="OK")
        p = self.n.priecinok / f"{s['id']}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        data["text"] = "Fiktívna firma Alfa"
        data["stav"] = "neviem"
        p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        (self.n.priecinok / "20261117T100000Z-marco-zly.json").write_text("{", encoding="utf-8")
        problemy = "\n".join(self.n.kontrola())
        self.assertIn("citlivý údaj", problemy)
        self.assertIn("stav", problemy)
        self.assertIn("nie je platný JSON", problemy)

    def test_replies_resolution_and_columns(self):
        pre_marca = self.n.pridaj(autor="agent", pre="marco", typ="rozhodnutie", tema="A alebo B", text="…",
                                  cas="2026-11-17T10:00:00Z")
        oboch = self.n.pridaj(autor="agent", pre="oba", typ="info", tema="Info", text="…", cas="2026-11-17T11:00:00Z")
        self.n.pridaj(autor="marco", pre="robino", typ="feedback", tema="Re", text="B.", odpoved_na=pre_marca["id"],
                      cas="2026-11-17T12:00:00Z")
        with self.assertRaises(KeyError):
            self.n.pridaj(autor="marco", pre="robino", typ="feedback", tema="Re", text="?",
                          odpoved_na="20991231T000000Z-agent-neexistuje")
        marco = self.n.pre("marco")
        self.assertEqual([s["id"] for s in marco], [oboch["id"], pre_marca["id"]])
        self.assertEqual(marco[1]["odpovede"][0]["text"], "B.")
        self.assertEqual([s["id"] for s in self.n.pre("robino")], [oboch["id"]])
        self.n.vyries(pre_marca["id"], "marco")
        self.assertEqual([s["id"] for s in self.n.pre("marco")], [oboch["id"]])
        self.assertEqual(self.n.pre("marco", aj_vyriesene=True)[1]["vyriesil"], "marco")
        self.n.vyries(pre_marca["id"], "robino", znovu_otvor=True)
        self.assertEqual(len(self.n.pre("marco")), 2)
        self.assertEqual(self.n.kontrola(), [])

    def test_cli_new_list_resolve_check(self):
        out = io.StringIO()
        zaklad = ["--priecinok", str(self.n.priecinok), "--intake", str(self.intake)]
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(zaklad + ["nova", "--autor", "agent", "--pre", "robino", "--typ", "kontrola",
                                            "--tema", "Kontrola testov", "--text", "Chýba test.", "--vetva", "tools/x"]), 0)
        id_ = Path(out.getvalue().strip()).stem
        self.assertEqual(self.n.nacitaj(id_)["vetva"], "tools/x")
        with contextlib.redirect_stdout(io.StringIO()) as zoznam:
            main(zaklad + ["zoznam", "--pre", "robino"])
        self.assertIn("Kontrola testov", zoznam.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(zaklad + ["vyries", id_, "--kto", "robino"]), 0)
            self.assertEqual(main(zaklad + ["kontrola"]), 0)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(zaklad + ["vyries", "../../etc", "--kto", "robino"]), 2)

    def test_repository_board_is_valid(self):
        self.assertEqual(S.Nastenka(S.PRIECINOK).kontrola(), [])


if __name__ == "__main__":
    unittest.main()
