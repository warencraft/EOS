"""Prevádzkové záznamy UI (ADR-0025): ponuky, objednávky, sklad, dodávatelia, knowledge base.

Ukladajú sa ako JSON súbory v intake/_eos/prevadzka/<druh>/<id>.json, mimo gitu (ADR-0019).
Formát je nástrojový (prevadzka.schema.json), nie kontrakt EOS. Hodnoty v nich nie sú znalosti
EOS: ceny a časy sú pracovné, kým ich neprevezme schválený kontrakt.
"""

from __future__ import annotations

import json
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).resolve().parent / "prevadzka.schema.json"
KINDS = {"ponuky": "quote", "objednavky": "order", "sklad": "stock", "dodavatelia": "supplier", "kb": "kb"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")

QUOTE_STATUS = {"draft": "Rozpracovaná", "gmail_draft": "Koncept v Gmaile", "sent": "Odoslaná", "accepted": "Prijatá", "rejected": "Zamietnutá"}
ORDER_STATUS = {"accepted": "Prijatá", "waiting_material": "Čaká na materiál", "in_production": "Vo výrobe", "done": "Hotová", "shipped": "Odoslaná"}
MATERIAL_STATUS = {"verify": "Overiť", "in_stock": "Na sklade", "to_order": "Objednať", "ordered": "Objednané", "received": "Prijaté"}
SUPPLIER_STATUS = {"verify": "Na overenie", "used": "Používame", "not_used": "Nepoužívame"}
KB_CATEGORIES = ["EOS projekt", "Sadzby", "Pravidlá nacenenia", "Stroje", "Procesy", "Materiály", "Zákazníci", "Firma", "Referenčné zákazky", "Iné"]


class RecordError(ValueError):
    """Záznam nezodpovedá prevadzka.schema.json."""


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(text: str, fallback: str = "zaznam") -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]
    return s or fallback


def new_id(prefix: str) -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(2)}"


class Prevadzka:
    def __init__(self, intake: Path):
        self.root = Path(intake) / "_eos" / "prevadzka"
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self._validators = {
            kind: Draft202012Validator({"$schema": schema["$schema"], "$defs": schema["$defs"], "$ref": f"#/$defs/{d}"},
                                       format_checker=FormatChecker())
            for kind, d in KINDS.items()
        }

    def _dir(self, kind: str) -> Path:
        if kind not in KINDS:
            raise KeyError(kind)
        return self.root / kind

    def _path(self, kind: str, id_: str) -> Path:
        if not ID_RE.match(id_ or ""):
            raise KeyError(id_)
        return self._dir(kind) / f"{id_}.json"

    def errors(self, kind: str, record: dict) -> list[str]:
        return [f"{'/'.join(map(str, e.absolute_path)) or '(koreň)'}: {e.message}"
                for e in sorted(self._validators[kind].iter_errors(record), key=lambda e: list(e.absolute_path))]

    def list(self, kind: str) -> list[dict]:
        d = self._dir(kind)
        if not d.is_dir():
            return []
        out = []
        for p in sorted(d.glob("*.json")):
            try:
                out.append(json.loads(p.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue  # poškodený súbor sa nezobrazí; ostáva na disku na ručnú opravu
        return out

    def get(self, kind: str, id_: str) -> dict:
        p = self._path(kind, id_)
        if not p.is_file():
            raise KeyError(id_)
        return json.loads(p.read_text(encoding="utf-8"))

    def save(self, kind: str, record: dict) -> dict:
        rec = dict(record)
        stamp = now()
        rec.setdefault("createdAt", stamp)
        rec["updatedAt"] = stamp
        errs = self.errors(kind, rec)
        if errs:
            raise RecordError("; ".join(errs))
        p = self._path(kind, rec["id"])
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, p)
        return rec

    def delete(self, kind: str, id_: str) -> None:
        p = self._path(kind, id_)
        if p.is_file():
            p.unlink()
