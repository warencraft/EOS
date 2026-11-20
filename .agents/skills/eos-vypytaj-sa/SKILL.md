---
name: eos-vypytaj-sa
description: Rozhovor otázka po otázke, kým nie je jasné, čo používateľ chce. Použi, keď Marco alebo Robino prinesie nápad, novú funkciu, pravidlo z praxe alebo plán a ešte nie je jasné, čo presne treba urobiť, alebo keď povie „vypytuj sa ma“, „prejdime to“, „opýtaj sa ma“.
---

# Vypytuj sa, kým to nie je jasné

Cieľ: po rozhovore vieš ty aj používateľ presne, čo sa má urobiť, a nič nie je potichu domyslené. Kým rozhovor neskončí, **nič neimplementuj.**

Pôvod: upravené z `grilling` z [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, pozri `.agents/skills/THIRD_PARTY_NOTICES.md`).

## Ako sa pýtať

1. **Najprv si urob mapu rozhodnutí.** Každé rozhodnutie môže otvoriť ďalšie. Napríklad „chcem evidovať nástroje“ otvorí otázky, či ide o vlastný katalóg alebo súčasť stroja, čo je povinný údaj a odkiaľ budú zdroje.
2. **Pýtaj sa v kolách.** V jednom kole sa opýtaj iba na to, čo sa dá rozhodnúť už teraz bez hádania odpovedí na iné otázky. Otázka, ktorá závisí od inej otvorenej otázky, ide do ďalšieho kola.
3. **V jednom kole najviac 5 otázok.** Pri Marcovi radšej 2–3.
4. **Ku každej otázke pridaj svoj návrh odpovede.** Otázku formuluj tak, aby odpoveď „áno“ znamenala súhlas s návrhom.
5. Po odpovediach prepočítaj mapu a pokračuj ďalším kolom.

Formát kola:

```
❓ **O1 – <krátky názov>:** <otázka, prípadne možnosti A/B/C s dôsledkami>

➡️ Návrh: <tvoja odpoveď a jedna veta prečo>

---

❓ **O2 – …**
```

## Fakty si zisti sám, rozhodnutia nechaj ľuďom

- **Fakty** (čo je v schémach, v ADR, v kóde, čo už existuje) si zisti v repozitári sám. Nepýtaj sa na nič, čo sa dá dohľadať. Kým hľadáš, môžeš sa pýtať na otázky, ktoré od toho nezávisia.
- **Doménové rozhodnutia** (čo je materiál, stroj, proces, aké pravidlo platí v praxi, aké zdroje platia) rozhoduje **Marco**. Ponúkni možnosti s dôsledkami, ale nerozhoduj za neho.
- **Technické rozhodnutia** (knižnica, štruktúra kódu, etapa, server) rozhoduje **Robino**. Ak sa takáto otázka objaví v rozhovore s Marcom, Marca ňou nezaťažuj. Zapíš ju ako otvorenú otázku pre Robina.
- Do návrhov **nedávaj konkrétne technické, cenové ani materiálové hodnoty bez zdroja** (AGENTS.md). Namiesto čísla navrhni, odkiaľ ho vziať.
- Obsah reálnych zákaziek v `intake/` nečítaj bez `aiProcessingAllowed: true` a výslovného zadania (ADR-0019).

## Ako hovoriť

- S Marcom po slovensky, jednoducho, bez programátorského žargónu. Odborný pojem z kódu vysvetli jednou vetou.
- Používaj pojmy z glosára EOS (`docs/rfc/RFC-0003_EOS_Engineering_Glossary.md`), nie vlastné nové slová.
- Ak odpoveď nebola jasná, nepredpokladaj. Opýtaj sa znova inými slovami.

## Koniec rozhovoru

Rozhovor končí, keď v mape nie je žiadna otvorená otázka, ktorú vie používateľ rozhodnúť.

1. Napíš krátke zhrnutie: **čo je rozhodnuté**, **čo ostáva otvorené a kto to rozhodne**, **čo by sa urobilo ako ďalší krok**.
2. Opýtaj sa: „Sedí to takto?“ Kým používateľ nepotvrdí, nič ďalšie nerob.
3. Po potvrdení ponúkni zápis (nič nezapisuj bez súhlasu):
   - zhrnutie do `docs/handoff/YYYY-MM-DD_<tema>.md`,
   - otvorené technické otázky na nástenku: `python -m scripts.status nova --autor agent --pre robino --typ otazka ...`,
   - otvorené doménové otázky pre Marca dotazníkom (skill `eos-dotaznik`),
   - ak ide o zmenu architektúry alebo pravidiel, návrh ADR (skill `eos-adr`, vždy `Status: Draft`).
4. Implementácia je **samostatné zadanie**. Rozhovor ju nezačína (CLAUDE.md: ďalšiu fázu nezačínaj bez samostatného zadania).
