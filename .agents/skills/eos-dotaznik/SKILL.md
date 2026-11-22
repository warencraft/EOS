---
name: eos-dotaznik
description: Z otvoreného rozhodnutia urob krátky dotazník, ktorý vyplní niekto iný (najčastejšie Marco pri doménových otázkach, alebo Robino pri technických). Použi, keď rozhodnutie nemôže urobiť ten, kto práve pracuje, alebo keď povie „sprav otázky pre Marca“, „dotazník“, „pošli mu to na vyplnenie“.
---

# Dotazník pre niekoho iného

Cieľ: dostať od človeka, ktorý vie viac (napr. Marco o praxi v dielni), presne tie odpovede, ktoré chýbajú. Dotazník musí ísť vyplniť bez ďalšieho vysvetľovania, aj na jedno prečítanie.

Pôvod: upravené z `to-questionnaire` z [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, pozri `.agents/skills/THIRD_PARTY_NOTICES.md`).

## Postup

1. **Komu to ide?** Ak to nie je jasné z rozhovoru, opýtaj sa jednou otázkou: Marco (doména), Robino (technika), alebo niekto iný. Podľa toho volíš jazyk a koľko kontextu treba.
2. **Čo potrebuješ späť?** Jednou otázkou zisti konkrétne rozhodnutia alebo fakty, bez ktorých sa nedá pokračovať. Fakty, ktoré sa dajú nájsť v repozitári, do dotazníka nedávaj. Zisti ich sám.
3. **Napíš dotazník** do `docs/handoff/YYYY-MM-DD_<tema>_otazky.md` podľa šablóny nižšie. Vzor tónu je `docs/handoff/2026-11-04_otazky.md`.
4. **Daj vedieť na nástenke**, aby to adresát videl v EOS v časti Stav:

   ```bash
   python -m scripts.status nova --autor agent --pre marco --typ otazka \
     --tema "Dotazník: <téma>" --subor docs/handoff/YYYY-MM-DD_<tema>_otazky.md <<'TEXT'
   Prosím vyplň dotazník. Odpovede stačí napísať priamo pod otázky v súbore alebo povedať agentovi.
   TEXT
   ```

5. Povedz používateľovi cestu k súboru. Commit a PR iba cez `eos-git-publish`, ak o to požiada.

## Pravidlá pre otázky

- **Najdôležitejšie otázky prvé.** Odpovede môžu prísť iba raz.
- **Jedna otázka = jedna vec.** Nie „aký materiál a akú hrúbku“.
- **Doménové otázky dávaj možnosti s dôsledkami**, ale nevyberaj za Marca. Napríklad: „A: … (dôsledok), B: … (dôsledok)“.
- **Bez čísel bez zdroja.** Ak treba hodnotu, pýtaj sa na hodnotu **aj na jej zdroj** (norma, katalóg dodávateľa, prax v dielni).
- **„Neviem“ je platná odpoveď.** Napíš to do úvodu.
- Žiadne citlivé údaje zo zákaziek v otázkach (mená zákazníkov, ceny). Súbor ide do gitu.
- Pre Marca po slovensky, jednoducho. Odborný pojem z kódu vysvetli jednou vetou.

## Šablóna

```markdown
# Otázky: <téma>

**Prečo:** <ktoré rozhodnutie od odpovedí závisí, jedna-dve vety>
**Od:** <kto sa pýta> · **Pre:** <adresát> · **Čo sa s odpoveďami stane:** <napr. podľa nich sa navrhne schéma / ADR>
**Dátum:** YYYY-MM-DD

## Súvislosti

Jeden odsek, aby adresát vedel, o čo ide, aj keď nebol pri rozhovore.

## Ako odpovedať

Stačí napísať odpoveď pod otázku (riadok `>`), alebo ju povedať agentovi. „Neviem“ alebo „nie som si istý“ je v poriadku, napíš to radšej, než otázku preskočiť.

## <Téma 1>

### 1. <Otázka>

_Prečo na tom záleží: <iba ak by sa otázka dala pochopiť zle>_

>

### 2. <Otázka>

>

## Ešte niečo?

Je niečo, na čo sme sa nespýtali a mali by sme o tom vedieť?

>
```

## Keď prídu odpovede

- Odpovede zapíš do toho istého súboru pod otázky (alebo ich tam zapíše adresát).
- Z odpovedí urob ďalší krok (návrh schémy, ADR cez `eos-adr`, správu na nástenke). Nerozhoduj nič, čo odpovede nerozhodli.
- Správu na nástenke označ ako vyriešenú: `python -m scripts.status vyries <id>`.
