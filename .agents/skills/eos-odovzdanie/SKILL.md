---
name: eos-odovzdanie
description: Zhrň rozbehnutú prácu do odovzdávacieho dokumentu, aby ju ďalší agent alebo človek vedel prevziať. Použi na konci dlhšej session, pred prestávkou, keď práca ostáva nedokončená, alebo keď používateľ povie „odovzdaj to“, „zhrň to pre ďalšieho“, „pokračujeme zajtra“.
---

# Odovzdanie práce

Cieľ: ďalší agent (alebo Robino, alebo Marco) prevezme prácu bez toho, aby musel čítať celý rozhovor.

Pôvod: upravené z `handoff` z [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, pozri `.agents/skills/THIRD_PARTY_NOTICES.md`). Rozdiel: v EOS sa odovzdanie ukladá do repozitára (`docs/handoff/`), lebo ho čítajú obaja, Marco aj Robino.

## Kam

`docs/handoff/YYYY-MM-DD_<tema>.md`. Ak súbor s rovnakou témou z toho dňa existuje, doplň ho, nevytváraj druhý.

Ak používateľ povie, na čo bude ďalšia session (napr. „zajtra testy“), prispôsob tomu obsah.

## Obsah

```markdown
# Odovzdanie: <téma>

**Pre koho:** <ďalší agent / Robino / Marco>
**Dátum:** YYYY-MM-DD
**Vetva:** <názov vetvy alebo „bez zmien v kóde“> · **PR:** <odkaz alebo „zatiaľ nie“>

## Cieľ

Jedna-dve vety: čo sa má dosiahnuť a pre koho.

## Hotové

- <čo je urobené, s cestou k súboru alebo commitu>

## Rozpracované

- <čo je začaté a v akom stave, čo presne ostáva>

## Rozhodnuté

- <rozhodnutie> (kto: Marco / Robino, kde je zapísané)

## Otvorené

- <otázka> → rozhodne <Marco / Robino>; <kde sa sleduje: nástenka, dotazník, ADR>

## Ďalší krok

1. <prvý konkrétny krok, ktorým má ďalší agent začať>

## Odporúčané skilly

- `<skill>`: <kedy ho použiť pri ďalšej práci>

## Na prečítanie

- <cesty k ADR, plánom, súborom, ktoré treba poznať>
```

## Pravidlá

- **Neopakuj, čo už je zapísané** v ADR, plánoch, commitoch alebo na nástenke. Daj odkaz (cesta alebo URL).
- **Žiadne citlivé údaje:** API kľúče, heslá, e-mailové adresy, mená zákazníkov, ceny a obsah súborov z `intake/` do dokumentu nepatria. Súbor ide do gitu.
- **Rozlišuj fakty a predpoklady.** Čo nie je overené, označ „neoverené“.
- **Stav testov píš presne** (počet, ktorá sada, či chýbali závislosti). „Testy prechádzajú“ iba vtedy, keď sa naozaj spustili všetky (`eos-run-tests`).
- Píš po slovensky. Pre Marca jednoducho, pre agenta môže byť technickejší.
- Na konci povedz používateľovi cestu k súboru. Commit a PR iba cez `eos-git-publish`, ak o to požiada.
