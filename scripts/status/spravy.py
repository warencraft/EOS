"""Správy stavovej nástenky (ADR-0022).

Každá správa je samostatný JSON súbor v status/spravy/. Git ich prenáša medzi Marcom
a Robinom; samostatné súbory znamenajú, že dve nové správy nikdy nespôsobia konflikt.
Správy sú v gite, preto nesmú obsahovať údaje zákazníkov (ADR-0019): `citlive()` ich
porovná s názvami zákaziek a zákazníkov z lokálneho intake/.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
PRIECINOK = ROOT / "status" / "spravy"
SCHEMA = json.loads(Path(__file__).with_name("sprava.schema.json").read_text(encoding="utf-8"))

LUDIA = {"marco": "Marco", "robino": "Robino", "agent": "Agent"}
PRE = {"marco": "Pre Marca", "robino": "Pre Robina", "oba": "Pre oboch"}
TYPY = {"kontrola": "Kontrola pred commitom", "otazka": "Otázka", "feedback": "Feedback",
        "rozhodnutie": "Treba rozhodnúť", "info": "Na vedomie"}
ZAVAZNOST = {"blokuje": "blokuje", "dolezite": "dôležité", "poznamka": "poznámka"}


def teraz() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:36].strip("-") or "sprava"


def chyby(sprava: Any) -> list[str]:
    v = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
    return [f"{'/'.join(map(str, e.path)) or '$'}: {e.message}" for e in v.iter_errors(sprava)]


def citlive_vyrazy(intake: Path | None) -> set[str]:
    """Názvy zákaziek a zákazníkov z lokálneho intake/, ktoré nesmú ísť do gitu."""
    out: set[str] = set()
    if not intake or not intake.is_dir():
        return out
    for m in intake.glob("JOB-*/manifest.json"):
        try:
            titul = json.loads(m.read_text(encoding="utf-8")).get("title") or ""
        except (OSError, ValueError):
            continue
        out.update(x.strip() for x in re.findall(r"\(([^)]+)\)", titul))
        if titul.strip():
            out.add(titul.strip())
    for k in (intake / "_eos" / "kalkulacie").glob("*.json"):
        try:
            data = json.loads(k.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for kluc in ("zakaznik", "nazov", "vykres"):
            if isinstance(data.get(kluc), str) and len(data[kluc].strip()) >= 3:
                out.add(data[kluc].strip())
    return {x for x in out if len(x) >= 3}


def citlive(sprava: dict, intake: Path | None) -> list[str]:
    """Vráti citlivé výrazy, ktoré sa v správe objavili (porovnanie bez ohľadu na veľkosť písmen)."""
    obsah = " ".join(str(sprava.get(k) or "") for k in ("tema", "text")).casefold()
    return sorted(x for x in citlive_vyrazy(intake) if x.casefold() in obsah)


def nova(*, autor: str, pre: str, typ: str, tema: str, text: str, zavaznost: str | None = None,
         vetva: str | None = None, commit: str | None = None, subory: list[str] | None = None,
         odpoved_na: str | None = None, cas: str | None = None) -> dict:
    cas = cas or teraz()
    sprava = {
        "formatVersion": "0.1.0",
        "id": f"{cas[:19].replace('-', '').replace(':', '')}Z-{autor}-{slug(tema)}",
        "cas": cas, "autor": autor, "pre": pre, "typ": typ, "stav": "otvorene",
        "tema": tema.strip(), "text": text.strip(), "zavaznost": zavaznost,
        "vetva": vetva, "commit": commit, "subory": subory or [], "odpovedNa": odpoved_na,
        "vyriesil": None, "vyriesene": None,
    }
    return sprava


class Nastenka:
    def __init__(self, priecinok: Path = PRIECINOK, intake: Path | None = None):
        self.priecinok = Path(priecinok)
        self.intake = intake

    def vsetky(self) -> list[dict]:
        if not self.priecinok.is_dir():
            return []
        out = []
        for p in sorted(self.priecinok.glob("*.json")):
            out.append(json.loads(p.read_text(encoding="utf-8")))
        return sorted(out, key=lambda s: s["cas"])

    def nacitaj(self, id_: str) -> dict:
        p = self._cesta(id_)
        if not p.is_file():
            raise KeyError(id_)
        return json.loads(p.read_text(encoding="utf-8"))

    def _cesta(self, id_: str) -> Path:
        if not re.fullmatch(SCHEMA["properties"]["id"]["pattern"], id_):
            raise KeyError(id_)
        return self.priecinok / f"{id_}.json"

    def uloz(self, sprava: dict, *, nova_sprava: bool = True) -> Path:
        problemy = chyby(sprava)
        if problemy:
            raise ValueError("; ".join(problemy[:5]))
        nalez = citlive(sprava, self.intake)
        if nalez:
            raise ValueError("Správa obsahuje údaje zo zákaziek, ktoré nesmú ísť do gitu: " + ", ".join(nalez))
        if sprava.get("odpovedNa"):
            self.nacitaj(sprava["odpovedNa"])  # KeyError, ak neexistuje
        self.priecinok.mkdir(parents=True, exist_ok=True)
        p = self._cesta(sprava["id"])
        if nova_sprava:
            zaklad, n = sprava["id"], 2
            while p.exists():
                sprava["id"] = f"{zaklad}-{n}"
                p = self._cesta(sprava["id"])
                n += 1
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(sprava, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, p)
        return p

    def pridaj(self, **kw) -> dict:
        sprava = nova(**kw)
        self.uloz(sprava)
        return sprava

    def vyries(self, id_: str, kto: str, *, znovu_otvor: bool = False) -> dict:
        s = self.nacitaj(id_)
        if znovu_otvor:
            s.update({"stav": "otvorene", "vyriesil": None, "vyriesene": None})
        else:
            s.update({"stav": "vyriesene", "vyriesil": kto, "vyriesene": teraz()})
        self.uloz(s, nova_sprava=False)
        return s

    def kontrola(self) -> list[str]:
        """Chyby formátu, citlivé údaje a odpovede na neexistujúce správy vo všetkých súboroch."""
        problemy = []
        ids = set()
        spravy = []
        for p in sorted(self.priecinok.glob("*.json")) if self.priecinok.is_dir() else []:
            try:
                s = json.loads(p.read_text(encoding="utf-8"))
            except ValueError as e:
                problemy.append(f"{p.name}: nie je platný JSON ({e})")
                continue
            problemy += [f"{p.name}: {c}" for c in chyby(s)]
            if isinstance(s, dict) and s.get("id") and f"{s['id']}.json" != p.name:
                problemy.append(f"{p.name}: id {s['id']} nezodpovedá názvu súboru")
            if isinstance(s, dict):
                problemy += [f"{p.name}: citlivý údaj „{x}“" for x in citlive(s, self.intake)]
                ids.add(s.get("id"))
                spravy.append((p.name, s))
        for meno, s in spravy:
            if s.get("odpovedNa") and s["odpovedNa"] not in ids:
                problemy.append(f"{meno}: odpovedá na neexistujúcu správu {s['odpovedNa']}")
        return problemy

    def pre(self, kto: str, *, aj_vyriesene: bool = False) -> list[dict]:
        """Hlavné správy (nie odpovede) pre daného človeka, najnovšie hore, s odpoveďami."""
        vsetky = self.vsetky()
        odpovede: dict[str, list[dict]] = {}
        for s in vsetky:
            if s.get("odpovedNa"):
                odpovede.setdefault(s["odpovedNa"], []).append(s)
        out = []
        for s in reversed(vsetky):
            if s.get("odpovedNa") or s["pre"] not in (kto, "oba"):
                continue
            if s["stav"] == "vyriesene" and not aj_vyriesene:
                continue
            out.append({**s, "odpovede": odpovede.get(s["id"], [])})
        return out
