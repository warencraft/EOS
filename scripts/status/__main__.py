"""Príkazový riadok stavovej nástenky (ADR-0022).

  python -m scripts.status nova --autor agent --pre marco --typ kontrola --tema "…" --text "…"
  python -m scripts.status zoznam [--pre marco|robino] [--vsetky]
  python -m scripts.status vyries <id> --kto robino
  python -m scripts.status kontrola
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .spravy import LUDIA, PRE, PRIECINOK, ROOT, TYPY, Nastenka


def aktualna_vetva() -> str | None:
    try:
        out = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m scripts.status", description="Stavová nástenka EOS (ADR-0022).")
    ap.add_argument("--priecinok", type=Path, default=PRIECINOK)
    ap.add_argument("--intake", type=Path, default=ROOT / "intake")
    sub = ap.add_subparsers(dest="prikaz", required=True)
    n = sub.add_parser("nova", help="pridá správu")
    n.add_argument("--autor", required=True, choices=list(LUDIA))
    n.add_argument("--pre", required=True, choices=list(PRE))
    n.add_argument("--typ", required=True, choices=list(TYPY))
    n.add_argument("--tema", required=True)
    n.add_argument("--text", help="text správy; ak chýba, číta sa zo štandardného vstupu")
    n.add_argument("--zavaznost", choices=["blokuje", "dolezite", "poznamka"])
    n.add_argument("--vetva", default=None, help="predvolene aktuálna git vetva")
    n.add_argument("--subor", action="append", default=[], dest="subory")
    n.add_argument("--odpoved-na", dest="odpoved_na")
    z = sub.add_parser("zoznam", help="otvorené správy")
    z.add_argument("--pre", choices=["marco", "robino"])
    z.add_argument("--vsetky", action="store_true", help="aj vyriešené")
    v = sub.add_parser("vyries", help="označí správu ako vyriešenú")
    v.add_argument("id")
    v.add_argument("--kto", required=True, choices=list(LUDIA))
    sub.add_parser("kontrola", help="overí formát a citlivé údaje vo všetkých správach")
    a = ap.parse_args(argv)
    nastenka = Nastenka(a.priecinok, a.intake)

    try:
        if a.prikaz == "nova":
            text = a.text if a.text is not None else sys.stdin.read()
            s = nastenka.pridaj(autor=a.autor, pre=a.pre, typ=a.typ, tema=a.tema, text=text,
                                zavaznost=a.zavaznost, vetva=a.vetva or aktualna_vetva(),
                                subory=a.subory, odpoved_na=a.odpoved_na)
            print(f"status/spravy/{s['id']}.json")
        elif a.prikaz == "zoznam":
            for kto in ([a.pre] if a.pre else ["marco", "robino"]):
                spravy = nastenka.pre(kto, aj_vyriesene=a.vsetky)
                print(f"== {PRE[kto]} ({len(spravy)}) ==")
                for s in spravy:
                    print(f"- [{s['stav']}] {s['id']}\n  {TYPY[s['typ']]} od {LUDIA[s['autor']]}: {s['tema']}")
        elif a.prikaz == "vyries":
            nastenka.vyries(a.id, a.kto)
            print(f"vyriešené: {a.id}")
        elif a.prikaz == "kontrola":
            problemy = nastenka.kontrola()
            for p in problemy:
                print(p)
            print("OK" if not problemy else f"{len(problemy)} problémov")
            return 1 if problemy else 0
    except (KeyError, ValueError) as e:
        print(f"Chyba: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
