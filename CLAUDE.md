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
- **Výnimka UI v0 (ADR-0021):** `scripts/web/` (FastAPI + Jinja + HTMX) a `scripts/calc/` (pracovná kalkulácia, import šablóny). Kalkulácia nie je kontrakt EOS; jej formát je `scripts/calc/kalkulacia.schema.json` a súbory sú v `intake/_eos/` mimo gitu. Návod: `docs/manual/UI.md`.
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
6. Ponúkni uloženie a pull request (`eos-git-publish`); pred commitom vždy `eos-pre-commit-review`.

## Skilly

Skilly sú v `.agents/skills/<názov>/SKILL.md` (spoločný priečinok pre Codex aj Claude). `.claude/skills/` je ich generovaná kópia, lebo Claude Code hľadá skilly iba tam a odkaz (symlink) na Windows nefunguje spoľahlivo. Kópiu neupravuj. Po každej zmene v `.agents/skills/` spusti `python scripts/sync_claude_skills.py`, inak zlyhá `tests/test_claude_skills.py`. Keď úloha zodpovedá riadku nižšie, **najprv si prečítaj príslušný `SKILL.md`** a postupuj podľa neho.

| Skill | Kedy |
| --- | --- |
| `eos-run-tests` | po každej zmene kódu, schémy alebo fixtúry |
| `eos-schema-change` | nová entita, katalóg alebo zmena schémy |
| `eos-write-tests` | pred pridaním testu, fixtúry alebo neplatného prípadu |
| `eos-adr` | zmena architektúry, závislostí, etapy alebo pravidiel |
| `eos-governance-check` | vždy pred ukončením práce |
| `eos-spustit-ui` | „spusti EOS“, „otvor UI“, „aktualizuj aplikáciu“; stiahne verziu, pripraví prostredie a spustí UI |
| `eos-pre-commit-review` | pred každým commitom a pushom; nálezy zapíše na nástenku pre Marca (doména) a Robina (technika) |
| `eos-git-publish` | „ulož to“, „pushni“, „sprav PR“; všetko urob a vysvetli za používateľa |
| `eos-vypytaj-sa` | nový nápad, funkcia, pravidlo z praxe alebo plán, ktorý ešte nie je jasný; „vypytuj sa ma“; pred implementáciou |
| `eos-dotaznik` | rozhodnutie musí urobiť niekto iný (doména → Marco, technika → Robino); „sprav otázky pre Marca“ |
| `eos-vysvetli-inak` | „nerozumiem“, „povedz to jednoduchšie“, alebo je vidieť, že vysvetlenie nedošlo |
| `eos-odovzdanie` | koniec dlhšej session alebo nedokončená práca; „odovzdaj to“, „pokračujeme zajtra“ |

Štyri posledné skilly sú upravené z [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, `.agents/skills/THIRD_PARTY_NOTICES.md`). Ostatné skilly z toho repozitára sa v EOS nepoužívajú, lebo by sa zrazili s pravidlami a skillmi EOS (testy, review, PR, ADR).

## Príkazy

```bash
.venv/bin/python -m pip install -e .                    # Windows: .\.venv\Scripts\python ...
.venv/bin/python -m unittest discover -s tests -v       # celá sada
.venv/bin/python -m scripts.validation.cli <record.json> <schema_id>
python scripts/export_viewer.py                         # HTML prehľad → exports/viewer/
python scripts/job_intake.py check                      # príjem reálnej zákazky (intake/README.md)
```

## Nikdy

- nepoužívaj technológiu mimo aktuálnej etapy ani mimo `TECH_STACK.md`,
- nevkladaj reálne technické, cenové ani materiálové hodnoty bez zdroja; fixtúry sú fiktívne,
- nehlás testy ako úspešné, keď chýba `jsonschema` alebo sa nespustili všetky,
- nemeň Accepted/Approved ADR ani uzavreté CDR; navrhni amendment,
- necommituj do `main`, nepoužívaj `--force` ani `reset --hard`,
- necommituj nič z `intake/` (reálne zákazky) a nečítaj obsah ich súborov bez `aiProcessingAllowed: true` v manifeste a výslovného zadania (ADR-0019).
