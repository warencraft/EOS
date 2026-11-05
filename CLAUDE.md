# CLAUDE.md - EOS

EOS je interný inžiniersky znalostný systém pre strojársku výrobu a cenové ponuky. Pravidlá projektu sú v `AGENTS.md`, technologický rámec v `TECH_STACK.md`. Oba súbory platia celé.

@AGENTS.md
@TECH_STACK.md

## Roly (ADR-0018)

| Rola | Kto | Rozhoduje o |
| --- | --- | --- |
| Chief Engineering Knowledge Architect | strojár, vlastník obsahu | čo EOS vie: entity a ich hranice, zdroje, normy, pravidlá z praxe |
| Software Architect | IT strana projektu | technika: stack, architektúra kódu, etapy, CI, git |
| AI agent | ty | implementácia v rámci týchto rozhodnutí |

- So strojárom hovor po slovensky, jednoducho a bez programátorského žargónu. Odborné pojmy z kódu vysvetli jednou vetou.
- **Doménové rozhodnutia nerob sám.** Čo je materiál, stroj, proces, aké hodnoty a zdroje platia, rozhoduje strojár. Navrhni možnosti s dôsledkami a nechaj ho vybrať.
- **Technológie nevyberaj sám.** Drž sa `TECH_STACK.md`. Čo v ňom nie je, navrhni Software Architectovi cez ADR (skill `eos-adr`).

## Na čom programujeme

- **Aktuálna etapa: A – Kontrakty.** Iba Python + štandardná knižnica + `jsonschema`. Dáta sú JSON súbory, testy `unittest`.
- Ďalšie etapy (SQLite, kalkulátory, Excel, FastAPI + HTMX, AI) sú v `TECH_STACK.md` §3. **Nepoužívaj ich, kým Software Architect nezmení etapu.**
- JSON Schema v `schemas/` je jediný zdroj pravdy o tvare dát. Nevytváraj paralelné modely (Pydantic, ORM, dataclasses ako náhradu).
- Nová závislosť smie pribudnúť iba vtedy, ak patrí do aktuálnej etapy. Zapíš ju do `pyproject.toml` aj `TECH_STACK.md`.

## Kde je aktuálny stav

- Orientácia: `docs/INDEX.md`. Aktuálny plán: **horná sekcia** `ROADMAP.md` a `BACKLOG.md`. Nižšie sekcie sú historické.
- CDR a RFC majú 30–60 KB. Čítaj hlavičku, prvý odsek a sekciu výsledku podľa `docs/INDEX.md`, zvyšok hľadaj cez `grep`.
- Ďalšiu fázu nezačínaj bez samostatného zadania.

## Ako pracovať

1. Najprv navrhni postup a počkaj na súhlas (AGENTS.md bod 12).
2. Pracuj vo vetve, nie v `main`.
3. Drž sa existujúcich vzorov: nová entita = štruktúra `schemas/entities/material.schema.json`, testy podľa `eos-write-tests` (riadok v `ENTITY_PROFILES`, nie kópia testov).
4. Po každej zmene spusti celú testovaciu sadu (`eos-run-tests`).
5. Pred ukončením prejdi kontrolu (`eos-governance-check`).
6. Ponúkni uloženie a pull request (`eos-git-publish`).

## Skilly

| Skill | Kedy |
| --- | --- |
| `eos-run-tests` | po každej zmene kódu, schémy alebo fixtúry |
| `eos-schema-change` | nová entita, katalóg alebo zmena schémy |
| `eos-write-tests` | pred pridaním testu, fixtúry alebo neplatného prípadu |
| `eos-adr` | zmena architektúry, závislostí, etapy alebo pravidiel |
| `eos-governance-check` | vždy pred ukončením práce |
| `eos-git-publish` | „ulož to“, „pushni“, „sprav PR“; všetko urob a vysvetli za používateľa |

## Príkazy

```bash
.venv/bin/python -m pip install -e .                    # Windows: .\.venv\Scripts\python ...
.venv/bin/python -m unittest discover -s tests -v       # celá sada
.venv/bin/python -m scripts.validation.cli <record.json> <schema_id>
python scripts/export_viewer.py                         # HTML prehľad → exports/viewer/
```

## Nikdy

- nepoužívaj technológiu mimo aktuálnej etapy ani mimo `TECH_STACK.md`,
- nevkladaj reálne technické, cenové ani materiálové hodnoty bez zdroja; fixtúry sú fiktívne,
- nehlás testy ako úspešné, keď chýba `jsonschema` alebo sa nespustili všetky,
- nemeň Accepted/Approved ADR ani uzavreté CDR; navrhni amendment,
- necommituj do `main`, nepoužívaj `--force` ani `reset --hard`.
