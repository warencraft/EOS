"""ADR-0025: prevádzkové záznamy (scripts/prevadzka), Gmail cez IMAP (scripts/gmail) a ich stránky v UI.

Všetko na fiktívnych dátach v dočasnom priečinku. Gmail nahrádza falošný IMAP server, nič sa
nikam nepripája. Testy UI potrebujú `.[ui]`, inak sa preskočia.
"""
import email
import email.policy
import imaplib
import json
import os
import re
import sys
import stat
import tempfile
import unittest
from email.message import EmailMessage
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from jsonschema import Draft202012Validator

from scripts import gmail as G
from scripts import prevadzka as P
from scripts.prevadzka.__main__ import import_export
from tests.validation_support import ROOT

try:
    from fastapi.testclient import TestClient

    from scripts.web.app import create_app
except ImportError:  # pragma: no cover - závisí od prostredia
    TestClient = None

PASSWORD = "abcd efgh ijkl mnop"


def mail(uid, thrid, subject, sender, date, body, html=False, msgid=None):
    m = EmailMessage()
    m["From"], m["To"], m["Subject"], m["Date"] = sender, "firma@example.com", subject, date
    m["Message-ID"] = msgid or f"<m{uid}@example.org>"
    if html:
        m.set_content("<p>Dobrý deň,<br>prosím ponuku.</p><script>x()</script>", subtype="html")
    else:
        m.set_content(body)
    return {"uid": uid, "thrid": thrid, "raw": m.as_bytes()}


class FakeIMAP:
    """Minimálny IMAP podľa toho, čo posiela Gmail: LIST s príznakmi, UID SEARCH X-GM-RAW/X-GM-THRID, FETCH, APPEND."""
    instances = []

    def __init__(self, messages=(), password=PASSWORD.replace(" ", "")):
        self.messages, self.password, self.appended, self.literal = list(messages), password, [], None
        FakeIMAP.instances.append(self)

    def login(self, user, pw):
        if pw != self.password:
            raise imaplib.IMAP4.error("[AUTHENTICATIONFAILED] Invalid credentials")
        return "OK", [b"ok"]

    def list(self):
        return "OK", [b'(\\HasNoChildren) "/" "INBOX"', b'(\\All \\HasNoChildren) "/" "[Gmail]/V&AWE-etky spr&AOE-vy"',
                      b'(\\Drafts \\HasNoChildren) "/" "[Gmail]/Koncepty"']

    def select(self, box, readonly=False):
        self.selected = box
        return "OK", [b"1"]

    def uid(self, cmd, *args):
        if cmd == "SEARCH":
            if "X-GM-THRID" in args:
                ids = [m["uid"] for m in self.messages if m["thrid"] == args[-1]]
            else:
                self.query = self.literal.decode()
                ids = [m["uid"] for m in self.messages]
            return "OK", [" ".join(ids).encode()]
        wanted = args[0].split(",")
        data = []
        for m in self.messages:
            if m["uid"] in wanted:
                data.append((f"{m['uid']} (X-GM-THRID {m['thrid']} X-GM-MSGID 9{m['uid']} UID {m['uid']} BODY[] {{{len(m['raw'])}}}".encode(), m["raw"]))
                data.append(b")")
        return "OK", data

    def append(self, box, flags, date, raw):
        self.appended.append((box, flags, raw))
        return "OK", [b"APPEND completed"]

    def logout(self):
        return "BYE", [b""]


def fiktivne_vlakno():
    return [mail("11", "500", "Dopyt na fiktívny diel", "Fiktívny Zákazník <zakaznik@example.org>", "Mon, 05 Jan 2026 08:00:00 +0100",
                 "Dobrý deň,\nprosím ponuku na fiktívny diel A, 4 ks."),
            mail("12", "500", "Re: Dopyt na fiktívny diel", "firma@example.com", "Mon, 05 Jan 2026 09:00:00 +0100", "Doplňte výkres."),
            mail("13", "501", "Iný fiktívny dopyt", "Iný <iny@example.org>", "Tue, 06 Jan 2026 08:00:00 +0100", "", html=True)]


class StoreAndImportTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.store = P.Prevadzka(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_records_are_validated_and_stored_outside_git_paths(self):
        rec = self.store.save("sklad", {"id": "s-1", "name": "Fiktívna položka", "qty": 2.0})
        self.assertTrue((Path(self._tmp.name) / "_eos" / "prevadzka" / "sklad" / "s-1.json").is_file())
        self.assertEqual(self.store.get("sklad", "s-1")["qty"], 2.0)
        self.assertTrue(rec["createdAt"].endswith("Z"))
        cases = {"zlý-stav": ("ponuky", {"id": "q-1", "status": "hotovo", "items": []}),
                 "záporné-množstvo": ("sklad", {"id": "s-2", "name": "x", "qty": -1}),
                 "neznáme-pole": ("dodavatelia", {"id": "d-1", "name": "x", "category": "y", "status": "used", "heslo": "z"})}
        for name, (kind, record) in cases.items():
            with self.subTest(name), self.assertRaises(P.RecordError):
                self.store.save(kind, record)
        for bad in ("../x", "A", ""):
            with self.subTest(bad), self.assertRaises(KeyError):
                self.store.get("sklad", bad)
        self.store.delete("sklad", "s-1")
        self.assertEqual(self.store.list("sklad"), [])

    def test_import_maps_prototype_statuses_and_keeps_existing(self):
        export = {
            "suppliers": [{"id": "fiktivny-a", "name": "Fiktívny A", "category": "Kategória", "status": "Používame", "web": "https://example.com", "updatedAt": "x"}],
            "kb": [{"id": "k1", "title": "Fiktívne pravidlo", "category": "Iné", "source": "—", "content": "text"}],
            "quotes": [{"id": "q-1", "number": "CP 9001", "status": "Koncept v Gmaile", "items": [{"name": "Diel", "qty": "2", "unitPrice": "1,5", "basis": "KB"}],
                        "threadId": "abc"}],
            "orders": [{"id": "o-1", "status": "Čaká na materiál", "oitems": [{"name": "Diel", "qty": "2"}],
                        "materials": [{"name": "Tyč", "status": "Objednať"}], "operations": [{"part": "Diel", "minPerPiece": "", "done": True}]}],
            "stock": [{"id": "s-1", "name": "Tyč", "qty": "3", "minQty": ""}],
        }
        report = import_export(export, self.store)
        self.assertEqual({k: v["imported"] for k, v in report.items()}, {"dodavatelia": 1, "kb": 1, "sklad": 1, "ponuky": 1, "objednavky": 1})
        self.assertEqual(self.store.get("dodavatelia", "fiktivny-a")["status"], "used")
        self.assertIsNone(self.store.get("kb", "k1")["source"])
        q = self.store.get("ponuky", "q-1")
        self.assertEqual((q["status"], q["items"][0]["unitPrice"], q["items"][0]["note"]), ("gmail_draft", 1.5, "návrh ceny: KB"))
        o = self.store.get("objednavky", "o-1")
        self.assertEqual((o["status"], o["materials"][0]["status"], o["items"][0]["qty"]), ("waiting_material", "to_order", 2.0))
        again = import_export(export, self.store)
        self.assertEqual(again["dodavatelia"], {"imported": 0, "skipped": 1, "failed": 0})


class GmailTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cfg = Path(self._tmp.name) / "cfg" / "gmail.json"

    def tearDown(self):
        self._tmp.cleanup()

    def gmail(self, messages=(), password=PASSWORD):
        self.imap = FakeIMAP(messages)
        return G.Gmail("firma@example.com", password, lambda: self.imap)

    def test_search_groups_threads_and_reads_bodies(self):
        g = self.gmail(fiktivne_vlakno())
        threads = g.search("dopyt čšť")
        self.assertEqual(self.imap.query, "dopyt čšť")  # diakritika ide ako UTF-8 literál
        self.assertEqual(self.imap.selected, '"[Gmail]/V&AWE-etky spr&AOE-vy"')  # priečinok podľa \\All, nie podľa jazyka
        self.assertEqual([(t["threadId"], t["count"]) for t in threads], [("501", 1), ("500", 2)])
        self.assertEqual(threads[1]["subject"], "Dopyt na fiktívny diel")  # predmet z prvej správy vlákna
        msgs = g.thread("500")
        self.assertEqual([m["messageId"] for m in msgs], ["<m11@example.org>", "<m12@example.org>"])
        self.assertIn("fiktívny diel A", msgs[0]["text"])
        html = g.thread("501")[0]["text"]
        self.assertIn("prosím ponuku", html)
        self.assertNotIn("<", html)
        self.assertNotIn("x()", html)
        with self.assertRaises(G.GmailError):
            g.thread("1 OR 1")

    def test_draft_is_appended_as_reply_and_never_sent(self):
        g = self.gmail()
        g.create_draft("Fiktívny <zakaznik@example.org>", "Re: Dopyt", "Text ponuky", in_reply_to="<m12@example.org>")
        box, flags, raw = self.imap.appended[0]
        self.assertEqual((box, flags), ('"[Gmail]/Koncepty"', "\\Draft"))
        self.assertIn(b"In-Reply-To: <m12@example.org>", raw)
        self.assertIn(b"To: zakaznik@example.org", raw)
        self.assertFalse(hasattr(g, "send"))
        with self.assertRaises(G.GmailError):
            g.create_draft("bez zavináča", "x", "y")

    def test_wrong_password_gives_readable_error_without_secret(self):
        g = self.gmail(password="zle heslo")
        with self.assertRaises(G.GmailError) as e:
            g.test()
        self.assertIn("heslo aplikácie", str(e.exception))
        self.assertNotIn("zleheslo", str(e.exception))

    def test_config_file_is_private_and_removable(self):
        G.save_config("firma@example.com", "abcdefghijklmnop", self.cfg)
        self.assertEqual(stat.S_IMODE(self.cfg.stat().st_mode), 0o600)
        self.assertEqual(G.load_config(self.cfg)["email"], "firma@example.com")
        G.delete_config(self.cfg)
        self.assertIsNone(G.load_config(self.cfg))


@unittest.skipIf(TestClient is None, "UI závislosti nie sú nainštalované (pip install -e .[ui])")
class PrevadzkaUiTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.intake, self.cfg = base / "intake", base / "cfg" / "gmail.json"
        self.imap = FakeIMAP(fiktivne_vlakno())
        self.client = TestClient(create_app(ROOT, self.intake, base / "spravy", gmail_config=self.cfg, imap_factory=lambda: self.imap,
                                            allowed_hosts={"eos.fiktivna-siet.ts.net"}))
        self.store = P.Prevadzka(self.intake)

    def tearDown(self):
        self._tmp.cleanup()

    def serve_client(self, login):
        origin = "https://eos.fiktivna-siet.ts.net"
        self.enterContext(patch.dict(os.environ, {
            "EOS_SERVE_ORIGIN": origin, "EOS_MAIL_SENDERS": "owner@example.org",
            "EOS_CHAT_USERS": "owner@example.org,brother@example.org",
            "ANTHROPIC_API_KEY": "fake-key", "EOS_CLAUDE_MODEL": "fake-model",
        }))
        return TestClient(self.client.app, base_url=origin, headers={
            "origin": origin, "tailscale-user-login": login,
        }, follow_redirects=False, client=("127.0.0.1", 50000))

    def test_send_requires_matching_preview_and_rejects_repeated_confirmation(self):
        client = self.serve_client("owner@example.org")
        G.save_config("firma@example.com", PASSWORD, self.cfg)
        self.store.save("ponuky", {"id": "cp-test", "status": "draft", "items": [],
                                  "email": "recipient@example.org", "subject": "Test",
                                  "gmail": {"messageId": "<original@example.org>"}})
        url = "/ponuka/cp-test/odoslat"
        self.assertEqual(client.get(url, headers={"tailscale-user-login": "brother@example.org"}).status_code, 403)
        preview = client.get(url)
        self.assertEqual(preview.status_code, 200)
        fingerprint = re.search(r'name="fingerprint" value="([a-f0-9]+)"', preview.text)[1]
        with patch.object(G.smtplib, "SMTP_SSL") as smtp:
            self.assertEqual(client.post(url, data={"fingerprint": "old"}).status_code, 409)
            smtp.assert_not_called()
            form = {"fingerprint": fingerprint}
            self.assertEqual(client.post(url, data=form).status_code, 303)
            self.assertEqual(client.post(url, data=form).status_code, 409)
            smtp.return_value.send_message.assert_called_once()
            message = smtp.return_value.send_message.call_args.args[0]
            self.assertEqual(str(message["To"]), "recipient@example.org")
            self.assertEqual(str(message["Subject"]), "Re: Test")
            self.assertEqual(str(message["In-Reply-To"]), "<original@example.org>")
        self.assertEqual(self.store.get("ponuky", "cp-test")["status"], "sent")

    def test_claude_chat_continues_and_is_private_per_tailscale_identity(self):
        client = self.serve_client("owner@example.org")
        sdk = SimpleNamespace(Anthropic=MagicMock(), APIError=RuntimeError)
        messages = sdk.Anthropic.return_value.__enter__.return_value.messages
        messages.create.return_value = SimpleNamespace(content=[
            SimpleNamespace(type="text", text="<b>Fiktívny návrh</b>"),
        ])
        with patch.dict(sys.modules, {"anthropic": sdk}):
            first = client.post("/chat", data={"prompt": "Napíš pozdrav"})
            self.assertEqual(first.status_code, 303)
            url = first.headers["location"]
            session = url.split("=")[-1]
            self.assertIn("&lt;b&gt;Fiktívny návrh&lt;/b&gt;", client.get(url).text)
            other = {"tailscale-user-login": "brother@example.org"}
            self.assertEqual(client.get(url, headers=other).status_code, 404)
            self.assertEqual(client.post("/chat", headers=other, data={"session": session, "prompt": "Ahoj"}).status_code, 404)
            self.assertEqual(client.post("/chat", data={"session": session, "prompt": "Skráť ho"}).status_code, 303)
        self.assertEqual([m["role"] for m in messages.create.call_args.kwargs["messages"]],
                         ["user", "assistant", "user"])

    def test_gmail_order_prefills_job_and_keeps_reviewed_source_once(self):
        G.save_config("firma@example.com", PASSWORD, self.cfg)
        self.imap.messages = [mail(
            "22", "502", "Objednávka fiktívnych držiakov", "Demo <demo@example.org>",
            "Mon, 05 Jan 2026 08:00:00 +0100",
            "Číslo objednávky: DEMO-2\nMnožstvo: 2 ks\nTermín dodania: podľa dohody",
        )]
        self.assertIn("Objednávka fiktívnych držiakov", self.client.get("/nova?hladat=1").text)
        preview = self.client.get("/nova?vlakno=502")
        self.assertIn('name="number" maxlength="300" value="DEMO-2"', preview.text)
        self.assertIn('name="quantity" maxlength="300" value="2 ks"', preview.text)
        form = {"vlakno": "502", "nazov": "Overená ukážka", "kto": "Marco", "number": "DEMO-2",
                "customer": "Upravený zákazník", "quantity": "2 ks"}
        first = self.client.post("/nova", data=form, files={"subory": ("vykres.txt", b"demo")},
                                 follow_redirects=False)
        self.assertEqual(first.status_code, 303)
        url = first.headers["location"]
        self.assertEqual(self.client.post("/nova", data=form, follow_redirects=False).headers["location"], url)
        self.assertIn("Upravený zákazník", self.client.get(url).text)
        files = list(self.intake.glob("JOB-*/objednavka/objednavka-*.txt"))
        self.assertEqual(len(files), 1)
        self.assertIn("Pôvodný e-mail", files[0].read_text())
        self.assertTrue(files[0].parents[1].joinpath("vykresy/vykres.txt").exists())

    def test_ai_supplier_uses_private_proposal_and_existing_save_form(self):
        client = self.serve_client("owner@example.org")
        sdk = SimpleNamespace(Anthropic=MagicMock(), APIError=RuntimeError)
        messages = sdk.Anthropic.return_value.__enter__.return_value.messages
        messages.create.return_value = SimpleNamespace(content=[SimpleNamespace(
            type="tool_use", name="propose_supplier",
            input={"name": "Ukážkový dodávateľ", "category": "Náradie",
                   "web": "javascript:alert(1)", "status": "used"},
        )])
        with patch.dict(sys.modules, {"anthropic": sdk}):
            url = client.post("/chat", data={"prompt": "Pridaj dodávateľa"}).headers["location"]
        self.assertEqual(self.store.list("dodavatelia"), [])
        self.assertIn("Skontrolovať dodávateľa", client.get(url).text)
        draft = "/dodavatelia/novy?chat=" + url.split("=")[-1] + "&turn=1"
        self.assertEqual(client.get(draft, headers={"tailscale-user-login": "brother@example.org"}).status_code, 404)
        form = client.get(draft)
        self.assertIn("Ukážkový dodávateľ", form.text)
        self.assertNotIn("javascript:alert(1)", form.text)
        self.assertEqual(client.post("/dodavatelia/novy", data={
            "name": "Ukážkový dodávateľ", "category": "Náradie", "status": "verify",
        }).status_code, 303)
        self.assertEqual(self.store.list("dodavatelia")[0]["status"], "verify")

    def test_chat_feedback_is_saved_for_robino(self):
        client = self.serve_client("brother@example.org")
        response = client.post("/chat/navrh", data={"topic": "Fiktívne zlepšenie", "text": "Pridať filter."})
        self.assertEqual(response.headers["location"], "/chat?submitted=1")
        self.assertIn("Fiktívne zlepšenie", client.get("/stav").text)

    def test_personal_gmail_connect_and_disconnect_leave_other_identity_unchanged(self):
        client = self.serve_client("owner@example.org")
        self.enterContext(patch.dict(os.environ, {"EOS_GMAIL_USERS": "owner@example.org,brother@example.org"}))
        other = {"tailscale-user-login": "brother@example.org"}
        login = {"email": "owner-mail@example.org", "heslo": PASSWORD}
        self.assertEqual(client.post("/gmail", data=login).status_code, 303)
        self.assertNotIn(login["email"], client.get("/gmail", headers=other).text)
        brother_login = {**login, "email": "brother-mail@example.org"}
        self.assertEqual(client.post("/gmail", headers=other, data=brother_login).status_code, 303)
        self.assertIn(brother_login["email"], client.get("/gmail", headers=other).text)
        self.assertEqual(client.post("/gmail", headers=other, data={"akcia": "odpojit"}).status_code, 303)
        self.assertIn(login["email"], client.get("/gmail").text)
        self.assertFalse(self.cfg.exists())

    def test_gmail_connects_only_with_valid_app_password(self):
        r = self.client.post("/gmail", data={"email": "firma@example.com", "heslo": "zle"})
        self.assertEqual(r.status_code, 422)
        self.assertFalse(self.cfg.exists())
        r = self.client.post("/gmail", data={"email": "firma@example.com", "heslo": PASSWORD}, follow_redirects=False)
        self.assertEqual(r.status_code, 303)
        self.assertEqual(G.load_config(self.cfg)["appPassword"], PASSWORD.replace(" ", ""))
        self.assertNotIn(PASSWORD.replace(" ", ""), self.client.get("/gmail").text)
        self.client.post("/gmail", data={"akcia": "odpojit"})
        self.assertFalse(self.cfg.exists())

    def test_quote_from_gmail_to_draft_to_order(self):
        G.save_config("firma@example.com", PASSWORD, self.cfg)
        self.assertIn("Dopyt na fiktívny diel", self.client.get("/ponuky?hladat=1").text)
        r = self.client.post("/ponuky/z-gmailu", data={"vlakno": "500"}, follow_redirects=False)
        url = r.headers["location"]
        self.assertEqual(self.client.post("/ponuky/z-gmailu", data={"vlakno": "500"}, follow_redirects=False).headers["location"], url)
        q = self.store.list("ponuky")[0]
        self.assertEqual((q["email"], q["customer"], q["gmail"]["messageId"]), ("zakaznik@example.org", "Fiktívny Zákazník", "<m12@example.org>"))
        self.assertIn("prosím ponuku na fiktívny diel A", self.client.get(url).text)
        form = {"number": "CP 9001", "email": "zakaznik@example.org", "status": "draft",
                "items-0-name": "Fiktívny diel A", "items-0-qty": "4", "items-0-unit": "ks", "items-0-unitPrice": "12,50"}
        self.client.post(url, data={**form, "akcia": "koncept"})
        draft = email.message_from_bytes(self.imap.appended[-1][2], policy=email.policy.default)
        self.assertEqual((draft["Subject"], draft["In-Reply-To"]), ("Re: Dopyt na fiktívny diel", "<m12@example.org>"))
        self.assertIn("50,00 €", draft.get_content())  # 4 × 12,50
        self.assertEqual(self.store.list("ponuky")[0]["status"], "gmail_draft")
        r = self.client.post(url, data={**form, "status": "accepted", "akcia": "objednavka"}, follow_redirects=False)
        o = self.store.list("objednavky")[0]
        self.assertEqual((r.headers["location"], o["number"], o["items"][0]["qty"]), (f"/objednavka/{o['id']}", "OBJ 9001", 4.0))

    def test_line_rows_add_remove_and_reject_bad_numbers(self):
        url = self.client.post("/ponuky/nova", follow_redirects=False).headers["location"]
        rows = {"items-0-name": "A", "items-1-name": "B", "items-2-name": "C"}
        self.client.post(url, data={**rows, "akcia": "odobrat-items-1"})
        self.assertEqual([i["name"] for i in self.store.list("ponuky")[0]["items"]], ["A", "C"])
        r = self.client.post(url, data={"items-0-name": "A", "items-0-qty": "dva", "akcia": "ulozit"})
        self.assertEqual(r.status_code, 422)
        self.assertIn("nie je číslo", r.text)

    def test_order_checks_stock_and_exports_valid_price_search_input(self):
        self.store.save("sklad", {"id": "s-1", "name": "Fiktívna tyč", "qty": 5.0, "unit": "ks"})
        self.store.save("dodavatelia", {"id": "fiktivny-a", "name": "Fiktívny A", "category": "X", "status": "used", "web": "https://www.example.com/sk"})
        self.store.save("dodavatelia", {"id": "bez-webu", "name": "Bez webu", "category": "X", "status": "used"})
        o = self.store.save("objednavky", {"id": "o-1", "status": "accepted", "items": [], "materials": [], "operations": []})
        mats = {"materials-0-name": "Fiktívna tyč", "materials-0-qty": "2", "materials-0-status": "verify",
                "materials-1-name": "Fiktívna rúra", "materials-1-qty": "1", "materials-1-status": "verify"}
        self.client.post(f"/objednavka/{o['id']}", data={**mats, "akcia": "sklad"})
        self.assertEqual([m["status"] for m in self.store.get("objednavky", "o-1")["materials"]], ["in_stock", "to_order"])
        r = self.client.post(f"/objednavka/{o['id']}", data={**mats, "materials-0-status": "in_stock", "materials-1-status": "to_order", "akcia": "ceny"})
        data = r.json()
        schema = json.loads((ROOT / "scripts" / "ai" / "cenovy_dopyt.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(data)), [])
        self.assertEqual(([i["text"] for i in data["items"]], [s["domain"] for s in data["suppliers"]]), (["Fiktívna rúra"], ["example.com"]))

    def test_records_pages_and_foreign_origin(self):
        r = self.client.post("/kb/novy", data={"title": "Fiktívne pravidlo", "category": "Iné", "source": "P", "content": "text"}, follow_redirects=False)
        self.assertEqual(r.status_code, 303)
        self.assertIn("Fiktívne pravidlo", self.client.get("/kb").text)
        r = self.client.post("/dodavatelia/novy", data={"name": "X", "category": "Y", "status": "used", "searchUrl": "https://example.com/s"})
        self.assertEqual(r.status_code, 422)  # vyhľadávanie bez {q}
        self.assertEqual(self.client.post("/sklad/novy", data={"name": "x"}, headers={"origin": "https://eos.fiktivna-siet.ts.net"},
                                          follow_redirects=False).status_code, 303)
        self.assertEqual(self.client.post("/sklad/novy", data={"name": "x"}, headers={"origin": "https://cudzia.example.net"}).status_code, 403)


if __name__ == "__main__":
    unittest.main()
