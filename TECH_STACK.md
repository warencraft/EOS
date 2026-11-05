# TECH_STACK - Technologický rámec EOS

**Project:** EOS - Engineering Operating System  
**Document ID:** (pridelí sa po schválení, napr. `EOS-011`)  
**Version:** 0.2  
**Revision:** 0  
**Status:** Approved  
**Last update:** 2026-11-04  
**Document basis:** platné ADR + ADR-0018  

---

## 1. Účel

Jedno miesto, kde človek aj AI agent zistí, **na čom sa EOS programuje, čo je teraz povolené a čo je zakázané**. Agent nesmie vyberať knižnice, frameworky ani nástroje mimo tohto dokumentu.

## 2. Aktuálna etapa

> **Etapa A – Kontrakty.** Povolené sú iba technológie z riadku A v časti 3.

Etapu mení Software Architect (IT strana) po dohode s Chief Engineering Knowledge Architect. Agent nesmie použiť technológiu z neskoršej etapy ani „na skúšku“.

## 3. Cieľová architektúra po etapách (ADR-0018)

| Etapa | Cieľ | Technológie (pribúdajú) | Úložisko |
| --- | --- | --- | --- |
| **A. Kontrakty** ◀ teraz | schémy, validácia, testy | Python ≥3.11, štandardná knižnica, `jsonschema>=4.18` | JSON súbory v gite |
| **B. Dáta a prehľad** | prvé reálne záznamy, vyhľadávanie, HTML prehľad | `sqlite3` (štandardná knižnica), CLI `argparse` | JSON = zdroj pravdy, SQLite = generovaná kópia |
| **C. Výpočty a výstupy** | kalkulátory, cenová ponuka | `openpyxl`; PDF podľa samostatného rozhodnutia | ako B |
| **D. Interná aplikácia** | prezeranie a zadávanie v prehliadači | `fastapi`, `uvicorn`, `jinja2`, HTMX (1 statický súbor) | SQLite + export do JSON |
| **E. AI asistencia** | čítanie výkresov, návrhy | `anthropic` SDK v module `ai/` | ako D |

```
             ┌──────────── etapa D ────────────┐
 prehliadač ─┤ web/ (FastAPI + Jinja + HTMX)   │
             └───────────────┬─────────────────┘
   CLI `eos` ────────────────┤
                             ▼
   calc/ (čisté funkcie) ◀── store/ (SQLite, čisté SQL) ◀── build ── data/*.json (git)
        │                                                              ▲
        ▼                                                              │
   export/ (HTML, Excel, PDF)                     validation/ ── schemas/*.schema.json
```

## 4. Pevné pravidlá (platia vo všetkých etapách)

| Oblasť | Pravidlo | Zdroj |
| --- | --- | --- |
| Jazyk | iba Python, žiadny druhý backendový jazyk ani JS framework | ADR-0018 |
| Zdroj pravdy | JSON Schema v `schemas/`; kód, tabuľky a formuláre sa z nej odvodzujú | ADR-0002, ADR-0018 |
| Schémy | Draft 2020-12, uzavreté (`additionalProperties: false`), `$id` = `https://eos.local/schemas/…` | ADR-0009, ADR-0010 |
| Identifikátory | iba v `schemas/common/identifiers.schema.json`, prefixy podľa EOS-003 | ADR-0012 |
| Validácia | štruktúra cez `Draft202012Validator`, význam cez `scripts/validation/` | ADR-0013 |
| Kalkulátory | čisté funkcie, bez hardcoded technických hodnôt, výsledok nesie ID použitých záznamov | ADR-0003 |
| Databáza | `sqlite3` + čisté SQL, **bez ORM** | ADR-0018 |
| Výstupy AI a odhady | vždy označené ako návrh, kým ich neschváli človek | EOS-001 §8 |
| Testy | `unittest` (nie `pytest`) | `tests/README.md` |
| Dokumentácia | Markdown s governance hlavičkou, po slovensky s diakritikou; kód a JSON polia po anglicky; UTF-8 | ADR-0001, AGENTS.md |
| Git | práca vo vetvách, do `main` iba cez pull request | skill `eos-git-publish` |

## 5. Vždy zakázané

- Django, Flask, Streamlit, React, Vue, Next.js a iné frameworky mimo tabuľky,
- ORM (SQLAlchemy, Django ORM, Peewee…) a migračné nástroje ako zdroj pravdy,
- Pydantic, dataclasses alebo YAML ako **náhrada** JSON Schema,
- PostgreSQL alebo iný databázový server bez nového ADR,
- závislosti mimo tabuľky v časti 3 bez zápisu do tohto dokumentu,
- reálne technické, cenové alebo materiálové hodnoty bez zdrojovej klasifikácie (N/L/P/V),
- exporty a generované súbory ako autoritatívny zdroj znalostí.

## 6. Cieľová štruktúra kódu

```
src/eos/
  validation/   # dnešné scripts/validation (presun = samostatná úloha)
  store/        # JSON → SQLite, dotazy
  calc/         # kalkulátory
  export/       # HTML, Excel, PDF
  web/          # etapa D
  ai/           # etapa E
  cli.py        # príkaz `eos`
```

Kým nie je schválený presun, nový kód patrí do `scripts/` podľa existujúceho vzoru.

## 7. Nástroje pre vývojára (nepovinné)

| Nástroj | Účel | Stav |
| --- | --- | --- |
| GitHub Actions | `unittest` pri každom pushi a PR (Python 3.11 a 3.12) | návrh |
| `ruff` | jednotný formát a lint, iba ako dev závislosť | návrh |
| `gh` (GitHub CLI) | pull requesty z príkazového riadka | odporúčané |

## 8. Príkazy

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s tests -v
```

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## 9. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-11-04 | 0.1 | 0 | Návrh (Claude) | Zhrnutie platných ADR + návrhy P1–P5 |
| 2026-11-04 | 0.2 | 0 | Software Architect + Claude | Cieľová architektúra po etapách A–E podľa ADR-0018 (Accepted) |
