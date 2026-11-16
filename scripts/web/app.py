"""EOS UI v0 – lokálna webová aplikácia (ADR-0021, etapa D podľa ADR-0018).

Beží iba na tomto počítači (127.0.0.1). Číta zákazky z intake/ a pracovné kalkulácie
z intake/_eos/kalkulacie/. Nič neposiela von.
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scripts.calc import import_sablona as I
from scripts.calc import kalkulacia as K
from scripts.export_viewer import AREAS, TRANSLATIONS, load_schemas, load_translations

from .sklad import Sklad

TU = Path(__file__).resolve().parent
ROOT = TU.parents[1]

# Čo dnešný model EOS nevie uniesť (vertical slice V949, 2026-11-15). Rozhoduje Marco.
MEDZERY = [
    ("Zákazka a operácia", "Zákazník, množstvo, termín; operácia = diel, typ procesu, čas na kus. Formáty ID existujú, schémy nie. Dnes ich nahrádza pracovná kalkulácia v tejto aplikácii."),
    ("Väzby dielu", "Diel (EIT) sa nedá spojiť s materiálom, polotovarom, výkresom ani zostavou."),
    ("Polotovar", "Tvar, rozmery, norma polotovaru a cena za kg. Prefix POL existuje, schéma nie."),
    ("Hodnoty v katalógoch", "Bez hustoty a jednotiek EOS nevypočíta hmotnosť z rozmerov."),
    ("Nakupované diely a služby", "Hlavy valcov, ložiská, tesnenia, vyváženie, pretesnenie."),
    ("Kontrola odkazov", "Validátor overuje jeden záznam; odkaz na neexistujúci zdroj prejde."),
]


def cislo(v) -> str:
    if v is None:
        return "–"
    s = f"{v:,.2f}".replace(",", " ").replace(".", ",")
    return s


def cas(v) -> str:
    if v is None:
        return "–"
    return (f"{v:.2f}".rstrip("0").rstrip(".")).replace(".", ",")


def rozdiel(v) -> str:
    if v is None:
        return ""
    return ("+" if v > 0 else "−" if v < 0 else "±") + cislo(abs(v))


def create_app(root: Path = ROOT, intake: Path | None = None) -> FastAPI:
    sklad = Sklad(intake or root / "intake")
    app = FastAPI(title="EOS", docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static", StaticFiles(directory=TU / "static"), name="static")
    sablony = Jinja2Templates(directory=TU / "templates")
    sablony.env.filters["eur"] = cislo
    sablony.env.filters["cas"] = cas
    sablony.env.filters["rozdiel"] = rozdiel
    TRANSLATIONS.update(load_translations(root / "scripts" / "viewer_sk.json"))

    def zakazka_alebo_404(job_ref: str) -> dict:
        try:
            return sklad.zakazka(job_ref)
        except KeyError:
            raise HTTPException(404, f"Zákazka {job_ref} nie je v intake/") from None

    def kontext_kalkulacie(job_ref: str, k: dict | None, chyba: str | None = None) -> dict:
        if k is None:
            return {"k": None, "jobRef": job_ref, "chyba": chyba}
        v = K.vypocitaj(k)
        jednotna = K.vypocitaj(k, jednotna_sadzba=k["sadzby"]["pracaEurH"])
        predaj = (K.vypocitaj(k, jednotna_sadzba=k["sadzby"]["predajEurH"])
                  if k["sadzby"].get("predajEurH") else None)
        return {"k": k, "v": v, "jobRef": job_ref, "porovnanie": K.porovnanie(k, v),
                "jednotna": jednotna, "predaj": predaj, "chyba": chyba,
                "diely": list(dict.fromkeys([o["diel"] for o in k["operacie"]] + [m["diel"] for m in k["material"]]))}

    def vykresli_kalkulaciu(request: Request, job_ref: str, k: dict | None, chyba: str | None = None):
        return sablony.TemplateResponse(request, "_kalkulacia.html", kontext_kalkulacie(job_ref, k, chyba))

    @app.get("/", response_class=HTMLResponse)
    def zakazky(request: Request):
        zoznam = sklad.zakazky()
        for z in zoznam:
            k = sklad.nacitaj_kalkulaciu(z["jobRef"])
            if k:
                v = K.vypocitaj(k)
                z["spolu"], z["zaKus"], z["upozorneni"] = v["spolu"], v["zaKus"], len(k["upozornenia"])
                ref = (k.get("referencia") or {}).get("spolu")
                z["ponuka"] = ref
                z["sedi"] = ref is None or abs(v["spolu"] - ref) < 0.015
                z["mnozstvo"] = k["mnozstvo"]
        return sablony.TemplateResponse(request, "zakazky.html", {"zakazky": zoznam, "intake": sklad.intake})

    @app.get("/zakazka/{job_ref}", response_class=HTMLResponse)
    def zakazka(request: Request, job_ref: str):
        z = zakazka_alebo_404(job_ref)
        k = sklad.nacitaj_kalkulaciu(job_ref)
        return sablony.TemplateResponse(request, "zakazka.html", {"z": z, **kontext_kalkulacie(job_ref, k)})

    @app.post("/zakazka/{job_ref}/import")
    def importuj(request: Request, job_ref: str, subor: str = Form(...)):
        zakazka_alebo_404(job_ref)
        try:
            cesta = sklad.cesta_suboru(job_ref, subor)
            k = I.importuj(cesta, job_ref, relativna_cesta=subor)
            sklad.uloz_kalkulaciu(k)
        except KeyError:
            raise HTTPException(400, "Súbor nie je v manifeste zákazky.") from None
        except I.ChybaImportu as e:
            z = sklad.zakazka(job_ref)
            return sablony.TemplateResponse(request, "zakazka.html",
                                            {"z": z, **kontext_kalkulacie(job_ref, None, str(e))}, status_code=422)
        return RedirectResponse(f"/zakazka/{job_ref}", status_code=303)

    def uprav(request: Request, job_ref: str, pole: str, hodnota: str):
        k = sklad.nacitaj_kalkulaciu(job_ref)
        if k is None:
            raise HTTPException(404, "Zákazka nemá kalkuláciu.")
        try:
            cislo_hodnota = float(hodnota.replace(",", ".").replace(" ", ""))
            if cislo_hodnota < 0:
                raise ValueError
        except ValueError:
            return vykresli_kalkulaciu(request, job_ref, k, f"„{hodnota}“ nie je nezáporné číslo. Zmena sa neuložila.")
        try:
            nova = K.zmen(k, pole, cislo_hodnota)
            sklad.uloz_kalkulaciu(nova)
        except (KeyError, ValueError) as e:
            return vykresli_kalkulaciu(request, job_ref, k, f"Zmena sa neuložila: {e}")
        return vykresli_kalkulaciu(request, job_ref, nova)

    @app.post("/zakazka/{job_ref}/operacia/{op_id}", response_class=HTMLResponse)
    def uprav_operaciu(request: Request, job_ref: str, op_id: str, casNaKusMin: str = Form(...)):
        return uprav(request, job_ref, f"operacie.{op_id}.casNaKusMin", casNaKusMin)

    @app.post("/zakazka/{job_ref}/sadzba", response_class=HTMLResponse)
    def uprav_sadzbu(request: Request, job_ref: str, pracaEurH: str = Form(...)):
        return uprav(request, job_ref, "sadzby.pracaEurH", pracaEurH)

    @app.post("/zakazka/{job_ref}/operacia/{op_id}/sadzba", response_class=HTMLResponse)
    def zjednot_sadzbu(request: Request, job_ref: str, op_id: str):
        k = sklad.nacitaj_kalkulaciu(job_ref)
        if k is None:
            raise HTTPException(404, "Zákazka nemá kalkuláciu.")
        nova = K.zmen(k, f"operacie.{op_id}.sadzbaEurH", None)
        sklad.uloz_kalkulaciu(nova)
        return vykresli_kalkulaciu(request, job_ref, nova)

    @app.post("/zakazka/{job_ref}/nakup/{n_id}/zapocitat", response_class=HTMLResponse)
    def prepni_zapocitanie(request: Request, job_ref: str, n_id: str):
        k = sklad.nacitaj_kalkulaciu(job_ref)
        if k is None:
            raise HTTPException(404, "Zákazka nemá kalkuláciu.")
        cast = "nakup" if any(n["id"] == n_id for n in k["nakup"]) else "dalsie"
        polozka = next((n for n in k[cast] if n["id"] == n_id), None)
        if polozka is None:
            raise HTTPException(404, "Neznáma položka.")
        nova = K.zmen(k, f"{cast}.{n_id}.zapocitat", not polozka["zapocitat"])
        sklad.uloz_kalkulaciu(nova)
        return vykresli_kalkulaciu(request, job_ref, nova)

    @app.get("/model", response_class=HTMLResponse)
    def model(request: Request):
        schemy = load_schemas(root)
        oblasti = []
        poradie = ["entities", "knowledge-core", "catalogs", "common", "root"]
        for kluc, nazov, popis in sorted(AREAS, key=lambda a: poradie.index(a[0]) if a[0] in poradie else 99):
            polozky = [s for s in schemy if s["area"] == kluc]
            if polozky:
                oblasti.append({"nazov": nazov, "popis": popis, "schemy": polozky})
        return sablony.TemplateResponse(request, "model.html", {"oblasti": oblasti, "medzery": MEDZERY,
                                                                "pocet": len(schemy)})

    return app


app = create_app()
