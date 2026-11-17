"""Výpočet pracovnej kalkulácie zákazky (ADR-0021).

Čisté funkcie: vstup je slovník podľa kalkulacia.schema.json, výstup je rozpis ceny.
Žiadne technické ani obchodné hodnoty nie sú v kóde: sadzby, časy, ceny a množstvá
prichádzajú zo vstupu (EOS-000, ADR-0003).
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = json.loads(Path(__file__).with_name("kalkulacia.schema.json").read_text(encoding="utf-8"))

MATERIAL = "Priamy materiál"
NAKUP = "Nakupované diely"
PRACA = "Priame mzdy"
TESNENIA = "Sada tesnív"
PRIPRAVKY = "Prípravky"
DOKUMENTACIA = "Výkresová dokumentácia"
KOOPERACIA = "Kooperácia"
DOPRAVA = "Doprava"

# Poradie riadkov ako v ponuke (hárok KALKULAČNÍ).
PORADIE = [MATERIAL, NAKUP, TESNENIA, PRACA, PRIPRAVKY, DOKUMENTACIA, KOOPERACIA, DOPRAVA]


def chyby_formatu(kalkulacia: Any) -> list[str]:
    validator = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
    return [f"{'/'.join(map(str, e.path)) or '$'}: {e.message}" for e in validator.iter_errors(kalkulacia)]


def sadzba_operacie(kalkulacia: dict, operacia: dict, jednotna: float | None = None) -> float:
    if jednotna is not None:
        return float(jednotna)
    vlastna = operacia.get("sadzbaEurH")
    return float(vlastna if vlastna is not None else kalkulacia["sadzby"]["pracaEurH"])


def vypocitaj(kalkulacia: dict, *, jednotna_sadzba: float | None = None) -> dict:
    """Vráti rozpis ceny po riadkoch ponuky, po operáciách a po dieloch."""
    riadky: dict[str, float] = {}

    def pripocitaj(riadok: str, suma: float) -> None:
        riadky[riadok] = riadky.get(riadok, 0.0) + suma

    operacie = []
    minuty = 0.0
    for op in kalkulacia["operacie"]:
        sadzba = sadzba_operacie(kalkulacia, op, jednotna_sadzba)
        minut = op["casNaKusMin"] * op["kusov"]
        cena = minut / 60 * sadzba
        minuty += minut
        pripocitaj(op.get("polozkaPonuky") or PRACA, cena)
        operacie.append({"id": op["id"], "minutSpolu": minut, "sadzba": sadzba, "cena": cena,
                         "inaSadzba": op.get("sadzbaEurH") is not None and jednotna_sadzba is None})

    for m in kalkulacia["material"]:
        pripocitaj(m.get("polozkaPonuky") or MATERIAL, m["kg"] * m["eurZaKg"])
    for p in kalkulacia["nakup"]:
        if p["zapocitat"]:
            pripocitaj(p.get("polozkaPonuky") or NAKUP, p["eurZaKs"] * p["kusov"])
    for d in kalkulacia["dalsie"]:
        if d["zapocitat"]:
            pripocitaj(d.get("polozkaPonuky") or DOKUMENTACIA, d["eurZaKs"] * d["kusov"])

    nezapocitane = sum(p["eurZaKs"] * p["kusov"] for p in kalkulacia["nakup"] + kalkulacia["dalsie"]
                       if not p["zapocitat"])
    poradie = [r for r in PORADIE if r in riadky] + sorted(r for r in riadky if r not in PORADIE)
    spolu = sum(riadky.values())
    mnozstvo = kalkulacia["mnozstvo"]
    return {
        "riadky": [{"nazov": r, "suma": round(riadky[r], 2)} for r in poradie],
        "spolu": round(spolu, 2),
        "zaKus": round(spolu / mnozstvo, 2),
        "hodinSpolu": round(minuty / 60, 2),
        "nezapocitane": round(nezapocitane, 2),
        "operacie": {o["id"]: {**o, "cena": round(o["cena"], 2)} for o in operacie},
    }


def porovnanie(kalkulacia: dict, vysledok: dict) -> list[dict]:
    """Rozdiel výpočtu oproti ponuke z Excelu (ak je známa)."""
    ref = kalkulacia.get("referencia") or {}
    out = []
    vypocet = {r["nazov"]: r["suma"] for r in vysledok["riadky"]}
    for nazov, suma in (ref.get("riadky") or {}).items():
        out.append({"nazov": nazov, "excel": suma, "eos": vypocet.get(nazov, 0.0),
                    "rozdiel": round(vypocet.get(nazov, 0.0) - suma, 2)})
    if ref.get("spolu") is not None:
        out.append({"nazov": "Spolu", "excel": ref["spolu"], "eos": vysledok["spolu"],
                    "rozdiel": round(vysledok["spolu"] - ref["spolu"], 2)})
    return out


def zmen(kalkulacia: dict, pole: str, nova_hodnota: Any) -> dict:
    """Zmení jedno pole a zapíše zmenu do histórie. pole: 'sadzby.pracaEurH' alebo 'operacie.<id>.casNaKusMin' a pod."""
    k = deepcopy(kalkulacia)
    cast, *zvysok = pole.split(".")
    if cast == "mnozstvo" and not zvysok:
        ciel, kluc = k, "mnozstvo"
    elif cast == "sadzby":
        ciel, kluc = k["sadzby"], zvysok[0]
    elif cast in {"operacie", "material", "nakup", "dalsie"}:
        ciel = next((x for x in k[cast] if x["id"] == zvysok[0]), None)
        if ciel is None:
            raise KeyError(f"{cast}: neznáme id {zvysok[0]}")
        kluc = zvysok[1]
    else:
        raise KeyError(f"nepodporované pole {pole}")
    povodne = ciel.get(kluc)
    if povodne == nova_hodnota:
        return k
    ciel[kluc] = nova_hodnota
    k["zmeny"].append({"cas": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "pole": pole, "povodne": povodne, "nove": nova_hodnota})
    return k


CASTI = {"operacie": "O", "material": "M", "nakup": "N", "dalsie": "D"}


def _cas() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def prazdna(job_ref: str, *, nazov: str | None, mnozstvo: float, praca_eur_h: float,
            zakaznik: str | None = None) -> dict:
    """Nová kalkulácia bez excelovej šablóny. Všetky hodnoty zadáva používateľ."""
    return {
        "formatVersion": "0.1.0", "jobRef": job_ref, "nazov": nazov, "zakaznik": zakaznik,
        "vykres": None, "materialPopis": None, "mnozstvo": mnozstvo, "terminDodania": None,
        "sadzby": {"pracaEurH": praca_eur_h, "predajEurH": None},
        "material": [], "operacie": [], "nakup": [], "dalsie": [],
        "referencia": None, "upozornenia": [], "zmeny": [],
    }


def skopiruj(zdroj: dict, job_ref: str, *, nazov: str | None, mnozstvo: float) -> dict:
    """Kalkulácia novej zákazky podľa staršej. Kusy operácií, kg materiálu a kusy nákupu
    sa prepočítajú pomerom množstiev; ďalšie položky (dokumentácia, doprava…) ostanú.
    Výsledok nesie upozornenie, že pomer treba overiť – nie je to technologické pravidlo."""
    k = deepcopy(zdroj)
    pomer = mnozstvo / zdroj["mnozstvo"]
    for o in k["operacie"]:
        o["kusov"] = round(o["kusov"] * pomer, 4)
    for m in k["material"]:
        m["kg"] = round(m["kg"] * pomer, 4)
    for n in k["nakup"]:
        n["kusov"] = round(n["kusov"] * pomer, 4)
    k.update({"jobRef": job_ref, "nazov": nazov, "mnozstvo": mnozstvo, "referencia": None,
              "zmeny": [], "terminDodania": None})
    k.pop("zdroj", None)
    k["upozornenia"] = [{
        "kod": "kopia",
        "text": (f"Skopírované z {zdroj['jobRef']} ({cas_sk(zdroj['mnozstvo'])} ks → {cas_sk(mnozstvo)} ks). "
                 "Kusy operácií, kg materiálu a kusy nákupu sú prepočítané pomerom množstiev; "
                 "časy na kus, sadzby a ceny sú prevzaté. Over ich podľa výkresov tejto zákazky."),
        "bunka": None, "dopadEur": None}]
    return k


def cas_sk(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def pridaj(kalkulacia: dict, cast: str, polozka: dict) -> dict:
    """Pridá riadok (operáciu, materiál, nákup, ďalšiu položku) s novým id a zapíše to do histórie."""
    if cast not in CASTI:
        raise KeyError(f"nepodporovaná časť {cast}")
    k = deepcopy(kalkulacia)
    # Id sa nepoužije znova ani po odobratí riadku, aby história zmien zostala jednoznačná.
    vzor = re.compile(rf"^{CASTI[cast]}(\d+)$")
    pouzite = [x["id"] for x in k[cast]] + [z["pole"].split(".")[1] for z in k["zmeny"]
                                             if z["pole"].startswith(cast + ".") and "." in z["pole"]]
    n = max((int(m.group(1)) for i in pouzite if (m := vzor.match(i))), default=0) + 1
    nova = {"id": f"{CASTI[cast]}{n}", **polozka}
    k[cast].append(nova)
    k["zmeny"].append({"cas": _cas(), "pole": f"{cast}.{nova['id']}", "povodne": None, "nove": nova})
    return k


def odober(kalkulacia: dict, cast: str, id_: str) -> dict:
    if cast not in CASTI:
        raise KeyError(f"nepodporovaná časť {cast}")
    k = deepcopy(kalkulacia)
    stara = next((x for x in k[cast] if x["id"] == id_), None)
    if stara is None:
        raise KeyError(f"{cast}: neznáme id {id_}")
    k[cast].remove(stara)
    k["zmeny"].append({"cas": _cas(), "pole": f"{cast}.{id_}", "povodne": stara, "nove": None})
    return k
