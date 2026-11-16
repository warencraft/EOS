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

from scripts.calc import kalkulacia as K

JOB_RE = re.compile(r"^JOB-[0-9]{4}-[0-9]{4}$")
TABULKY = {".xls", ".xlsx", ".xlsm"}


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
