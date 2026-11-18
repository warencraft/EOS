"""ADR-0024: vyhľadanie cien u dodávateľov (scripts/ai/hladanie_cien.py).

Bez skutočného Claude API: náhradný klient vracia pripravené odpovede. Dodávatelia, domény,
položky a ceny sú fiktívne (example.com, example.org). Testy overujú obmedzenie na domény,
priebeh požiadaviek a pravidlá návrhu, nie technické hodnoty.
"""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from scripts.ai import hladanie_cien as H

NOW = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)


def dopyt():
    return json.loads((Path(H.__file__).parent / "priklad_vstup.json").read_text(encoding="utf-8"))


def resp(stop, *blocks):
    return SimpleNamespace(stop_reason=stop, content=list(blocks))


def result(items):
    return SimpleNamespace(type="tool_use", id="toolu_1", name=H.RESULT_TOOL_NAME, input={"items": items})


def offer(**kw):
    base = {"supplierId": "dodavatel-a", "priceStatus": "verejna", "url": "https://example.com/p/1",
            "productName": "Fiktívny produkt", "price": 12.5, "currency": "eur", "priceUnit": "ks",
            "vatIncluded": False, "availability": "skladom", "quote": "Fiktívny produkt 12,50 €"}
    base.update(kw)
    return base


class FakeClient:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.calls.append(deepcopy(kw))
        return self.responses.pop(0)


class HladanieCienTest(unittest.TestCase):
    def run_search(self, *responses):
        client = FakeClient(*responses)
        return H.search(dopyt(), client, now=lambda: NOW), client

    def test_tools_are_limited_to_supplier_domains_and_input_holds_no_job_data(self):
        # ADR-0024 bod 2 a 6
        req = H.build_request(dopyt())
        search_tool, fetch_tool, result_tool = req["tools"]
        self.assertEqual(search_tool["type"], H.WEB_SEARCH_TOOL)
        self.assertEqual(fetch_tool["type"], H.WEB_FETCH_TOOL)
        for tool in (search_tool, fetch_tool):
            self.assertEqual(tool["allowed_domains"], ["example.com", "shop.example.org"])
            self.assertNotIn("blocked_domains", tool)
        self.assertEqual(result_tool["name"], H.RESULT_TOOL_NAME)
        text = req["messages"][0]["content"]
        self.assertIn("https://shop.example.org", text)  # web_fetch smie čítať iba URL z používateľskej správy

    def test_invalid_input_is_rejected_before_any_api_call(self):
        cases = {
            "zakaznik-v-poziadavke": lambda d: d.update(customer="Fiktívny zákazník"),
            "doména-so-schemou": lambda d: d["suppliers"][0].update(domain="https://example.com"),
            "prázdne-položky": lambda d: d.update(items=[]),
            "opakované-id": lambda d: d["items"].append(dict(d["items"][0])),
            "nulové-množstvo": lambda d: d["items"][0].update(quantity=0),
        }
        for name, mutate in cases.items():
            with self.subTest(name):
                d = dopyt(); mutate(d)
                client = FakeClient()
                with self.assertRaises(H.InputError):
                    H.search(d, client)
                self.assertEqual(client.calls, [])

    def test_pause_turn_is_resent_unchanged_and_result_is_valid_proposal(self):
        paused = SimpleNamespace(type="server_tool_use", id="srvtoolu_1", name="web_search", input={"query": "fiktívny"},
                                 model_dump=lambda exclude_none=True: {"type": "server_tool_use", "id": "srvtoolu_1",
                                                                       "name": "web_search", "input": {"query": "fiktívny"}})
        navrh, client = self.run_search(resp("pause_turn", paused), resp("tool_use", result([{"itemId": "P1", "offers": [offer()]}])))
        self.assertEqual(len(client.calls), 2)
        self.assertEqual(client.calls[1]["messages"][-1], {"role": "assistant", "content": [paused.model_dump()]})
        self.assertEqual(H.output_errors(navrh), [])
        self.assertEqual((navrh["status"], navrh["apiCalls"]), ("navrh", 2))
        o = navrh["items"][0]["offers"][0]
        self.assertEqual((o["priceStatus"], o["price"], o["currency"], o["retrievedAt"]), ("verejna", 12.5, "EUR", "2026-01-02T03:04:05Z"))
        self.assertEqual(navrh["items"][1]["offers"], [])  # položka bez výsledku ostáva prázdna, nie vymyslená

    def test_unverifiable_offers_are_downgraded_or_dropped(self):
        offers = [
            offer(url="https://inde.example.net/p/1"),                      # mimo domény dodávateľa
            offer(supplierId="dodavatel-b", url="https://shop.example.org/x", price=None),  # verejná bez ceny
            offer(supplierId="neznamy"),                                    # dodávateľ mimo vstupu
            offer(supplierId="dodavatel-b", priceStatus="na_dopyt"),        # opakovaný dodávateľ
        ]
        navrh, _ = self.run_search(resp("tool_use", result([{"itemId": "P1", "offers": offers}, {"itemId": "X9", "offers": [offer()]}])))
        self.assertEqual(H.output_errors(navrh), [])
        got = [(o["supplierId"], o["priceStatus"], o["url"], o["price"]) for o in navrh["items"][0]["offers"]]
        self.assertEqual(got, [("dodavatel-a", "nenajdene", None, None), ("dodavatel-b", "na_dopyt", "https://shop.example.org/x", None)])
        self.assertEqual([i["itemId"] for i in navrh["items"]], ["P1", "P2"])

    def test_missing_result_is_requested_then_fails_after_limit(self):
        text = SimpleNamespace(type="text", text="hotovo", model_dump=lambda exclude_none=True: {"type": "text", "text": "hotovo"})
        navrh, client = self.run_search(resp("end_turn", text), resp("tool_use", result([])))
        self.assertIn(H.RESULT_TOOL_NAME, client.calls[1]["messages"][-1]["content"])
        self.assertEqual(navrh["apiCalls"], 2)
        with self.assertRaises(H.SearchError):
            self.run_search(*[resp("end_turn", text) for _ in range(H.MAX_REQUESTS)])

    def test_command_line_writes_proposal_and_reports_bad_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            vstup, vystup = Path(tmp) / "vstup.json", Path(tmp) / "navrh.json"
            vstup.write_text(json.dumps(dopyt()), encoding="utf-8")
            client = FakeClient(resp("tool_use", result([{"itemId": "P2", "offers": [offer(supplierId="dodavatel-b", priceStatus="nenajdene", url=None)]}])))
            with redirect_stderr(io.StringIO()):
                self.assertEqual(H.main([str(vstup), "-o", str(vystup), "--model", "fiktivny-model"], client=client), 0)
            navrh = json.loads(vystup.read_text(encoding="utf-8"))
            self.assertEqual((navrh["model"], navrh["items"][1]["offers"][0]["priceStatus"]), ("fiktivny-model", "nenajdene"))
            vstup.write_text("{}", encoding="utf-8")
            err = io.StringIO()
            with redirect_stderr(err), redirect_stdout(io.StringIO()):
                self.assertEqual(H.main([str(vstup)], client=FakeClient()), 2)
            self.assertIn("Neplatný vstup", err.getvalue())


if __name__ == "__main__":
    unittest.main()
