---
name: eos-governance-check
description: Záverečná kontrola súladu s pravidlami EOS (EOS-000, AGENTS.md, TECH_STACK.md) pred ukončením akejkoľvek práce v repozitári. Použi vždy pred hlásením „hotovo“.
---

# Záverečná kontrola EOS

Prejdi každý bod a pri každom uveď v hlásení PASS, FAIL alebo N/A s krátkym dôvodom.

## Obsah

1. **Žiadne neoverené technické hodnoty.** Žiadne materiálové, strojové, technologické, časové ani cenové hodnoty. Výnimkou sú záznamy so zdrojom a klasifikáciou N/L/P/V.
2. **Normy a odporúčania nie sú zmiešané.** Odporúčanie sa netvári ako norma.
3. **Fixtúry sú fiktívne** a nepripomínajú reálne dáta.

## Štruktúra

4. Súbory majú správne **ID a názov** podľa EOS-002 a EOS-003. Dokumenty majú governance hlavičku a Change History.
5. Zmena je v **správnom module** a dodržiava povolené závislosti (EOS-001 §4).
6. Informácie sa **neduplikujú**. Namiesto kópie je odkaz.
7. Dokumenty sú **po slovensky s diakritikou**, identifikátory po anglicky, súbory v UTF-8.

## Technika

8. Nepribudla **žiadna závislosť ani nástroj** mimo TECH_STACK.md.
9. **Testy** prebehli podľa skillu `eos-run-tests` a výsledok je uvedený presne.
10. Ak sa menila architektúra, existuje **ADR** (skill `eos-adr`).

## Stav projektu

11. Horná sekcia `ROADMAP.md`, `BACKLOG.md` a `CHANGELOG.md` zodpovedajú skutočnosti. Stav nie je nadhodnotený (`IMPLEMENTED` ≠ `COMPLETE`).
12. **Nezačala sa ďalšia fáza** bez zadania.

## Hlásenie

Na koniec napíš krátke zhrnutie: čo sa zmenilo, výsledok testov, zoznam bodov s FAIL a otvorené otázky pre používateľa.
