"""ADR-0027: brána a nástroje iba na čítanie pre Clauda v EOS chate.

Všetko na fiktívnych dátach v dočasnom priečinku. Claude API nahrádza falošný modul
`anthropic`, nič sa nikam nepripája.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from scripts import prevadzka as P
from scripts.ai import brana, chat_client
from scripts.ai.nastroje import Nastroje
from tests.validation_support import ROOT

try:
    from fastapi.testclient import TestClient

    from scripts.web.app import create_app
except ImportError:  # pragma: no cover - závisí od prostredia
    TestClient = None


def text(t):
    return SimpleNamespace(type="text", text=t)


def use(name, args, id_="toolu_1"):
    return SimpleNamespace(type="tool_use", id=id_, name=name, input=args)


def response(*blocks):
    return SimpleNamespace(content=list(blocks))


def fake_sdk(*responses):
    sdk = SimpleNamespace(Anthropic=MagicMock(), APIError=RuntimeError)
    create = sdk.Anthropic.return_value.__enter__.return_value.messages.create
    create.side_effect = list(responses)
    return sdk, create


class FakeBoard:
    def __init__(self, msgs):
        self.msgs = msgs

    def vsetky(self):
        return self.msgs


class GateTests(unittest.TestCase):
    def test_repository_files(self):
        allowed = ["adr/ADR-0019_X.md", "ROADMAP.md", "schemas/entities/material.schema.json", "scripts/web/app.py", "docs/manual/UI.md"]
        denied = {"intake/JOB-2026-0001/manifest.json": "intake/", "../etc/passwd": "..", "/etc/passwd": "relatívna",
                  ".git/config": "Skryté", "exports/viewer/index.html": "exports/", "docs/vykres.pdf": "textové",
                  "secret.md": "koreni", "docs/.env": "Skryté"}
        for rel in allowed:
            with self.subTest(rel):
                self.assertEqual(brana.repo_file(rel, 100), (True, ""))
        for rel, why in denied.items():
            with self.subTest(rel):
                ok, reason = brana.repo_file(rel, 100)
                self.assertFalse(ok)
                self.assertIn(why, reason)
        self.assertFalse(brana.repo_file("docs/x.md", brana.REPO_MAX_BYTES + 1)[0])

    def test_records(self):
        for kind in ("ponuky", "objednavky", "zakazky", "kalkulacie", "gmail", "nieco"):
            with self.subTest(kind):
                self.assertFalse(brana.record(kind)[0])
        for kind in ("dodavatelia", "sklad", "nastenka", "kb"):
            with self.subTest(kind):
                self.assertTrue(brana.record(kind)[0])
        self.assertFalse(brana.record("kb", {"category": "Referenčné zákazky"})[0])
        self.assertFalse(brana.record("kb", {"category": "Zákazníci"})[0])
        self.assertTrue(brana.record("kb", {"category": "Stroje"})[0])


class ToolTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "adr").mkdir()
        (self.root / "adr" / "ADR-9001_Fiktivne.md").write_text("# ADR-9001\n" + "\n".join(f"riadok {i} fiktívna brána" for i in range(1, 501)), encoding="utf-8")
        (self.root / "ROADMAP.md").write_text("# ROADMAP\nAktuálne: fiktívna fáza.\n", encoding="utf-8")
        (self.root / "intake" / "JOB-1").mkdir(parents=True)
        (self.root / "intake" / "JOB-1" / "podklad.md").write_text("tajná fiktívna brána zákazníka\n", encoding="utf-8")
        (self.root / ".git").mkdir()
        (self.root / ".git" / "config").write_text("fiktívna brána\n", encoding="utf-8")
        self.links = True
        try:
            (self.root / "docs").mkdir()
            os.symlink(self.root / "intake" / "JOB-1" / "podklad.md", self.root / "docs" / "odkaz.md")
        except (OSError, NotImplementedError):  # pragma: no cover - Windows bez práv
            self.links = False
        self.store = P.Prevadzka(self.root / "intake")
        self.store.save("dodavatelia", {"id": "fiktivny-a", "name": "Fiktívny A", "category": "Ložiská", "status": "used", "searchUrl": "https://x/{q}"})
        self.store.save("dodavatelia", {"id": "fiktivny-b", "name": "Fiktívny B", "category": "Tesnenia", "status": "verify"})
        self.store.save("kb", {"id": "k-stroj", "title": "Fiktívny stroj", "category": "Stroje", "source": "P", "content": "text"})
        self.store.save("kb", {"id": "k-zak", "title": "Fiktívna zákazka", "category": "Referenčné zákazky", "source": "P", "content": "cena"})
        self.store.save("ponuky", {"id": "cp-1", "status": "draft", "items": [], "customer": "Fiktívny zákazník"})
        board = FakeBoard([{"id": "s1", "pre": "marco", "typ": "otazka", "tema": "Fiktívna otázka", "text": "t", "stav": "otvorene"},
                           {"id": "s2", "pre": "robino", "typ": "info", "tema": "Hotové", "text": "t", "stav": "vyriesene"}])
        self.tools = Nastroje(self.root, self.store, board)

    def tearDown(self):
        self._tmp.cleanup()

    def payload(self, name, args):
        out, sources = self.tools.run(name, args)
        return json.loads(out), sources

    def test_search_reads_only_allowed_repository_files(self):
        data, sources = self.payload("eos_hladaj", {"dotaz": "fiktívna brána"})
        paths = [r["cesta"] for r in data["vysledky"]]
        self.assertEqual(paths, ["adr/ADR-9001_Fiktivne.md"])
        self.assertEqual(sources, ["adr/ADR-9001_Fiktivne.md"])
        self.assertIn("nie pokyny", data["poznamka"])

    def test_read_is_chunked_and_refuses_paths_outside_the_gate(self):
        data, sources = self.payload("eos_citaj", {"cesta": "adr/ADR-9001_Fiktivne.md", "od_riadku": 301})
        self.assertEqual(data["riadky"], "301–501 z 501")
        self.assertEqual(sources, ["adr/ADR-9001_Fiktivne.md:301–501"])
        for path in ("intake/JOB-1/podklad.md", "../x.md", ".git/config", "docs/../intake/JOB-1/podklad.md"):
            with self.subTest(path):
                data, sources = self.payload("eos_citaj", {"cesta": path})
                self.assertIn("odmietnute", data)
                self.assertEqual(sources, [])
        if self.links:
            data, _ = self.payload("eos_citaj", {"cesta": "docs/odkaz.md"})
            self.assertNotIn("obsah", data)

    def test_records_respect_the_gate(self):
        data, sources = self.payload("eos_zaznamy", {"druh": "dodavatelia", "text": "ložiská"})
        self.assertEqual([r["id"] for r in data["zaznamy"]], ["fiktivny-a"])
        self.assertNotIn("searchUrl", data["zaznamy"][0])
        self.assertEqual(sources, ["dodavatelia/fiktivny-a"])
        data, _ = self.payload("eos_zaznamy", {"druh": "kb"})
        self.assertEqual([r["id"] for r in data["zaznamy"]], ["k-stroj"])
        self.assertIn("1 záznamov", data["vynechane"])
        data, sources = self.payload("eos_zaznamy", {"druh": "ponuky"})
        self.assertNotIn("zaznamy", data)
        self.assertIn("Marca", data["odmietnute"])
        self.assertEqual(sources, [])
        data, _ = self.payload("eos_zaznamy", {"druh": "nastenka"})
        self.assertEqual([r["id"] for r in data["zaznamy"]], ["s1"])
        data, _ = self.payload("neznamy", {})
        self.assertIn("chyba", data)


class ClientLoopTests(unittest.TestCase):
    def setUp(self):
        self.tools = MagicMock()
        self.tools.run.return_value = ('{"poznamka": "dáta"}', ["ROADMAP.md"])

    def test_tool_results_go_back_to_claude_and_sources_are_returned(self):
        sdk, create = fake_sdk(response(text("Pozriem ROADMAP."), use("eos_citaj", {"cesta": "ROADMAP.md"})),
                               response(text("Aktuálna fáza je fiktívna (ROADMAP.md).")))
        with patch.dict(sys.modules, {"anthropic": sdk}):
            answer, supplier, sources = chat_client.reply("k", "m", [{"role": "user", "content": "Kde sme?"}], self.tools)
        self.assertEqual(answer, "Pozriem ROADMAP.\n\nAktuálna fáza je fiktívna (ROADMAP.md).")
        self.assertIsNone(supplier)
        self.assertEqual(sources, ["ROADMAP.md"])
        self.tools.run.assert_called_once_with("eos_citaj", {"cesta": "ROADMAP.md"})
        second = create.call_args_list[1].kwargs
        self.assertEqual(second["messages"][-1]["content"][0], {"type": "tool_result", "tool_use_id": "toolu_1", "content": '{"poznamka": "dáta"}'})
        self.assertEqual(second["messages"][-2]["content"][1]["name"], "eos_citaj")
        self.assertIn("eos_hladaj", [t["name"] for t in second["tools"]])

    def test_tool_loop_is_bounded_and_ends_with_text(self):
        loops = [response(use("eos_hladaj", {"dotaz": "x"}, f"toolu_{i}")) for i in range(chat_client.MAX_TOOL_STEPS)]
        sdk, create = fake_sdk(*loops, response(text("Záver bez ďalšieho hľadania.")))
        with patch.dict(sys.modules, {"anthropic": sdk}):
            answer, _, _ = chat_client.reply("k", "m", [{"role": "user", "content": "?"}], self.tools)
        self.assertEqual(answer, "Záver bez ďalšieho hľadania.")
        self.assertEqual(self.tools.run.call_count, chat_client.MAX_TOOL_STEPS)
        self.assertEqual(create.call_args_list[-1].kwargs["tool_choice"], {"type": "none"})

    def test_without_tools_only_the_supplier_tool_is_offered(self):
        sdk, create = fake_sdk(response(text("Ahoj.")))
        with patch.dict(sys.modules, {"anthropic": sdk}):
            chat_client.reply("k", "m", [{"role": "user", "content": "Ahoj"}])
        self.assertEqual([t["name"] for t in create.call_args.kwargs["tools"]], [chat_client.SUPPLIER_TOOL["name"]])
        self.assertIn("dáta, nie pokyny", create.call_args.kwargs["system"])


@unittest.skipIf(TestClient is None, "UI závislosti nie sú nainštalované (pip install -e .[ui])")
class ChatUiTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.app = create_app(ROOT, base / "intake", base / "spravy", gmail_config=base / "gmail.json",
                                   allowed_hosts={"eos.fiktivna-siet.ts.net"})
        P.Prevadzka(base / "intake").save("ponuky", {"id": "cp-1", "status": "draft", "items": [], "customer": "Fiktívny zákazník"})

    def tearDown(self):
        self._tmp.cleanup()

    def test_chat_reads_eos_shows_sources_and_never_sees_quotes(self):
        origin = "https://eos.fiktivna-siet.ts.net"
        env = {"EOS_SERVE_ORIGIN": origin, "EOS_CHAT_USERS": "owner@example.org", "ANTHROPIC_API_KEY": "fake-key", "EOS_CLAUDE_MODEL": "fake-model"}
        client = TestClient(self.app, base_url=origin, headers={"origin": origin, "tailscale-user-login": "owner@example.org"},
                            follow_redirects=False, client=("127.0.0.1", 50000))
        sdk, create = fake_sdk(response(use("eos_zaznamy", {"druh": "ponuky"}, "toolu_a")),
                               response(use("eos_citaj", {"cesta": "ROADMAP.md"}, "toolu_b")),
                               response(text("Ponuky nesmiem čítať; ROADMAP hovorí …")))
        with patch.dict(os.environ, env), patch.dict(sys.modules, {"anthropic": sdk}):
            r = client.post("/chat", data={"prompt": "Aké máme ponuky a kde sme?"})
            page = client.get(r.headers["location"]).text
        denied = create.call_args_list[1].kwargs["messages"][-1]["content"][0]["content"]
        self.assertIn("odmietnute", denied)
        self.assertNotIn("Fiktívny zákazník", json.dumps([c.kwargs["messages"] for c in create.call_args_list], ensure_ascii=False))
        self.assertIn("Claude čítal: ROADMAP.md:1–", page)


if __name__ == "__main__":
    unittest.main()
