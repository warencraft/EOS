"""Vyhľadanie cien u dodávateľov cez Claude API (ADR-0024).

Vstup: položky materiálu a dodávatelia s doménami (`cenovy_dopyt.schema.json`).
Výstup: návrh cien s odkazom, citátom a časom zistenia (`cenovy_navrh.schema.json`).

Claude smie hľadať a čítať iba na doménach dodávateľov zo vstupu. Výsledok je vždy návrh:
do ponuky ho preberá Marco, znalosťou EOS sa stane až cez schválený kontrakt (ADR-0024 bod 5).

Príkazový riadok:
    python -m scripts.ai.hladanie_cien vstup.json [-o navrh.json] [--model MODEL]

Potrebuje voliteľnú závislosť `.[ai]` (anthropic) a premennú prostredia ANTHROPIC_API_KEY.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
INPUT_SCHEMA = HERE / "cenovy_dopyt.schema.json"
OUTPUT_SCHEMA = HERE / "cenovy_navrh.schema.json"
FORMAT_VERSION = "0.1.0"

DEFAULT_MODEL = "claude-sonnet-5-5"
WEB_SEARCH_TOOL = "web_search_20250305"
WEB_FETCH_TOOL = "web_fetch_20250910"
RESULT_TOOL_NAME = "zapis_navrh"
MAX_REQUESTS = 12
MAX_TOKENS = 8000
FETCH_MAX_CONTENT_TOKENS = 20000
PRICE_STATUSES = ("verejna", "na_dopyt", "nenajdene")

SYSTEM_PROMPT = """Si nákupca strojárskej firmy. Hľadáš ceny položiek u dodávateľov zo zoznamu.
Pravidlá:
- Hľadaj a čítaj iba na weboch dodávateľov zo zoznamu.
- Cenu zapíš iba vtedy, keď ju vidíš na stránke produktu. Nevymýšľaj ani neodhaduj ceny, rozmery ani materiály.
- Ak produkt sedí, ale cena nie je verejná (prihlásenie, dopyt), použi priceStatus "na_dopyt" a uveď odkaz.
- Ak produkt u dodávateľa nenájdeš, použi priceStatus "nenajdene".
- Do "quote" skopíruj krátky presný úryvok zo stránky (názov produktu a cena), najviac 300 znakov.
- Mena ako ISO kód (EUR, CZK). vatIncluded true/false iba ak to stránka uvádza, inak null.
- Na konci zavolaj nástroj zapis_navrh raz, so všetkými položkami a dodávateľmi, ktoré si skúšal."""

RESULT_TOOL = {
    "name": RESULT_TOOL_NAME,
    "description": "Zapíše výsledok hľadania cien. Zavolaj raz na konci.",
    "input_schema": {
        "type": "object",
        "required": ["items"],
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["itemId", "offers"],
                    "properties": {
                        "itemId": {"type": "string"},
                        "offers": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["supplierId", "priceStatus"],
                                "properties": {
                                    "supplierId": {"type": "string"},
                                    "priceStatus": {"type": "string", "enum": list(PRICE_STATUSES)},
                                    "url": {"type": ["string", "null"]},
                                    "productName": {"type": ["string", "null"]},
                                    "price": {"type": ["number", "null"]},
                                    "currency": {"type": ["string", "null"]},
                                    "priceUnit": {"type": ["string", "null"]},
                                    "vatIncluded": {"type": ["boolean", "null"]},
                                    "availability": {"type": ["string", "null"]},
                                    "quote": {"type": ["string", "null"]},
                                },
                            },
                        },
                    },
                },
            }
        },
    },
}


class InputError(ValueError):
    """Vstup nezodpovedá cenovy_dopyt.schema.json."""


class SearchError(RuntimeError):
    """Claude nevrátil použiteľný výsledok."""


def _validator(path: Path) -> Draft202012Validator:
    return Draft202012Validator(json.loads(path.read_text(encoding="utf-8")), format_checker=FormatChecker())


def validate_input(data: Any) -> None:
    errors = sorted(_validator(INPUT_SCHEMA).iter_errors(data), key=lambda e: list(e.absolute_path))
    if errors:
        raise InputError("; ".join(f"{'/'.join(map(str, e.absolute_path)) or '(koreň)'}: {e.message}" for e in errors))
    for key in ("items", "suppliers"):
        ids = [x["id"] for x in data[key]]
        if len(ids) != len(set(ids)):
            raise InputError(f"{key}: id sa opakuje")


def output_errors(navrh: dict) -> list[str]:
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in _validator(OUTPUT_SCHEMA).iter_errors(navrh)]


def _host(domain: str) -> str:
    return domain.split("/", 1)[0].lower()


def url_matches_domain(url: str | None, domain: str) -> bool:
    """URL patrí doméne dodávateľa (aj jej subdoménam) a pri doméne s cestou aj danej ceste."""
    if not url:
        return False
    try:
        u = urlparse(url)
    except ValueError:
        return False
    if u.scheme not in ("http", "https") or not u.hostname:
        return False
    host, base = u.hostname.lower(), _host(domain)
    if host != base and not host.endswith("." + base) and host != "www." + base:
        return False
    prefix = domain[len(base):]
    return not prefix or (u.path or "/").startswith(prefix)


def build_request(dopyt: dict, model: str = DEFAULT_MODEL, max_searches: int = 10, max_fetches: int = 10) -> dict:
    """Parametre pre client.messages.create. Nástroje sú obmedzené na domény dodávateľov (ADR-0024 bod 2)."""
    domains = sorted({s["domain"] for s in dopyt["suppliers"]})
    lines = ["Položky:"]
    for it in dopyt["items"]:
        qty = f" ({it['quantity']:g} {it.get('unit', '')})".rstrip() if "quantity" in it else ""
        lines.append(f"- {it['id']}: {it['text']}{qty}")
    lines.append("\nDodávatelia (id, názov, web):")
    for s in dopyt["suppliers"]:
        lines.append(f"- {s['id']}: {s['name']}, https://{s['domain']}")
    lines.append("\nNájdi ceny každej položky u každého dodávateľa, ktorý ju môže mať, a zapíš výsledok nástrojom zapis_navrh.")
    return {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "system": SYSTEM_PROMPT,
        "tools": [
            {"type": WEB_SEARCH_TOOL, "name": "web_search", "max_uses": max_searches, "allowed_domains": domains},
            {"type": WEB_FETCH_TOOL, "name": "web_fetch", "max_uses": max_fetches, "allowed_domains": domains,
             "max_content_tokens": FETCH_MAX_CONTENT_TOKENS},
            RESULT_TOOL,
        ],
        "messages": [{"role": "user", "content": "\n".join(lines)}],
    }


def _get(obj: Any, key: str, default: Any = None) -> Any:
    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)


def _as_param(block: Any) -> Any:
    """Blok odpovede späť do správy (pri pause_turn sa posiela nezmenený)."""
    return block if isinstance(block, dict) else block.model_dump(exclude_none=True)


def _clean_str(v: Any, limit: int = 300) -> str | None:
    if v is None:
        return None
    s = " ".join(str(v).split())
    return s[:limit] or None


def normalize(raw: dict, dopyt: dict, *, model: str, api_calls: int, now: datetime) -> dict:
    """Z výsledku Clauda urobí návrh podľa cenovy_navrh.schema.json a vyradí, čo pravidlám nezodpovedá."""
    stamp = now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    suppliers = {s["id"]: s for s in dopyt["suppliers"]}
    by_item: dict[str, list] = {}
    for it in raw.get("items") or []:
        if isinstance(it, dict):
            by_item.setdefault(str(it.get("itemId")), []).extend(o for o in (it.get("offers") or []) if isinstance(o, dict))
    items = []
    for it in dopyt["items"]:
        offers, seen = [], set()
        for o in by_item.get(it["id"], []):
            sup = suppliers.get(str(o.get("supplierId")))
            if not sup or sup["id"] in seen:
                continue  # neznámy alebo opakovaný dodávateľ
            seen.add(sup["id"])
            notes: list[str] = []
            status = o.get("priceStatus") if o.get("priceStatus") in PRICE_STATUSES else "nenajdene"
            url = _clean_str(o.get("url"), 2000)
            if url and not url_matches_domain(url, sup["domain"]):
                notes.append("odkaz mimo webu dodávateľa bol vyradený")
                url = None
            price = o.get("price")
            price = float(price) if isinstance(price, (int, float)) and not isinstance(price, bool) and price >= 0 else None
            currency = _clean_str(o.get("currency"), 3)
            currency = currency.upper() if currency and len(currency) == 3 and currency.isalpha() else None
            if status == "verejna" and (price is None or currency is None or url is None):
                notes.append("cena bez odkazu, meny alebo čísla nie je overiteľná")
                status = "na_dopyt" if url else "nenajdene"
            if status != "verejna":
                price = None
            vat = o.get("vatIncluded")
            offers.append({
                "supplierId": sup["id"], "supplierName": sup["name"], "priceStatus": status, "url": url,
                "productName": _clean_str(o.get("productName"), 200), "price": price,
                "currency": currency if price is not None else None, "priceUnit": _clean_str(o.get("priceUnit"), 40),
                "vatIncluded": vat if isinstance(vat, bool) else None, "availability": _clean_str(o.get("availability"), 120),
                "quote": _clean_str(o.get("quote"), 500), "retrievedAt": stamp, "notes": notes,
            })
        items.append({"itemId": it["id"], "text": it["text"], "quantity": it.get("quantity"), "unit": it.get("unit"), "offers": offers})
    return {"formatVersion": FORMAT_VERSION, "status": "navrh", "createdAt": stamp, "model": model, "apiCalls": api_calls, "items": items}


def search(dopyt: dict, client: Any, *, model: str = DEFAULT_MODEL, max_searches: int = 10, max_fetches: int = 10,
           now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> dict:
    """Spustí hľadanie. `client` je anthropic.Anthropic() alebo objekt s rovnakým `messages.create`."""
    validate_input(dopyt)
    req = build_request(dopyt, model, max_searches, max_fetches)
    messages = req.pop("messages")
    for calls in range(1, MAX_REQUESTS + 1):
        resp = client.messages.create(messages=messages, **req)
        content = list(_get(resp, "content", []) or [])
        for block in content:
            if _get(block, "type") == "tool_use" and _get(block, "name") == RESULT_TOOL_NAME:
                raw = _get(block, "input") or {}
                return normalize(raw if isinstance(raw, dict) else {}, dopyt, model=model, api_calls=calls, now=now())
        stop = _get(resp, "stop_reason")
        messages.append({"role": "assistant", "content": [_as_param(b) for b in content]})
        if stop == "pause_turn":
            continue  # server nástroje pokračujú v ďalšej požiadavke
        if stop == "max_tokens":
            raise SearchError("Odpoveď presiahla limit dĺžky. Skús menej položiek naraz.")
        messages.append({"role": "user", "content": f"Zapíš výsledok nástrojom {RESULT_TOOL_NAME}."})
    raise SearchError(f"Claude nevrátil výsledok ani po {MAX_REQUESTS} požiadavkách.")


def _make_client():
    try:
        import anthropic
    except ImportError:
        raise SystemExit("Chýba balík anthropic. Nainštaluj: python -m pip install -e '.[ai]'")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Chýba premenná prostredia ANTHROPIC_API_KEY.")
    return anthropic.Anthropic()


def main(argv: list[str] | None = None, client: Any = None) -> int:
    p = argparse.ArgumentParser(prog="python -m scripts.ai.hladanie_cien", description="Návrh cien od dodávateľov (ADR-0024).")
    p.add_argument("vstup", type=Path, help="JSON podľa scripts/ai/cenovy_dopyt.schema.json")
    p.add_argument("-o", "--vystup", type=Path, help="kam zapísať návrh (predvolene na štandardný výstup)")
    p.add_argument("--model", default=os.environ.get("EOS_AI_MODEL", DEFAULT_MODEL))
    p.add_argument("--max-searches", type=int, default=10)
    p.add_argument("--max-fetches", type=int, default=10)
    a = p.parse_args(argv)
    try:
        dopyt = json.loads(a.vstup.read_text(encoding="utf-8"))
        validate_input(dopyt)
    except (OSError, json.JSONDecodeError, InputError) as e:
        print(f"Neplatný vstup: {e}", file=sys.stderr)
        return 2
    try:
        navrh = search(dopyt, client or _make_client(), model=a.model, max_searches=a.max_searches, max_fetches=a.max_fetches)
    except SearchError as e:
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:  # chyba Claude API (sieť, kľúč, limity); bez výpisu kľúča
        print(f"Chyba Claude API: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    text = json.dumps(navrh, ensure_ascii=False, indent=2) + "\n"
    if a.vystup:
        a.vystup.write_text(text, encoding="utf-8")
        print(f"Návrh zapísaný do {a.vystup} ({navrh['apiCalls']} volaní API).", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
