# AGENTS.md - Pravidlá práce v projekte EOS

Tento súbor je trvalá inštrukcia pre Codex a ďalších agentov pracujúcich v repozitári EOS.

## Základné pravidlá

1. Vždy rešpektuj `docs/governance/EOS-000_Development_Manifesto.md`.
2. Neuvádzaj neoverené strojárske údaje ako fakty.
3. Nikdy nezamieňaj normy, záväzné požiadavky a odporúčania.
4. Do kalkulačného kódu nepridávaj hardcoded technické hodnoty.
5. Kód má počítať, databáza má niesť znalosti a dokumentácia má vysvetľovať.
6. Vytváraj testovateľný, modulárny a udržiavateľný kód.
7. Používaj UTF-8.
8. Projektové a používateľské dokumenty píš po slovensky s diakritikou.
9. Programové identifikátory, JSON polia a názvy tried píš po anglicky.
10. Zachovávaj spätnú dohľadateľnosť cez ID, zdroje, verzie a revízie.
11. Veľké architektonické zmeny nevykonávaj bez ADR.
12. Najprv navrhni riešenie a až potom implementuj, ak používateľ nepožiada inak.
13. Integračnú validáciu JSON Schema nereportuj ako úspešnú, ak chýba runtime závislosť `jsonschema`.

## Zakázané správanie

- Nepridávaj konkrétne materiálové, technologické, strojové alebo cenové hodnoty bez zdroja.
- Nevytváraj databázový server bez samostatného rozhodnutia.
- Neimplementuj používateľské rozhranie vo fáze architektúry.
- Neimplementuj kalkulačky, kým nie sú schválené dátové kontrakty.
- Neodstraňuj historické záznamy bez náhrady alebo dôvodu.
- Nepoužívaj exporty ako autoritatívny zdroj znalostí.

## Povinné kontroly

Pred dokončením práce over:

- súlad s `EOS-000`,
- správne ID a názov súboru,
- zdrojovú klasifikáciu,
- neprítomnosť neoverených technických hodnôt,
- či zmena nevyžaduje ADR.
