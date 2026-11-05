# Odovzdanie 2026-11-04 – Guardrails pre AI agentov a technologický rámec

**Pre koho:** Chief Engineering Knowledge Architect a jeho AI agenti (Claude, Codex…)  
**Vetva:** `tools/ai-guardrails`  
**Typ zmeny:** iba nové súbory a doplnky dokumentácie. Schémy, validátor, testy ani fixtúry sa nemenia.

> **Pre AI agenta:** tento súbor je úplný kontext zmeny. Prečítaj ho celý, potom `CLAUDE.md` a `TECH_STACK.md`. Na pochopenie zmeny nemusíš čítať nič iné.

## 1. Prečo

1. **Agenti si vyberali technológie a rozhodnutia sami.** Pre etapy po dátových kontraktoch (databáza, kalkulačky, aplikácia, exporty) neexistovalo rozhodnutie. Teraz je v ADR-0018.
2. **Agenti robili aj doménové rozhodnutia.** Príklad: v CDR-0021 rozhodol agent, či `MAC` znamená konkrétny stroj alebo typ stroja. Teraz sú roly rozdelené (časť 3).
3. **Testy sa rozrastali.** 671 fixtúr a 130 KB v jednom súbore (vyriešené v ADR-0017). Nový skill `eos-write-tests` bráni, aby sa to zopakovalo.
4. **Práca s gitom a GitHubom bola ručná a neznáma.** Skill `eos-git-publish` ju urobí za teba a ťahák ju vysvetlí.
5. **Projekt nebol vidieť.** `scripts/export_viewer.py` vygeneruje HTML prehľad schém, histórie a rozhodnutí.

## 2. Čo pribudlo

| Súbor | Čo to je | Treba čítať? |
| --- | --- | --- |
| `adr/ADR-0018_Define_target_technology_stack.md` | **rozhodnutie** o stacku po etapách A–E a o rolách | áno |
| `TECH_STACK.md` | technologický rámec: aktuálna etapa, povolené a zakázané technológie | áno |
| `CLAUDE.md` | vstupné pravidlá pre Claude Code; načítava `AGENTS.md` a `TECH_STACK.md` | áno, krátke |
| `.agents/skills/eos-run-tests/` | ako spustiť testy a poctivo nahlásiť výsledok | agent |
| `.agents/skills/eos-write-tests/` | ako písať testy a fixtúry bez duplicít (nadväzuje na ADR-0017 a `ENTITY_PROFILES`) | agent |
| `.agents/skills/eos-schema-change/` | postup pre novú entitu alebo zmenu schémy | agent |
| `.agents/skills/eos-adr/` | kedy a ako napísať ADR | agent |
| `.agents/skills/eos-governance-check/` | záverečná kontrola podľa EOS-000 a AGENTS.md | agent |
| `.agents/skills/eos-git-publish/` | vetva → commit → push → pull request, s poistkami | agent |
| `.github/pull_request_template.md` | šablóna, ktorú GitHub ponúkne pri každom PR | – |
| `docs/manual/GIT_TAHAK.md` | návod na git pre človeka | podľa potreby |
| `scripts/export_viewer.py`, `scripts/viewer_sk.json` | generátor HTML prehľadu projektu (iba štandardná knižnica) | – |
| `docs/handoff/2026-11-04_otazky.md` | otázky na spoločné stretnutie | áno |

Upravené súbory: `AGENTS.md` (nová sekcia na konci), `docs/INDEX.md` (riadok ADR-0018), `CHANGELOG.md` (nový záznam).

## 3. Kľúčové rozhodnutia

### Roly (ADR-0018)

| Rola | Rozhoduje o |
| --- | --- |
| **Chief Engineering Knowledge Architect** (ty) | obsah: čo EOS vie, hranice entít, zdroje, normy, pravidlá z praxe |
| **Software Architect** (IT strana) | technika: stack, architektúra kódu, etapy, CI, git |
| **AI agent** | implementácia v rámci týchto rozhodnutí; nevyberá technológie, nerobí doménové rozhodnutia |

### Technológie po etapách

| Etapa | Cieľ | Technológie |
| --- | --- | --- |
| **A – teraz** | kontrakty, validácia, testy | Python, `jsonschema`, JSON v gite |
| B | prvé reálne dáta, vyhľadávanie | + SQLite (generovaná kópia, JSON zostáva zdrojom pravdy) |
| C | kalkulačky, cenová ponuka | + `openpyxl` |
| D | interná webová aplikácia | + FastAPI, Jinja, HTMX (voľba frameworku sa potvrdí pri vstupe do etapy) |
| E | AI čítanie výkresov | + Claude API |

Pevné pravidlá: **iba Python**, **JSON Schema je jediný zdroj pravdy**, bez ORM, bez React/Django, bez PostgreSQL do samostatného ADR.

## 4. Ako to použiť

Skilly sú v `.agents/skills/`. Tento priečinok **Codex načíta automaticky** a Claude Code ich nájde cez odkaz v `CLAUDE.md`. Formát `SKILL.md` je pre oba nástroje rovnaký.

**Codex (CLI alebo rozšírenie v editore):** skill sa použije sám, keď úloha zodpovedá jeho popisu. Ručne ho vyvoláš príkazom `/skills` alebo napísaním `$` a názvu, napr. `$eos-git-publish`. Codex číta aj `AGENTS.md`, ktorý odkazuje na `TECH_STACK.md`.

**Claude Code:** v priečinku projektu spusti `claude`. `CLAUDE.md` sa načíta sám a odkazuje na skilly. Napríklad:

- „Implementuj Machine podľa CDR-0021.“ (agent použije `eos-schema-change` a `eos-write-tests`)
- „Ulož to a pošli na GitHub.“ (agent použije `eos-git-publish`)

**HTML prehľad:** `python scripts/export_viewer.py` → otvor `exports/viewer/index.html`.

## 5. Čo od teba potrebujeme

1. Prezri si pull request (záložka **Files changed**) a ak súhlasíš, klikni na **Merge pull request**.
2. Prečítaj `docs/handoff/2026-11-04_otazky.md` a poďme si k tomu sadnúť.
3. **Doménové rozhodnutie:** potvrď, či má `MAC` (Machine) znamenať konkrétny fyzický stroj, ako to v CDR-0021 §64 rozhodol agent. Je to tvoje rozhodnutie, nie jeho.

## 6. Čo sa zámerne nezmenilo

- žiadna schéma, validačné pravidlo, test ani fixtúra,
- žiadne Accepted/Approved ADR, RFC ani CDR,
- žiadna nová runtime závislosť (`pyproject.toml` bez zmeny).
