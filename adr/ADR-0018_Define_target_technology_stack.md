# ADR-0018 - Define target technology stack

**Status:** Accepted  
**Date:** 2026-11-04  
**Decided by:** Software Architect (IT strana projektu)  

## Context

Platné ADR (0002, 0009–0013) určujú technológie iba pre etapu dátových kontraktov: Python, JSON Schema Draft 2020-12, knižnicu `jsonschema`, JSON súbory a `unittest`. EOS-001 §7 spomína budúci prechod na SQLite alebo PostgreSQL. Pre ďalšie moduly z EOS-001 §3 (úložisko, kalkulátory, exporty, rozhranie, automatizácia) však neexistuje žiadne rozhodnutie.

Bez rozhodnutia si AI agenti pri každej novej úlohe vyberajú technológie sami. Hrozí, že vznikne mix frameworkov, ktorý projekt dlhodobo nebude vedieť udržať (EOS-000 §7, §10).

Obmedzenia, z ktorých návrh vychádza:

- systém je interný, používa ho jedna firma a spočiatku jeden až niekoľko ľudí,
- vlastník obsahu je strojár, nie programátor; kód píšu prevažne AI agenti,
- hlavné prostredie je Windows, vývoj prebieha aj na macOS,
- spätná dohľadateľnosť (ID, revízie, zdroje) je dôležitejšia ako výkon,
- dát bude spočiatku málo (stovky až tisíce záznamov).

## Decision

### 1. Jeden jazyk: Python

Celý systém vrátane rozhrania sa píše v Pythone (`>=3.11`, vývoj a CI na 3.12). Bez JavaScriptového frameworku a bez druhého backendového jazyka.

### 2. Zdroj pravdy zostáva JSON Schema

JSON Schema v `schemas/` je jediná definícia tvaru dát. Kód (Python triedy, databázové tabuľky, formuláre) sa od nej odvodzuje, nikdy naopak. Pydantic, ORM modely ani migračné nástroje sa nestávajú druhým zdrojom pravdy.

### 3. Etapy

Každá etapa smie používať iba technológie svojej a predchádzajúcich etáp. Prechod do ďalšej etapy schvaľuje Software Architect po dohode s Chief Engineering Knowledge Architect (pripravenosť obsahu a dát). Pridanie konkrétnej závislosti v rámci schválenej etapy už nepotrebuje ďalšie ADR, iba zápis do `TECH_STACK.md` a `pyproject.toml`.

| Etapa | Cieľ | Technológie | Úložisko |
| --- | --- | --- | --- |
| **A. Kontrakty** (aktuálna) | schémy, validácia, testy | štandardná knižnica, `jsonschema` | JSON súbory v gite |
| **B. Dáta a prehľad** | prvé reálne záznamy, vyhľadávanie, prehľad | + `sqlite3` (štandardná knižnica), CLI cez `argparse`, statický HTML export | JSON v gite = zdroj pravdy; SQLite = generovaná kópia na čítanie |
| **C. Výpočty a výstupy** | kalkulátory, cenová ponuka | + `openpyxl` (Excel); PDF podľa samostatného rozhodnutia | ako B |
| **D. Interná aplikácia** | prezeranie a zadávanie dát v prehliadači | + `fastapi`, `uvicorn`, `jinja2`, HTMX (jeden statický JS súbor) | SQLite ako pracovná databáza + export do JSON pre git a audit |
| **E. AI asistencia** | čítanie výkresov, návrhy postupov | + `anthropic` SDK v izolovanom module | ako D |

PostgreSQL sa zvažuje až pri súčasnej práci viacerých používateľov cez sieť. Vyžaduje vlastné ADR.

### 4. Cieľová štruktúra kódu

```
src/eos/
  validation/   # dnešné scripts/validation (presun = samostatná úloha)
  store/        # načítanie JSON, build SQLite, dotazy (bez ORM, čisté SQL)
  calc/         # kalkulátory: čisté funkcie, vstup = validované záznamy
  export/       # HTML prehľad, Excel, PDF
  web/          # FastAPI + Jinja šablóny (etapa D)
  ai/           # volania AI, výstupy vždy ako návrh (etapa E)
  cli.py        # príkaz `eos`: validate, build-db, export, serve
```

### 5. Pravidlá naprieč etapami

- **Kalkulátory** sú čisté funkcie bez prístupu k súborom a sieti. Každý výsledok nesie zoznam ID záznamov, z ktorých vznikol (EOS-000 §8, ADR-0003).
- **Databáza** sa pristupuje čistým SQL cez `sqlite3`. Schéma tabuliek sa generuje z JSON Schema.
- **Výstupy AI** a automatické odhady sa vždy označujú ako návrh, kým ich človek neschváli (EOS-001 §8).
- **Testy** zostávajú na `unittest`. CI beží na GitHub Actions.
- **Nástroje pre vývojára** (`ruff`) sú iba voliteľné dev závislosti.
- **Spustenie** je lokálne (`eos serve`). Kontajner (Docker) alebo server sa riešia až pri potrebe prístupu z viacerých počítačov.

## Alternatives Considered

| Možnosť | Výhody | Nevýhody | Verdikt |
| --- | --- | --- | --- |
| **FastAPI + Jinja + HTMX** | jeden jazyk, jednoduché, ľahko čitateľné pre AI aj človeka, JSON Schema ostáva pravdou | formuláre treba písať (alebo generovať zo schém) | **odporúčané pre D** |
| Django + admin | hotové CRUD rozhranie, prihlásenie a migrácie zadarmo | ORM modely by sa stali druhým zdrojom pravdy, ťažký framework | zamietnuté |
| Streamlit | veľmi rýchly prototyp | slabé na štruktúrované zadávanie dát, ťažko sa udržiava | iba na jednorazové experimenty |
| React / Next.js + API | moderné UI | druhý jazyk, build nástroje, náročné na údržbu pre jedného človeka | zamietnuté |
| PostgreSQL hneď | škálovanie, viac používateľov | server, správa, zálohy; teraz zbytočné | odložené |
| Pydantic modely ako zdroj pravdy | pohodlné v kóde | duplicita so schémami, rozpor s ADR-0002 | zamietnuté |
| Desktopová aplikácia (Qt, Tkinter) | bez prehliadača | ťažšia distribúcia a zdieľanie | zamietnuté |

## Roles

Toto ADR spresňuje roly z EOS-000 §4:

- **Chief Engineering Knowledge Architect** rozhoduje o obsahu: čo EOS vie, doménové hranice entít, zdroje, normy a pravidlá z praxe.
- **Software Architect** (IT strana projektu) rozhoduje o technike: jazyk, knižnice, úložisko, architektúra kódu, etapy, CI a spôsob práce s gitom.
- **AI agenti** (Claude, Codex…) implementujú v rámci týchto rozhodnutí. Sami nevyberajú technológie a nerobia doménové rozhodnutia.

## Consequences

- Agenti dostanú jasný rámec a nebudú vyberať technológie sami.
- Projekt môže hneď po uzavretí Machine prejsť do etapy B s prvými reálnymi dátami bez novej architektonickej diskusie.
- Presun `scripts/validation` do `src/eos/validation` je samostatná úloha s vlastnými testami. Teraz sa nerobí.
- `TECH_STACK.md` a `CLAUDE.md` odkazujú na toto ADR a vedú aktuálnu etapu.

## Risks

- HTMX je mladšia technológia ako React. Riziko je malé, lebo je to jeden súbor bez build nástrojov.
- Generovanie SQLite a formulárov zo schém treba navrhnúť poctivo, inak vznikne druhý zdroj pravdy.
- Pri viacerých používateľoch bude treba prihlásenie a možno PostgreSQL. To je mimo tohto ADR.

## Related Documents

- `docs/governance/EOS-000_Development_Manifesto.md`
- `docs/governance/EOS-001_System_Architecture.md`
- `adr/ADR-0002_Use_JSON_compatible_schemas_as_initial_data_contract.md`
- `adr/ADR-0003_Separate_engineering_knowledge_from_calculation_code.md`
- `adr/ADR-0013_Use_a_standards_compliant_JSON_Schema_validator.md`
- `TECH_STACK.md`

## Review Date

2027-02-01
