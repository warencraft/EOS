---
name: eos-pre-commit-review
description: Kontrola zmien pred každým commitom a pushom (Marco aj Robino). Overí testy, pravidlá EOS a rozsah zmeny, nálezy rozdelí na doménové pre Marca a technické pre Robina a zapíše ich ako správy na stavovú nástenku (status/spravy/), ktoré idú do toho istého commitu. Použi pred „commitni“, „pushni“, „sprav PR“, vždy zo skillu eos-git-publish, alebo keď používateľ povie „skontroluj zmeny“.
---

# Kontrola pred commitom → správy pre Marca a Robina

Cieľ: nikto neodošle zmenu, ktorú agent neprezrel, a obaja vidia na nástenke (`/stav` v UI, ADR-0022), čo majú riešiť. Marco rieši doménu, Robino techniku. Agent nerozhoduje za nich; zapíše nález a navrhne možnosti.

Kto commituje: zisti z kontextu (Marco = strojár, Robino = IT). Ak to nie je jasné, opýtaj sa jednou otázkou. Do správ píš `--autor agent`.

## Krok 1: Čo sa mení

```bash
git status --short
git diff --stat origin/main...HEAD
git diff --stat            # necommitnuté zmeny
git diff origin/main...HEAD
git diff
```

Prečítaj celý diff vrátane nových súborov. Pri veľkom diffe choď súbor po súbore.

## Krok 2: Povinné kontroly

1. Testy podľa `eos-run-tests` (presný počet passed/failed/skipped).
2. `python -m scripts.status kontrola` – formát správ a citlivé údaje na nástenke.
3. `python scripts/job_intake.py check` – nič z `intake/` nie je v gite.
4. Body zo `eos-governance-check`.

Ak testy alebo kontroly zlyhajú, je to nález so závažnosťou `blokuje`.

## Krok 3: Nálezy a komu patria

| Pre Marca (doména) – `--pre marco` | Pre Robina (technika) – `--pre robino` |
| --- | --- |
| nová alebo zmenená entita, pole, enum, katalóg | nová závislosť, nástroj, zmena `pyproject.toml` |
| technická hodnota bez zdroja a N/L/P/V | architektúra, moduly, mimo `TECH_STACK.md` / chýba ADR |
| agent alebo kód urobil doménové rozhodnutie (pravidlo, vzorec, predpoklad) | chýbajúce alebo slabé testy, preskočené testy |
| zmena rozsahu fázy, CDR, ROADMAP, BACKLOG | bezpečnosť: cesty k súborom, vstupy z formulárov, tajomstvá |
| norma zmiešaná s odporúčaním | kód v `scripts/`, UI, CI, git hygiena |
| výsledok, ktorý strojár musí overiť na výkrese alebo v praxi | výkon, údržba, duplicita kódu |

Týka sa oboch (napr. ADR, ktoré mení aj doménu) → `--pre oba`.
Typ správy: `kontrola` (súhrn), `rozhodnutie` (treba vybrať možnosť), `otazka`, `info`.
Závažnosť: `blokuje` (necommitovať, kým sa nevyrieši), `dolezite` (vyriešiť pred merge), `poznamka`.

## Krok 4: Zapíš správy

Pre každého, kto má aspoň jeden nález, **jedna súhrnná správa** typu `kontrola`. Každé rozhodnutie, ktoré musí niekto urobiť, je **samostatná správa** typu `rozhodnutie` s možnosťami A/B/C, aby sa dala vyriešiť zvlášť.

```bash
python -m scripts.status nova --autor agent --pre marco --typ kontrola --zavaznost dolezite \
  --tema "Kontrola: <krátky popis zmeny>" --subor <cesta> --subor <cesta> <<'TEXT'
Čo sa mení: …
Na čo sa pozrieť:
1. …
2. …
Testy: N passed, 0 failed, M skipped.
TEXT
```

Pravidlá textu:

- Po slovensky, krátko, konkrétne: súbor, čo je zle, čo navrhuješ. Bez git žargónu pre Marca.
- **Žiadne mená zákazníkov, názvy zákaziek, ceny ani hodnoty z reálnych zákaziek.** Odkazuj iba číslom `JOB-…`. Nástroj takú správu odmietne, ale nespoliehaj sa na to.
- Ak nič nenašiel, zapíš jednu správu `--pre oba --typ info --zavaznost poznamka` „Kontrola bez nálezov“ s výsledkom testov.
- Pred zapísaním si pozri otvorené správy (`python -m scripts.status zoznam`). Neduplikuj; ak zmena niektorú otvorenú správu rieši, označ ju: `python -m scripts.status vyries <id> --kto agent`.

## Krok 5: Výsledok pre používateľa

1. Ak je nález `blokuje`, **necommituj**. Vysvetli, čo treba opraviť, a ponúkni opravu.
2. Inak pridaj nové súbory zo `status/spravy/` do toho istého commitu (`git add status/spravy/`).
3. Povedz používateľovi jednou-dvoma vetami, koľko správ vzniklo pre Marca a koľko pre Robina, a že ich uvidia v UI na stránke **Stav** po stiahnutí zmien.
4. Pokračuj v `eos-git-publish` (potvrdenie, commit, push, PR). Do tela PR pridaj sekciu „Kontrola agenta“ s odkazmi na nové súbory správ.

## Čo nerobiť

- Neopravuj doménové nálezy sám. Zapíš ich Marcovi.
- Nemeň ani nemaž cudzie správy okrem označenia „vyriešené“, keď to zmena preukázateľne rieši.
- Nepíš do `status/spravy/` nič iné než cez `python -m scripts.status` alebo UI.
