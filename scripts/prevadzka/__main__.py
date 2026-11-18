"""Jednorazový import z prototypu EOS Zákazky na claude.ai (ADR-0025).

    python -m scripts.prevadzka import export.json [--intake intake] [--prepisat]

Súbor export.json má kľúče suppliers, kb, quotes, orders, stock v tvare prototypu.
Existujúce záznamy s rovnakým id sa bez --prepisat nemenia.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import Prevadzka, RecordError, slug

ROOT = Path(__file__).resolve().parents[2]
SUP = {"Na overenie": "verify", "Používame": "used", "Nepoužívame": "not_used"}
QST = {"Rozpracovaná": "draft", "Koncept v Gmaile": "gmail_draft", "Odoslaná": "sent", "Prijatá": "accepted", "Zamietnutá": "rejected"}
OST = {"Prijatá": "accepted", "Čaká na materiál": "waiting_material", "Vo výrobe": "in_production", "Hotová": "done", "Odoslaná": "shipped"}
MST = {"Overiť": "verify", "Na sklade": "in_stock", "Objednať": "to_order", "Objednané": "ordered", "Prijaté": "received"}


def _num(v):
    if v in (None, ""):
        return None
    try:
        n = float(str(v).replace(" ", "").replace(",", "."))
    except ValueError:
        return None
    return n if n >= 0 else None


def _s(v) -> str:
    return "" if v is None else str(v)


def _pick(rec: dict, keys) -> dict:
    return {k: _s(rec.get(k)) for k in keys if rec.get(k) not in (None, "")}


def _id(rec: dict, fallback: str) -> str:
    return slug(rec.get("id") or rec.get("name") or rec.get("title") or fallback, fallback)


def map_supplier(r):
    return {"id": _id(r, "dodavatel"), **_pick(r, ["name", "category", "supplies", "location", "web", "searchUrl", "email", "note"]),
            "status": SUP.get(r.get("status"), "verify")}


def map_kb(r):
    src = r.get("source")
    return {"id": _id(r, "kb"), "title": _s(r.get("title")), "category": _s(r.get("category") or "Iné"),
            "source": src if src in ("N", "L", "P", "V") else None, "content": _s(r.get("content"))}


def map_stock(r):
    return {"id": _id(r, "sklad"), **_pick(r, ["name", "category", "unit", "location", "note"]), "qty": _num(r.get("qty")), "minQty": _num(r.get("minQty"))}


def map_quote(r):
    items = []
    for i in r.get("items") or []:
        if not i.get("name"):
            continue
        note = _s(i.get("note"))
        if i.get("basis"):
            note = (note + " · " if note else "") + "návrh ceny: " + _s(i.get("basis"))
        items.append({"name": _s(i.get("name")), "qty": _num(i.get("qty")), "unit": _s(i.get("unit")), "unitPrice": _num(i.get("unitPrice")), "note": note})
    out = {"id": _id(r, "ponuka"), **_pick(r, ["number", "customer", "email", "subject", "notes"]), "status": QST.get(r.get("status"), "draft"), "items": items}
    if r.get("dueDate") and len(_s(r["dueDate"])) == 10:
        out["dueDate"] = _s(r["dueDate"])
    return out


def map_order(r):
    out = {"id": _id(r, "objednavka"), **_pick(r, ["number", "customer", "notes"]), "status": OST.get(r.get("status"), "accepted"),
           "items": [{"name": _s(i.get("name")), "qty": _num(i.get("qty")), "unit": _s(i.get("unit"))} for i in (r.get("oitems") or r.get("items") or []) if i.get("name")],
           "materials": [{"name": _s(m.get("name")), "qty": _num(m.get("qty")), "unit": _s(m.get("unit")), "status": MST.get(m.get("status"), "verify"),
                          "supplierId": _s(m.get("supplierId")), "note": _s(m.get("note"))} for m in (r.get("materials") or []) if m.get("name")],
           "operations": [{"part": _s(o.get("part")), "process": _s(o.get("process")), "machine": _s(o.get("machine")),
                           "minPerPiece": _num(o.get("minPerPiece")), "pieces": _num(o.get("pieces")), "done": bool(o.get("done"))} for o in (r.get("operations") or [])]}
    if r.get("dueDate") and len(_s(r["dueDate"])) == 10:
        out["dueDate"] = _s(r["dueDate"])
    return out


MAPS = {"suppliers": ("dodavatelia", map_supplier), "kb": ("kb", map_kb), "stock": ("sklad", map_stock),
        "quotes": ("ponuky", map_quote), "orders": ("objednavky", map_order)}


def import_export(data: dict, store: Prevadzka, overwrite: bool = False) -> dict:
    report = {}
    for key, (kind, fn) in MAPS.items():
        done = skipped = failed = 0
        existing = {r["id"] for r in store.list(kind)}
        for rec in data.get(key) or []:
            m = fn(rec)
            if m["id"] in existing and not overwrite:
                skipped += 1
                continue
            try:
                store.save(kind, m)
                done += 1
            except RecordError as e:
                failed += 1
                print(f"{kind}/{m['id']}: {e}", file=sys.stderr)
        report[kind] = {"imported": done, "skipped": skipped, "failed": failed}
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m scripts.prevadzka")
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("import", help="import z prototypu EOS Zákazky")
    i.add_argument("subor", type=Path)
    i.add_argument("--intake", type=Path, default=ROOT / "intake")
    i.add_argument("--prepisat", action="store_true")
    a = p.parse_args(argv)
    try:
        data = json.loads(a.subor.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"Súbor sa nedá načítať: {e}", file=sys.stderr)
        return 2
    report = import_export(data, Prevadzka(a.intake), a.prepisat)
    for kind, r in report.items():
        print(f"{kind}: {r['imported']} importovaných, {r['skipped']} už existovalo, {r['failed']} chybných")
    return 1 if any(r["failed"] for r in report.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
