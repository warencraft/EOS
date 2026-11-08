# ADR-0019 - Keep real job intake outside git

**Status:** Draft  
**Date:** 2026-11-06  

## Context

Marco (Chief Engineering Knowledge Architect) a Robino (Software Architect) sa dohodli, že Marco nahrá celú reálnu zákazku s výkresmi a ďalšími podkladmi. Cieľ: overiť model EOS na jednom skutočnom prípade od dopytu po ponuku (vertical slice, `docs/handoff/2026-11-04_otazky.md`, otázky 6 až 8).

Dnes na to nie je miesto ani pravidlo:

- projekt je v etape A (TECH_STACK.md §2); reálne záznamy patria do etapy B,
- entita Job nie je navrhnutá; existuje iba formát ID `JOB-yyyy-xxxx` (ADR-0008, EOS-003),
- `data/` je určený pre znalostné záznamy v gite, nie pre surové súbory zákazníka,
- výkresy a ponuky sú dôverné údaje zákazníka a zväčša binárne súbory; repozitár sa dá stiahnuť bez prihlásenia,
- otázka 8 v `docs/handoff/2026-11-04_otazky.md`: citlivé dáta nesmú ísť na GitHub ani do AI.

Rozhodnutie o úložisku a rozsahu urobil Robino 2026-11-06 (súbory mimo gitu; teraz iba príjem a súpis, bez návrhu Job).

## Decision

1. **Priečinok `intake/` mimo gitu.** `.gitignore` ignoruje `intake/*` okrem `intake/README.md`. Jedna zákazka = `intake/JOB-yyyy-xxxx/` s podpriečinkami podľa druhu podkladu (výkresy, modely, dopyt, ponuka, objednávka, výroba, merania, korešpondencia, iné).
2. **Manifest zákazky.** `intake/JOB-yyyy-xxxx/manifest.json` podľa `scripts/job_intake_manifest.schema.json`: predbežné `jobRef`, názov, dôvernosť (`internal` / `confidential` / `restricted`, predvolene `confidential`), výslovný súhlas `aiProcessingAllowed` (predvolene `false`) a pre každý súbor cesta, kategória, SHA-256, veľkosť, `sourceClass` (N/L/P/V podľa EOS-000 alebo `null`), voliteľne revízia dokumentu a popis.
3. **Nástroj `scripts/job_intake.py`** (štandardná knižnica + `jsonschema`, etapa A): `new` založí zákazku, `scan` doplní nové a zmenené súbory, `check` overí manifest, súbory a kontrolné súčty a hlási chybu, ak je súbor z `intake/` v gite.
4. **Hranica.** Manifest je nástrojový súpis, nie znalostný záznam, nie entita Job a nie zdroj pravdy. Schéma manifestu je preto v `scripts/`, nie v `schemas/`, a nie je v schema indexe. Znalosť zo zákazky vznikne až prevodom na záznamy so SourceReference po návrhu Job a prechode do etapy B.
5. **AI.** Agent obsah súborov v `intake/` nečíta ani nespracúva, kým to vlastník zákazky výslovne nepovolí (`aiProcessingAllowed: true` a zadanie). Manifest (názvy, kategórie, súčty) čítať smie.

## Alternatives Considered

| Možnosť | Posúdenie |
| --- | --- |
| Súbory zákazky v gite | Jednoduché zdieľanie, ale dôverné údaje zákazníka na GitHube, binárne súbory v histórii natrvalo. Zamietnuté. |
| Git LFS | Rieši veľkosť, nie dôvernosť; nová služba a nástroj mimo TECH_STACK.md. |
| Externé úložisko s odkazmi v gite | Vhodné neskôr pre zdieľanie medzi ľuďmi; teraz zbytočná závislosť. Manifest s kontrolnými súčtami umožní prechod bez zmeny formátu. |
| Navrhnúť hneď entitu Job | Vyžaduje doménové rozhodnutia o identite a rozsahu Job (Chief Engineering Knowledge Architect). Príjem podkladov ich nepotrebuje. |

## Consequences

- Marco môže zákazku nahrať hneď, bez čakania na Job a etapu B.
- Podklady sú overiteľné (kontrolné súčty) a ich zdroj sa zaradí (N/L/P/V) už pri príjme.
- Zdieľanie a zálohu podkladov treba riešiť mimo gitu.
- Testy pribudnú v `tests/test_job_intake.py`; produkčné schémy, validátor ani entity sa nemenia.

## Risks

- Podklady existujú iba na jednom počítači: strata pri poruche. Opatrenie: záloha mimo gitu (README v `intake/`).
- Niekto obíde `.gitignore` (`git add -f`). Opatrenie: `check` hlási chybu pre každý súbor z `intake/` v gite.
- Manifest sa môže rozísť s neskorším návrhom Job. Opatrenie: manifest nie je zdroj pravdy; formát sa môže zmeniť bez migrácie znalostí.

## Related Documents

- `docs/governance/EOS-000_Development_Manifesto.md` (klasifikácia N/L/P/V)
- `adr/ADR-0008_Use_hierarchical_identifiers_for_job_owned_entities.md`, `docs/governance/EOS-003_Identification_and_Versioning.md`
- `adr/ADR-0018_Define_target_technology_stack.md`, `TECH_STACK.md`
- `intake/README.md`, `scripts/job_intake.py`, `scripts/job_intake_manifest.schema.json`
- `docs/handoff/2026-11-04_otazky.md`

## Review Date

Pri návrhu entity Job alebo pri prechode do etapy B, podľa toho, čo nastane skôr.
