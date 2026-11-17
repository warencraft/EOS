# ADR-0021 - Local UI v0 and working calculation

**Status:** Accepted  
**Date:** 2026-11-16  
**Decided by:** Software Architect (IT strana projektu)  

## Context

Vertical slice zákazky V949 (2026-11-15, `intake/_analyzy/vertical-slice-V949/`, mimo gitu) ukázal:

- dnešný model EOS (etapa A) neunesie ani jednu ponuku: chýba zákazka, operácia a kalkulácia,
- celá znalosť potrebná na ponuku je v excelovej kalkulačnej šablóne a kopírovaním do nej vznikajú chyby (iná sadzba v dvoch riadkoch, nejednotné množstvá, nezapočítané položky, chýbajúci výkres v rozpise V795),
- strojár (Chief Engineering Knowledge Architect) zatiaľ systém nevidí; pracuje s JSON súbormi a dlhými dokumentmi.

ADR-0018 zaraďuje webovú aplikáciu do etapy D. Čakať na etapy B a C by znamenalo ďalšie mesiace bez niečoho, čo sa dá používať a zlepšovať na reálnych zákazkách.

## Decision

1. **Etapa D sa otvára v obmedzenom rozsahu „UI v0“.** Povolené je iba to, čo v ADR-0018 patrí do etapy D: `fastapi`, `uvicorn`, `jinja2` a HTMX ako jeden statický súbor (`scripts/web/static/htmx-1.9.12.min.js`, licencia 0BSD). Na import excelovej šablóny `openpyxl` (etapa C) a `xlrd` (staré `.xls`). Všetko sú **voliteľné** závislosti (`pip install -e .[ui,import]`); jadro EOS (validácia, testy kontraktov) ich nepotrebuje.
2. **Aplikácia beží iba lokálne** (`python -m scripts.web`, `127.0.0.1`). Nemá prihlásenie, nič neposiela von a číta iba `intake/`.
3. **Pracovná kalkulácia nie je kontrakt EOS.** Formát je opísaný v `scripts/calc/kalkulacia.schema.json` (rovnako ako manifest príjmu v ADR-0019): nie je v `schemas/`, nie je v indexe a neukladá sa do `data/`. Súbory sú v `intake/_eos/kalkulacie/<jobRef>.json`, teda mimo gitu a mimo priečinkov zákaziek, takže ich `job_intake.py check` nepovažuje za podklady.
4. **Výpočet je čistá funkcia** (`scripts/calc/kalkulacia.py`). Sadzby, časy, ceny a množstvá prichádzajú zo vstupu; v kóde nie sú žiadne technické ani obchodné hodnoty (ADR-0003).
5. **Importér šablóny nič neodhaduje.** Stĺpce hľadá podľa textu hlavičky. Čo v šablóne nesedí, vráti ako upozornenie s bunkou a dopadom v €. Výsledok porovná s ponukou z hárku KALKULAČNÍ.
6. **Úpravy v UI sa zapisujú do histórie** (`zmeny`: čas, pole, pôvodná a nová hodnota). Opätovný import ich prepíše; UI na to upozorní.
7. **Kalkulácia v0 sa nahradí** entitou Job, operáciou a kalkuláciou po ich návrhu (CDR, rozhoduje Chief Engineering Knowledge Architect). Formát v0 sa vtedy nemigruje automaticky; slúži ako zoznam požiadaviek na tieto entity.

## Alternatives Considered

| Možnosť | Posúdenie |
| --- | --- |
| Čakať na etapy B a C | Čisté poradie, ale mesiace bez použiteľného výsledku a bez spätnej väzby od strojára. |
| Statický HTML export | Ostáva v etape A, ale bez úprav a prepočtu sa z neho nestane pracovný nástroj. |
| Stránka hostovaná na claude.ai | Najrýchlejšie zdieľanie, ale dôverné údaje zákazníkov by boli online a mimo repozitára. |
| Navrhnúť hneď entitu Job ako kontrakt EOS | Doménové rozhodnutie Chief Engineering Knowledge Architect. UI v0 mu dá podklady, nerozhoduje zaň. |

## Consequences

- Strojár vidí zákazky, kalkuláciu, chyby šablóny a vplyv sadzby na cenu. Časy môže meniť a hneď vidí novú cenu.
- Pribudli voliteľné závislosti; testy UI a importu sa bez nich preskočia (10 testov). Plná sada sa spúšťa s `.[ui,import]`.
- `TECH_STACK.md` uvádza etapu A ako hlavnú a UI v0 ako povolenú výnimku z etapy D.
- Ďalšie funkcie UI (zadávanie nových zákaziek, entity EOS v databáze, viac používateľov) potrebujú samostatné rozhodnutie.

## Risks

- **Formát v0 sa stane neformálnym štandardom.** Opatrenie: je mimo `schemas/`, označený ako nástrojový a dočasný; UI to uvádza v pätičke.
- **Importér je naviazaný na jednu excelovú šablónu.** Iná šablóna skončí chybou importu, nie tichým nesprávnym výsledkom.
- **Kalkulácie existujú iba na jednom počítači.** Rovnaké riziko a opatrenie ako pri `intake/` (ADR-0019).

## Related Documents

- `adr/ADR-0018_Define_target_technology_stack.md`, `TECH_STACK.md`
- `adr/ADR-0019_Keep_real_job_intake_outside_git.md`, `intake/README.md`
- `docs/manual/UI.md`
- `scripts/calc/`, `scripts/web/`, `tests/test_kalkulacia.py`, `tests/test_web_ui.py`

## Review Date

Pri návrhu entity Job alebo 2027-02-01, podľa toho, čo nastane skôr.
