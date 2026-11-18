"""EOS UI v0 – lokálna webová aplikácia (ADR-0021, etapa D podľa ADR-0018).

Beží na 127.0.0.1. Na serveri ju sprístupní Tailscale (ADR-0025) iba pre vašu súkromnú sieť.
Číta zákazky z intake/, pracovné kalkulácie z intake/_eos/kalkulacie/ a prevádzkové záznamy
(ponuky, objednávky, sklad, dodávatelia, knowledge base) z intake/_eos/prevadzka/. Von posiela
iba to, čo pošle Gmail (IMAP), a iba na pokyn používateľa.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scripts.calc import import_sablona as I
from scripts.calc import kalkulacia as K
from scripts import gmail as G
from scripts import prevadzka as P
from scripts.status import spravy as S
from scripts.export_viewer import AREAS, TRANSLATIONS, load_schemas, load_translations

from . import prevadzka_ui
from .sklad import KATEGORIE, Sklad

# Polia, ktoré sa dajú v UI prepísať číslom (časť → kľúče).
CISELNE_POLIA = {
    "operacie": {"casNaKusMin", "kusov"},
    "material": {"kg", "eurZaKg"},
    "nakup": {"eurZaKs", "kusov"},
    "dalsie": {"eurZaKs", "kusov"},
}
POLOZKY_PONUKY = [K.PRACA, K.TESNENIA, K.PRIPRAVKY, K.NAKUP, K.DOKUMENTACIA, K.KOOPERACIA, K.DOPRAVA]
PRIECINKY = {"vykresy": "Výkresy", "modely": "3D modely", "dopyt": "Dopyt", "ponuka": "Ponuka / kalkulácia",
             "objednavka": "Objednávka", "vyroba": "Výroba", "merania": "Merania",
             "korespondencia": "Korešpondencia", "ine": "Iné"}

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


def cislo_z_formulara(hodnota: str) -> float:
    v = float(str(hodnota).replace(",", ".").replace(" ", "").replace("\u00a0", ""))
    if v < 0 or v != v:
        raise ValueError
    return v


def zmena(v) -> str:
    if v is None:
        return "–"
    if isinstance(v, dict):
        return " · ".join(str(v[x]) for x in ("diel", "proces", "nazov") if v.get(x))
    if isinstance(v, bool):
        return "áno" if v else "nie"
    if isinstance(v, (int, float)):
        return cas(v)
    return str(v)


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1", "testserver"}


def create_app(root: Path = ROOT, intake: Path | None = None, status: Path | None = None,
               allowed_hosts: set[str] | None = None, gmail_config: Path | None = None, imap_factory=None) -> FastAPI:
    sklad = Sklad(intake or root / "intake")
    povolene = LOCAL_HOSTS | {h.strip().lower() for h in (allowed_hosts or set()) if h.strip()}
    povolene |= {h.strip().lower() for h in os.environ.get("EOS_ALLOWED_HOSTS", "").split(",") if h.strip()}
    nastenka = S.Nastenka(status or root / "status" / "spravy", intake=sklad.intake)
    app = FastAPI(title="EOS", docs_url=None, redoc_url=None, openapi_url=None)
    app.mount("/static", StaticFiles(directory=TU / "static"), name="static")

    @app.middleware("http")
    async def iba_z_tejto_aplikacie(request: Request, call_next):
        # Zmeny (POST) prijme iba z vlastných stránok: cudzia stránka v prehliadači nesmie
        # poslať formulár na 127.0.0.1 (ochrana proti CSRF bez tokenov).
        if request.method == "POST":
            origin = request.headers.get("origin")
            if origin and urlsplit(origin).hostname not in povolene:
                return HTMLResponse("Požiadavka z inej stránky bola odmietnutá.", status_code=403)
            if request.headers.get("sec-fetch-site") == "cross-site":
                return HTMLResponse("Požiadavka z inej stránky bola odmietnutá.", status_code=403)
        return await call_next(request)
    sablony = Jinja2Templates(directory=TU / "templates")
    sablony.env.filters["eur"] = cislo
    sablony.env.filters["cas"] = cas
    sablony.env.filters["rozdiel"] = rozdiel
    sablony.env.filters["zmena"] = zmena
    sablony.env.globals.update(LUDIA=S.LUDIA, PRE=S.PRE, TYPY=S.TYPY, ZAVAZNOST=S.ZAVAZNOST,
                               PRIECINKY=PRIECINKY, POLOZKY_PONUKY=POLOZKY_PONUKY)
    sablony.env.globals["otvorene_spravy"] = lambda: sum(1 for x in nastenka.vsetky()
                                                         if x["stav"] == "otvorene" and not x.get("odpovedNa"))
    TRANSLATIONS.update(load_translations(root / "scripts" / "viewer_sk.json"))

    # --- ponuky, objednávky, sklad, dodávatelia, knowledge base, Gmail (ADR-0025) -------
    app.state.imap_factory = imap_factory
    def gmail_provider():
        return G.Gmail.from_config(gmail_config, imap_factory)
    def gmail_saver(address, password):
        if address and password:
            G.save_config(address, password, gmail_config)
        else:
            G.delete_config(gmail_config)
    prevadzka_ui.register(app, sablony, P.Prevadzka(sklad.intake), gmail_provider, gmail_saver)

    def zakazka_alebo_404(job_ref: str) -> dict:
        try:
            return sklad.zakazka(job_ref)
        except KeyError:
            raise HTTPException(404, f"Zákazka {job_ref} nie je v intake/") from None

    def ine_kalkulacie(job_ref: str) -> list[dict]:
        out = []
        for z in sklad.zakazky():
            if z["jobRef"] != job_ref and z["kalkulacia"]:
                kk = sklad.nacitaj_kalkulaciu(z["jobRef"])
                out.append({"jobRef": z["jobRef"], "nazov": z["nazov"], "mnozstvo": kk["mnozstvo"]})
        return out

    def kontext_kalkulacie(job_ref: str, k: dict | None, chyba: str | None = None) -> dict:
        if k is None:
            return {"k": None, "jobRef": job_ref, "chyba": chyba, "vzory": ine_kalkulacie(job_ref)}
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
    def zakazka(request: Request, job_ref: str, preskocene: str = ""):
        z = zakazka_alebo_404(job_ref)
        k = sklad.nacitaj_kalkulaciu(job_ref)
        return sablony.TemplateResponse(request, "zakazka.html", {"z": z, "preskocene": preskocene,
                                                                  **kontext_kalkulacie(job_ref, k)})

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
            cislo_hodnota = cislo_z_formulara(hodnota)
            if pole == "mnozstvo" and cislo_hodnota == 0:
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

    # --- nová zákazka a podklady -------------------------------------------------
    @app.get("/nova", response_class=HTMLResponse)
    def nova_formular(request: Request):
        return sablony.TemplateResponse(request, "nova.html", {"active": "zakazky", "dalsie": sklad.dalsie_cislo()})

    @app.post("/nova")
    async def nova_zakazka(request: Request, nazov: str = Form(""), kto: str = Form(""),
                           priecinok: str = Form("vykresy"), subory: list[UploadFile] = File(default=[])):
        if priecinok not in KATEGORIE:
            priecinok = "ine"
        try:
            job_ref = sklad.nova_zakazka(nazov, kto)
        except ValueError as e:
            return sablony.TemplateResponse(request, "nova.html", {"active": "zakazky", "chyba": str(e),
                                            "dalsie": sklad.dalsie_cislo(), "nazov": nazov, "kto": kto},
                                            status_code=422)
        return await uloz_podklady(job_ref, priecinok, subory)

    async def uloz_podklady(job_ref: str, priecinok: str, subory: list[UploadFile]):
        preskocene = []
        for f in subory:
            if not f.filename:
                continue
            try:
                sklad.uloz_podklad(job_ref, priecinok, f.filename, await f.read())
            except ValueError:
                preskocene.append(f.filename)
        ciel = f"/zakazka/{job_ref}"
        if preskocene:
            ciel += "?" + urlencode({"preskocene": ", ".join(preskocene)})
        return RedirectResponse(ciel, status_code=303)

    @app.post("/zakazka/{job_ref}/podklady")
    async def nahraj_podklady(job_ref: str, priecinok: str = Form("vykresy"),
                              subory: list[UploadFile] = File(default=[])):
        zakazka_alebo_404(job_ref)
        if priecinok not in KATEGORIE:
            raise HTTPException(400, "Neznámy druh podkladu.")
        return await uloz_podklady(job_ref, priecinok, subory)

    @app.get("/zakazka/{job_ref}/subor/{cesta:path}")
    def subor(job_ref: str, cesta: str):
        zakazka_alebo_404(job_ref)
        try:
            p, typ = sklad.nahlad(job_ref, cesta)
        except KeyError:
            raise HTTPException(404, "Súbor nie je v manifeste zákazky alebo sa nedá zobraziť.") from None
        return FileResponse(p, media_type=typ, content_disposition_type="inline", filename=p.name,
                            headers={"X-Content-Type-Options": "nosniff",
                                     "Content-Security-Policy": "sandbox; default-src 'none'; img-src 'self'; style-src 'unsafe-inline'"
                                     if p.suffix.lower() == ".svg" else "frame-ancestors 'self'"})

    # --- kalkulácia bez Excelu ------------------------------------------------------
    @app.post("/zakazka/{job_ref}/kalkulacia/nova")
    def nova_kalkulacia(request: Request, job_ref: str, mnozstvo: str = Form(...), pracaEurH: str = Form(""),
                        vzor: str = Form("")):
        z = zakazka_alebo_404(job_ref)
        if sklad.nacitaj_kalkulaciu(job_ref) is not None:
            raise HTTPException(409, "Zákazka už kalkuláciu má.")
        try:
            ks = cislo_z_formulara(mnozstvo)
            if ks == 0:
                raise ValueError
            if vzor:
                zdroj = sklad.nacitaj_kalkulaciu(vzor)
                if zdroj is None:
                    raise HTTPException(404, "Vzorová zákazka nemá kalkuláciu.")
                k = K.skopiruj(zdroj, job_ref, nazov=z["nazov"], mnozstvo=ks)
                if pracaEurH.strip():
                    k["sadzby"]["pracaEurH"] = cislo_z_formulara(pracaEurH)
            else:
                k = K.prazdna(job_ref, nazov=z["nazov"], mnozstvo=ks, praca_eur_h=cislo_z_formulara(pracaEurH))
        except ValueError:
            return sablony.TemplateResponse(request, "zakazka.html", {"z": z, **kontext_kalkulacie(
                job_ref, None, "Množstvo musí byť kladné číslo a sadzba nezáporné číslo.")}, status_code=422)
        sklad.uloz_kalkulaciu(k)
        return RedirectResponse(f"/zakazka/{job_ref}", status_code=303)

    @app.post("/zakazka/{job_ref}/mnozstvo", response_class=HTMLResponse)
    def uprav_mnozstvo(request: Request, job_ref: str, mnozstvo: str = Form(...)):
        return uprav(request, job_ref, "mnozstvo", mnozstvo)

    @app.post("/zakazka/{job_ref}/pole/{cast}/{id_}/{kluc}", response_class=HTMLResponse)
    def uprav_pole(request: Request, job_ref: str, cast: str, id_: str, kluc: str, hodnota: str = Form(...)):
        if kluc not in CISELNE_POLIA.get(cast, set()):
            raise HTTPException(404, "Toto pole sa nedá upraviť.")
        return uprav(request, job_ref, f"{cast}.{id_}.{kluc}", hodnota)

    @app.post("/zakazka/{job_ref}/pridaj/{cast}", response_class=HTMLResponse)
    def pridaj_riadok(request: Request, job_ref: str, cast: str, diel: str = Form(""), proces: str = Form(""),
                      nazov: str = Form(""), polotovar: str = Form(""), material: str = Form(""),
                      a: str = Form("0"), b: str = Form("0"), polozkaPonuky: str = Form("")):
        k = sklad.nacitaj_kalkulaciu(job_ref)
        if k is None or cast not in CISELNE_POLIA:
            raise HTTPException(404, "Zákazka nemá kalkuláciu.")
        try:
            x, y = cislo_z_formulara(a or "0"), cislo_z_formulara(b or "0")
        except ValueError:
            return vykresli_kalkulaciu(request, job_ref, k, "Čísla musia byť nezáporné. Riadok sa nepridal.")
        pp = polozkaPonuky if polozkaPonuky in POLOZKY_PONUKY else None
        if cast == "operacie":
            if not diel.strip() or not proces.strip():
                return vykresli_kalkulaciu(request, job_ref, k, "Operácia potrebuje diel a proces.")
            riadok = {"diel": diel.strip(), "proces": proces.strip(), "casNaKusMin": x, "kusov": y, "sadzbaEurH": None}
            if pp and pp != K.PRACA:
                riadok["polozkaPonuky"] = pp
        elif cast == "material":
            if not diel.strip():
                return vykresli_kalkulaciu(request, job_ref, k, "Materiál potrebuje diel.")
            riadok = {"diel": diel.strip(), "polotovar": polotovar.strip() or None,
                      "material": material.strip() or None, "kg": x, "eurZaKg": y}
        else:
            if not nazov.strip():
                return vykresli_kalkulaciu(request, job_ref, k, "Položka potrebuje názov.")
            riadok = {"nazov": nazov.strip(), "eurZaKs": x, "kusov": y, "zapocitat": True}
            if pp:
                riadok["polozkaPonuky"] = pp
        nova = K.pridaj(k, cast, riadok)
        sklad.uloz_kalkulaciu(nova)
        return vykresli_kalkulaciu(request, job_ref, nova)

    @app.post("/zakazka/{job_ref}/odober/{cast}/{id_}", response_class=HTMLResponse)
    def odober_riadok(request: Request, job_ref: str, cast: str, id_: str):
        k = sklad.nacitaj_kalkulaciu(job_ref)
        if k is None:
            raise HTTPException(404, "Zákazka nemá kalkuláciu.")
        try:
            nova = K.odober(k, cast, id_)
        except KeyError:
            raise HTTPException(404, "Neznámy riadok.") from None
        sklad.uloz_kalkulaciu(nova)
        return vykresli_kalkulaciu(request, job_ref, nova)

    # --- stavová nástenka (ADR-0022) ---------------------------------------------------
    def kontext_stavu(vsetky: bool = False, chyba: str | None = None, formular: dict | None = None) -> dict:
        return {"active": "stav", "marco": nastenka.pre("marco", aj_vyriesene=vsetky),
                "robino": nastenka.pre("robino", aj_vyriesene=vsetky), "vsetky": vsetky,
                "chyba": chyba, "f": formular or {}}

    @app.get("/stav", response_class=HTMLResponse)
    def stav(request: Request, vsetky: int = 0):
        return sablony.TemplateResponse(request, "stav.html", kontext_stavu(bool(vsetky)))

    @app.post("/stav")
    def stav_nova(request: Request, autor: str = Form(...), pre: str = Form(""), typ: str = Form("feedback"),
                  tema: str = Form(""), text: str = Form(""), odpovedNa: str = Form("")):
        try:
            if odpovedNa:
                povodna = nastenka.nacitaj(odpovedNa)
                tema = tema or f"Re: {povodna['tema']}"[:120]
                # Odpoveď ide druhému človeku; agent si odpovede prečíta zo súborov.
                pre = pre or {"marco": "robino", "robino": "marco"}.get(autor, "oba")
            nastenka.pridaj(autor=autor, pre=pre, typ=typ, tema=tema, text=text, odpoved_na=odpovedNa or None)
        except (KeyError, ValueError) as e:
            return sablony.TemplateResponse(request, "stav.html", kontext_stavu(
                chyba=f"Správa sa neuložila: {e}", formular={"autor": autor, "pre": pre, "typ": typ,
                                                               "tema": tema, "text": text}), status_code=422)
        return RedirectResponse("/stav", status_code=303)

    @app.post("/stav/{id_}/vyriesit")
    def stav_vyries(id_: str, kto: str = Form(...), znovu: str = Form("")):
        if kto not in S.LUDIA:
            raise HTTPException(400, "Neznámy človek.")
        try:
            nastenka.vyries(id_, kto, znovu_otvor=bool(znovu))
        except KeyError:
            raise HTTPException(404, "Neznáma správa.") from None
        return RedirectResponse("/stav", status_code=303)

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
