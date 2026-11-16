"""Import excelovej kalkulačnej šablóny (.xls, .xlsx) do pracovnej kalkulácie (ADR-0021).

Šablóna má hárky Nesortovaný, SADA TESNÍV, PRÍPRAVKY, SPOJOVACÍ MAT. NÁRADIE, KOO,
DOKUMENTÁCIA a KALKULAČNÍ. Stĺpce sa hľadajú podľa textu hlavičky (riadky 1–3), lebo
v jednotlivých hárkoch a verziách šablóny sú posunuté.

Importér nič neodhaduje. Čo v šablóne nesedí, vráti ako upozornenie s bunkou a dopadom.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import kalkulacia as K

PROCESY = {  # text hlavičky v šablóne → názov typu operácie
    "REZANIE": "Rezanie", "SUS": "Sústruženie", "FREZA": "Frézovanie", "VRTANIE": "Vŕtanie",
    "BRÚSENIE": "Brúsenie / honovanie", "ZVÁRANIE": "Zváranie", "KOO": "Kooperácia",
    "MONTÁŽ": "Montáž", "TLAKOVKA": "Tlaková skúška", "FARBA": "Farbenie",
}
PRACOVNE_HARKY = {"NESORTOVANÝ": K.PRACA, "SADA TESNÍV": K.TESNENIA, "PRÍPRAVKY": K.PRIPRAVKY}
NAKUPNE_HARKY = {"SPOJOVACÍ MAT. NÁRADIE": K.NAKUP, "KOO": K.KOOPERACIA, "DOKUMENTÁCIA": K.DOKUMENTACIA}
REFERENCIA = [  # kľúčové slovo v popise riadku KALKULAČNÍ → riadok výpočtu; poradie je dôležité
    ("nakupovan", K.NAKUP), ("tesn", K.TESNENIA), ("mzdy", K.PRACA), ("výroba", K.NAKUP),
    ("prípravk", K.PRIPRAVKY), ("dokument", K.DOKUMENTACIA), ("kooper", K.KOOPERACIA),
    ("doprava", K.DOPRAVA), ("materiál", K.MATERIAL),
]


class ChybaImportu(ValueError):
    pass


# ---------- čítanie zošita ----------------------------------------------------

class Harok:
    def __init__(self, nazov: str, bunky: list[list[Any]]):
        self.nazov = nazov
        self.bunky = bunky

    @property
    def riadkov(self) -> int:
        return len(self.bunky)

    def hodnota(self, r: int, c: int) -> Any:
        """r, c od 0."""
        if r >= len(self.bunky) or c >= len(self.bunky[r]):
            return None
        v = self.bunky[r][c]
        return None if v == "" else v

    def cislo(self, r: int, c: int | None) -> float:
        if c is None:
            return 0.0
        v = self.hodnota(r, c)
        return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0.0

    def text(self, r: int, c: int | None) -> str:
        if c is None:
            return ""
        v = self.hodnota(r, c)
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        return "" if v is None else str(v).strip()


def stlpec(c: int) -> str:
    s = ""
    c += 1
    while c:
        c, r = divmod(c - 1, 26)
        s = chr(65 + r) + s
    return s


def nacitaj_zosit(subor: Path) -> dict[str, Harok]:
    if subor.suffix.lower() == ".xls":
        import xlrd

        kniha = xlrd.open_workbook(str(subor))
        return {s.name.strip().upper(): Harok(s.name.strip(), [s.row_values(r) for r in range(s.nrows)])
                for s in kniha.sheets()}
    if subor.suffix.lower() in {".xlsx", ".xlsm"}:
        import openpyxl
        import openpyxl.reader.excel as excel

        # Šablóna obsahuje WMF obrázok, na ktorom openpyxl padá; obrázky nepotrebujeme.
        povodne = excel.find_images
        excel.find_images = lambda archive, path: ([], [])
        try:
            kniha = openpyxl.load_workbook(subor, data_only=True, read_only=False)
        finally:
            excel.find_images = povodne
        return {ws.title.strip().upper(): Harok(ws.title.strip(), [list(r) for r in ws.iter_rows(values_only=True)])
                for ws in kniha.worksheets}
    raise ChybaImportu(f"Nepodporovaný formát: {subor.suffix} (podporované .xls, .xlsx)")


def hlavicky(h: Harok) -> dict[int, str]:
    sirka = max((len(r) for r in h.bunky[:3]), default=0)
    out = {}
    for c in range(sirka):
        casti = [h.text(r, c) for r in range(3)]
        text = " / ".join(re.sub(r"\s+", " ", t) for t in casti if t)
        if text:
            out[c] = text
    return out


def najdi(hl: dict[int, str], *, zacina: str | None = None, rovna: str | None = None, po: int = -1) -> int | None:
    for c in sorted(hl):
        if c <= po:
            continue
        t = hl[c]
        if rovna is not None and t == rovna:
            return c
        if zacina is not None and t.upper().startswith(zacina.upper()):
            return c
    return None


def riadok_spolu(h: Harok) -> int:
    for r in range(3, h.riadkov):
        if h.text(r, 0).lower().startswith("spolu"):
            return r
    return h.riadkov


def sk(v: float, des: int = 2) -> str:
    """Číslo so slovenskou desatinnou čiarkou; celé čísla bez desatinných miest."""
    if float(v).is_integer():
        return f"{int(v)}"
    return f"{v:.{des}f}".rstrip("0").rstrip(".").replace(".", ",")


def sadzba_z_textu(text: str) -> float | None:
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:€|eur)", text, re.IGNORECASE) or re.search(r"/\s*(\d+(?:[.,]\d+)?)\s*€", text)
    return float(m.group(1).replace(",", ".")) if m else None


# ---------- import ---------------------------------------------------------------

def importuj(subor: Path, job_ref: str, *, relativna_cesta: str | None = None) -> dict:
    harky = nacitaj_zosit(subor)
    if "NESORTOVANÝ" not in harky or "KALKULAČNÍ" not in harky:
        raise ChybaImportu("Súbor nie je kalkulačná šablóna (chýba hárok Nesortovaný alebo KALKULAČNÍ).")

    upozornenia: list[dict] = []

    def upozorni(kod: str, text: str, bunka: str | None = None, dopad: float | None = None) -> None:
        upozornenia.append({"kod": kod, "text": text, "bunka": bunka,
                            "dopadEur": None if dopad is None else round(dopad, 2)})

    kalk = harky["KALKULAČNÍ"]
    hlavicka = {}
    referencia_riadky: dict[str, float] = {}
    ref_spolu = ref_kus = None
    termin = None
    sadzby_text = []
    for r in range(kalk.riadkov):
        for c in range(len(kalk.bunky[r])):
            t = kalk.text(r, c)
            if t.endswith(":"):
                hodnota = next((kalk.text(r, cc) for cc in range(c + 1, min(c + 4, len(kalk.bunky[r]))) if kalk.text(r, cc)), "")
                hlavicka[re.sub(r"\s+", " ", t.rstrip(" :").lower())] = hodnota or None
            if "termín" in t.lower() and not t.endswith(":"):
                termin = t
        popis = " ".join(kalk.text(r, c) for c in range(1, 6))
        nizke = popis.lower()
        if re.search(r"(€|eur)\s*[*/]?\s*hod", nizke):
            sadzby_text.append(popis)
        suma = next((kalk.cislo(r, c) for c in range(5, 8) if kalk.cislo(r, c)), None)
        if suma is None or not popis.strip():
            continue
        if "celková" in nizke:
            ref_spolu = suma
        elif "kusová" in nizke:
            ref_kus = suma
        else:
            for kluc, riadok in REFERENCIA:
                if kluc in nizke:
                    referencia_riadky[riadok] = round(referencia_riadky.get(riadok, 0) + suma, 2)
                    break

    mnozstvo_text = hlavicka.get("množstvo")
    try:
        mnozstvo = float(str(mnozstvo_text).replace(",", "."))
    except (TypeError, ValueError):
        raise ChybaImportu("V hárku KALKULAČNÍ chýba množstvo.") from None
    if termin is None:
        termin = hlavicka.get("termín dodania")
    if not hlavicka.get("zákazník"):
        upozorni("zakaznik_chyba", "V hárku KALKULAČNÍ nie je vyplnený zákazník.", "KALKULAČNÍ")

    # --- pracovné hárky: operácie, materiál, zvyšky šablóny
    operacie: list[dict] = []
    material: list[dict] = []
    sadzby_riadkov: list[tuple[float, str, float]] = []
    predaj = hlavicka_mzdy = None
    for kluc, polozka in PRACOVNE_HARKY.items():
        h = harky.get(kluc)
        if h is None:
            continue
        hl = hlavicky(h)
        col = {
            "nazov": najdi(hl, zacina="Číslo výkres"), "nazovMat": najdi(hl, zacina="Názov materiálu"),
            "priemer": najdi(hl, zacina="Priemer"), "hrubka": najdi(hl, zacina="Hrúbka"),
            "sirka": najdi(hl, zacina="Šírka"), "dlzka": najdi(hl, zacina="Dĺžka +"),
            "norma": najdi(hl, zacina="Norma"), "material": najdi(hl, rovna="Material"),
            "ks": najdi(hl, rovna="ks / zákazku"), "kg": najdi(hl, zacina="Hmotnosť"),
            "eurKg": najdi(hl, zacina="Jednotková cena"), "cenaMat": najdi(hl, zacina="Cena celkova / €"),
            "casSpolu": najdi(hl, zacina="Čas/ celkom v min"), "mzdy": najdi(hl, zacina="PRIAME MZDY"),
            "predaj": najdi(hl, zacina="(1hod/"),
        }
        col["mzdySpolu"] = najdi(hl, rovna="Cena spolu", po=col["mzdy"]) if col["mzdy"] is not None else None
        if col["mzdy"] is not None and hlavicka_mzdy is None:
            hlavicka_mzdy = sadzba_z_textu(hl[col["mzdy"]])
        if col["predaj"] is not None and predaj is None:
            predaj = sadzba_z_textu(hl[col["predaj"]])
        procesy = {}
        for c, t in hl.items():
            for skratka, proces in PROCESY.items():
                if t.upper().startswith(skratka) and "Čas/1ks" in t:
                    procesy[c] = proces
        zvysky, zvysky_kg = 0, 0.0
        for r in range(3, riadok_spolu(h)):
            diel = h.text(r, col["nazov"]) or h.text(r, col["nazovMat"]) or f"riadok {r + 1}"
            if diel in {"Názov dielca", "Výkres"}:
                diel = h.text(r, col["nazovMat"]) or f"riadok {r + 1}"
            ks = h.cislo(r, col["ks"])
            cas = h.cislo(r, col["casSpolu"])
            cena_mat = h.cislo(r, col["cenaMat"])
            if cas > 0:
                mzdy = h.cislo(r, col["mzdySpolu"])
                sadzba = round(mzdy / (cas / 60), 2) if mzdy else None
                if sadzba is not None:
                    sadzby_riadkov.append((sadzba, f"{h.nazov}!{stlpec(col['mzdySpolu'])}{r + 1}", cas))
                for c, proces in procesy.items():
                    t = h.cislo(r, c)
                    if t > 0:
                        operacie.append({"id": f"O{len(operacie) + 1}", "diel": diel, "proces": proces,
                                         "casNaKusMin": round(t, 4), "kusov": ks, "sadzbaEurH": sadzba,
                                         "polozkaPonuky": polozka, "zdrojBunka": f"{h.nazov}!{stlpec(c)}{r + 1}"})
            if cena_mat > 0:
                rozmery = " × ".join(sk(h.cislo(r, col[k])) for k in ("priemer", "hrubka", "sirka", "dlzka")
                                     if h.cislo(r, col[k]))
                material.append({"id": f"M{len(material) + 1}", "diel": diel,
                                 "polotovar": " ".join(x for x in (h.text(r, col["nazovMat"]), rozmery) if x) or None,
                                 "norma": h.text(r, col["norma"]) or None, "material": h.text(r, col["material"]) or None,
                                 "kg": round(h.cislo(r, col["kg"]), 4), "eurZaKg": h.cislo(r, col["eurKg"]),
                                 "polozkaPonuky": K.MATERIAL if polozka == K.PRACA else polozka,
                                 "zdrojBunka": f"{h.nazov}!{stlpec(col['cenaMat'])}{r + 1}"})
            elif cas == 0 and h.cislo(r, col["kg"]) > 0:
                zvysky += 1
                zvysky_kg += h.cislo(r, col["kg"])
        if zvysky:
            upozorni("zvysky_sablony",
                     f"{h.nazov}: {zvysky} riadkov bez ceny a času (zvyšky staršej kalkulácie) s hmotnosťou "
                     f"{sk(round(zvysky_kg, 1))} kg. Súčet hmotnosti v hárku je preto nesprávny.", h.nazov)

    if sadzby_riadkov:
        hlavna = Counter(s for s, _, _ in sadzby_riadkov).most_common(1)[0][0]
    else:
        z_textu = [s for s in (sadzba_z_textu(t) for t in sadzby_text) if s is not None]
        if not z_textu:
            raise ChybaImportu("V šablóne nie sú časy operácií ani sadzba v hárku KALKULAČNÍ.")
        hlavna = z_textu[0]
        upozorni("bez_operacii", "Kalkulácia nemá rozpis operácií s časmi; sadzba je prevzatá z textu ponuky.",
                 "Nesortovaný")
    for s, bunka, cas in sadzby_riadkov:
        if abs(s - hlavna) > 0.01:
            upozorni("sadzba_rozdielna", f"Riadok je ocenený {sk(s)} €/h namiesto {sk(hlavna)} €/h.", bunka,
                     (s - hlavna) * cas / 60)
    for op in operacie:
        if op["sadzbaEurH"] is not None and abs(op["sadzbaEurH"] - hlavna) <= 0.01:
            op["sadzbaEurH"] = None
    if hlavicka_mzdy is not None and abs(hlavicka_mzdy - hlavna) > 0.01:
        upozorni("hlavicka_sadzby", f"Hlavička stĺpca uvádza {sk(hlavicka_mzdy)} €/h, výpočet používa {sk(hlavna)} €/h.",
                 "Nesortovaný, hlavička PRIAME MZDY")
    for t in sadzby_text:
        s = sadzba_z_textu(t)
        if s is not None and abs(s - hlavna) > 0.01:
            upozorni("sadzba_ponuky", f"Ponuka uvádza {sk(s)} €/h, riadky sú ocenené {sk(hlavna)} €/h.", "KALKULAČNÍ")

    # --- nákupné hárky
    nakup: list[dict] = []
    dalsie: list[dict] = []
    for kluc, polozka in NAKUPNE_HARKY.items():
        h = harky.get(kluc)
        if h is None:
            continue
        hl = hlavicky(h)
        c_nazov, c_mat = najdi(hl, zacina="Číslo výkres"), najdi(hl, zacina="Názov materiálu")
        c_cena, c_spolu = najdi(hl, zacina="Jednotková cena"), najdi(hl, zacina="Cena celkova / €")
        c_ks, c_rozp = najdi(hl, rovna="ks / zákazku"), najdi(hl, rovna="ks / rozpiska")
        for r in range(3, riadok_spolu(h)):
            cena = h.cislo(r, c_cena)
            if cena <= 0:
                continue
            nazov = h.text(r, c_nazov)
            if nazov in {"", "Výkres"}:
                nazov = polozka if polozka == K.DOKUMENTACIA else (h.text(r, c_mat) or f"riadok {r + 1}")
            spolu, ks = h.cislo(r, c_spolu), h.cislo(r, c_ks)
            kusov = round(spolu / cena, 4) if spolu else ks
            bunka = f"{h.nazov}!{stlpec(c_cena)}{r + 1}"
            if spolu and ks and abs(kusov - ks) > 0.001:
                rozp = h.cislo(r, c_rozp)
                upozorni("mnozstvo_nesedi",
                         f"{nazov}: stĺpec „ks na zákazku“ = {sk(ks)}, cena počíta {sk(kusov)} ks"
                         + (f" (stĺpec „ks rozpiska“ = {sk(rozp)})." if rozp else "."), bunka, (ks - kusov) * cena)
            if not spolu:
                upozorni("nezapocitane", f"{nazov}: cena {sk(cena)} € je zapísaná, ale nie je v súčte.", bunka,
                         cena * (ks or 1))
            ciel = dalsie if polozka in {K.DOKUMENTACIA, K.KOOPERACIA} else nakup
            ciel.append({"id": f"{'D' if ciel is dalsie else 'N'}{len(ciel) + 1}", "nazov": nazov, "eurZaKs": cena,
                         "kusov": kusov, "zapocitat": bool(spolu), "polozkaPonuky": polozka, "zdrojBunka": bunka})

    kalkulacia = {
        "formatVersion": "0.1.0", "jobRef": job_ref,
        "nazov": hlavicka.get("názov výrobku"), "zakaznik": hlavicka.get("zákazník"),
        "vykres": hlavicka.get("číslo výkresu"), "materialPopis": hlavicka.get("materiál"),
        "mnozstvo": mnozstvo, "terminDodania": termin,
        "zdroj": {"subor": relativna_cesta or subor.name,
                  "sha256": hashlib.sha256(subor.read_bytes()).hexdigest(),
                  "importovane": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "sadzby": {"pracaEurH": hlavna, "predajEurH": predaj},
        "material": material, "operacie": operacie, "nakup": nakup, "dalsie": dalsie,
        "referencia": {"riadky": referencia_riadky,
                       "spolu": None if ref_spolu is None else round(ref_spolu, 2),
                       "zaKus": None if ref_kus is None else round(ref_kus, 2)},
        "upozornenia": upozornenia, "zmeny": [],
    }

    vysledok = K.vypocitaj(kalkulacia)
    for p in K.porovnanie(kalkulacia, vysledok):
        if abs(p["rozdiel"]) > 0.015:
            upozorni("rozdiel_ponuky", f"{p['nazov']}: výpočet z riadkov {sk(p['eos'])} €, ponuka {sk(p['excel'])} €.",
                     "KALKULAČNÍ", p["rozdiel"])
    chyby = K.chyby_formatu(kalkulacia)
    if chyby:
        raise ChybaImportu("Import vytvoril neplatnú kalkuláciu: " + "; ".join(chyby[:5]))
    return kalkulacia
