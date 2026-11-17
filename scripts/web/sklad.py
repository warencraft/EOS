"""Prístup k lokálnym dátam UI: zákazky v intake/ (ADR-0019) a pracovné kalkulácie (ADR-0021).

Kalkulácie sa ukladajú do intake/_eos/kalkulacie/<jobRef>.json. Priečinok _eos je mimo
priečinkov zákaziek, takže `job_intake.py check` ho nepovažuje za podklad zákazky, a celý
intake/ git ignoruje.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from datetime import date

from scripts import job_intake
from scripts.calc import kalkulacia as K

JOB_RE = re.compile(r"^JOB-[0-9]{4}-[0-9]{4}$")
TABULKY = {".xls", ".xlsx", ".xlsm"}
# Súbory, ktoré prehliadač vie ukázať priamo v stránke.
NAHLAD = {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
          ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml", ".txt": "text/plain; charset=utf-8"}
KATEGORIE = job_intake.FOLDERS  # priečinok → kategória manifestu
NAZOV_RE = re.compile(r"[^\w.\- ()+,]", re.UNICODE)


class Sklad:
    def __init__(self, intake: Path):
        self.intake = Path(intake)
        self.kalkulacie = self.intake / "_eos" / "kalkulacie"

    def zakazky(self) -> list[dict]:
        out = []
        if not self.intake.is_dir():
            return out
        for d in sorted(self.intake.iterdir()):
            if d.is_dir() and JOB_RE.match(d.name) and (d / "manifest.json").is_file():
                out.append(self.zakazka(d.name))
        return out

    def zakazka(self, job_ref: str) -> dict:
        if not JOB_RE.match(job_ref):
            raise KeyError(job_ref)
        d = self.intake / job_ref
        try:
            manifest = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise KeyError(job_ref) from None
        subory = manifest.get("files", [])
        return {
            "jobRef": job_ref,
            "nazov": manifest.get("title"),
            "doveronost": manifest.get("confidentiality"),
            "aiPovolene": manifest.get("aiProcessingAllowed"),
            "subory": subory,
            "tabulky": [f["path"] for f in subory if Path(f["path"]).suffix.lower() in TABULKY],
            "nahlady": [f["path"] for f in subory if Path(f["path"]).suffix.lower() in NAHLAD],
            "kalkulacia": (self.kalkulacie / f"{job_ref}.json").is_file(),
            "priecinok": d,
        }

    def nacitaj_kalkulaciu(self, job_ref: str) -> dict | None:
        p = self.kalkulacie / f"{job_ref}.json"
        if not p.is_file():
            return None
        return json.loads(p.read_text(encoding="utf-8"))

    def uloz_kalkulaciu(self, kalkulacia: dict) -> None:
        chyby = K.chyby_formatu(kalkulacia)
        if chyby:
            raise ValueError("; ".join(chyby[:5]))
        self.kalkulacie.mkdir(parents=True, exist_ok=True)
        p = self.kalkulacie / f"{kalkulacia['jobRef']}.json"
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(kalkulacia, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, p)

    def cesta_suboru(self, job_ref: str, rel: str) -> Path:
        z = self.zakazka(job_ref)
        if rel not in {f["path"] for f in z["subory"]}:
            raise KeyError(rel)
        return z["priecinok"] / rel

    def nahlad(self, job_ref: str, rel: str) -> tuple[Path, str]:
        """Súbor zo zákazky na zobrazenie v prehliadači. Iba cesty z manifestu a známe typy."""
        cesta = self.cesta_suboru(job_ref, rel)
        typ = NAHLAD.get(cesta.suffix.lower())
        if typ is None or not cesta.is_file():
            raise KeyError(rel)
        return cesta, typ

    def dalsie_cislo(self, rok: int | None = None) -> str:
        rok = rok or date.today().year
        cisla = [int(d.name[-4:]) for d in self.intake.glob(f"JOB-{rok}-*") if JOB_RE.match(d.name)]
        return f"JOB-{rok}-{max(cisla, default=0) + 1:04d}"

    def nova_zakazka(self, nazov: str, kto: str) -> str:
        nazov, kto = nazov.strip(), kto.strip()
        if not nazov or not kto:
            raise ValueError("Vyplň názov zákazky aj kto ju zakladá.")
        self.intake.mkdir(parents=True, exist_ok=True)
        job_ref = self.dalsie_cislo()
        job_intake.cmd_new(job_ref, nazov, kto, intake=self.intake)
        return job_ref

    def uloz_podklad(self, job_ref: str, priecinok: str, nazov_suboru: str, obsah: bytes) -> str:
        """Uloží nahratý súbor do priečinka zákazky a doplní ho do manifestu (job_intake scan)."""
        z = self.zakazka(job_ref)
        if priecinok not in KATEGORIE:
            raise ValueError(f"Neznámy priečinok {priecinok}.")
        meno = NAZOV_RE.sub("_", Path(nazov_suboru.replace("\\", "/")).name).strip(" .")
        if not meno or meno == job_intake.MANIFEST or meno.startswith("~$"):
            raise ValueError(f"Súbor „{nazov_suboru}“ sa nedá uložiť.")
        ciel_dir = z["priecinok"] / priecinok
        ciel_dir.mkdir(parents=True, exist_ok=True)
        ciel = ciel_dir / meno
        n = 2
        while ciel.exists():
            ciel = ciel_dir / f"{Path(meno).stem}-{n}{Path(meno).suffix}"
            n += 1
        ciel.write_bytes(obsah)
        job_intake.cmd_scan(z["priecinok"])
        return ciel.relative_to(z["priecinok"]).as_posix()
