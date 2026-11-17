# EOS UI v0 – návod

Lokálna aplikácia v prehliadači (ADR-0021, ADR-0022). Založíš v nej zákazku, nahráš a pozrieš si podklady, vytvoríš kalkuláciu (z Excelu, podľa podobnej zákazky alebo ručne) a hneď vidíš cenu. Na stránke **Stav** si s Robinom a agentom vymieňate spätnú väzbu. Beží iba na tvojom počítači a nič neposiela von.

## Spustenie

Raz nainštaluj voliteľné závislosti (z priečinka EOS):

```bash
python3 -m venv .venv                       # ak ešte nemáš
.venv/bin/python -m pip install -e ".[ui,import]"
```

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[ui,import]"
```

Spusti aplikáciu:

```bash
.venv/bin/python -m scripts.web             # Windows: .\.venv\Scripts\python -m scripts.web
```

Otvor **http://127.0.0.1:8000**. Ukončíš ju klávesmi Ctrl+C v termináli.

## Čo vie

| Stránka | Čo tam nájdeš |
| --- | --- |
| **Zákazky** | Všetky zákazky z `intake/`, počet podkladov, cena z kalkulácie a z ponuky, počet upozornení. Červený štítok „nesedí s ponukou“, keď výpočet z riadkov nedáva cenu ponuky. Tlačidlo **+ Nová zákazka**. |
| **Detail zákazky** | Podklady s náhľadom PDF a obrázkov, nahratie ďalších podkladov, vytvorenie kalkulácie, súhrn ceny (EOS oproti Excelu), sadzba, množstvo a scenáre, upozornenia, operácie, materiál, nákup a história ručných zmien. |
| **Stav** | Správy pre Marca a pre Robina: výsledky kontroly agenta pred commitom, otázky, feedback, rozhodnutia. Odpoveď a „vyriešené“. |
| **Model** | Čo model EOS ešte nevie (z vertical slice) a prehľad všetkých schém. |

### Nová zákazka

1. Na stránke Zákazky klikni na **+ Nová zákazka**.
2. Vyplň názov (napr. „Hydraulický valec 4 ks – V950“), vyber, kto ju zakladá, a pridaj podklady (výkresy PDF, dopyt). Vyber, kam patria (Výkresy, Dopyt…).
3. Klikni na **Založiť zákazku**. Dostane ďalšie voľné číslo `JOB-<rok>-<nnnn>` a podklady sa uložia do `intake/<číslo>/`. Do gitu nič nejde.

Ďalšie podklady pridáš v detaile zákazky (Pridať podklady). Excelovú kalkuláciu daj do „Ponuka / kalkulácia“.

### Náhľad podkladov

V detaile zákazky klikni na podklad vľavo. PDF a obrázky sa zobrazia vpravo v paneli **Náhľad**. Iné súbory (Excel, 3D model) otvor v ich programe.

### Kalkulácia bez Excelu

V paneli **Vytvoriť kalkuláciu**:

- **Podľa podobnej zákazky:** vyber vzor (zákazku, ktorá už kalkuláciu má), zadaj množstvo a klikni na **Vytvoriť**. Prevezmú sa diely, operácie s časmi na kus, materiál a nákup. Kusy operácií, kg materiálu a kusy nákupu sa prepočítajú pomerom množstiev. Je to iba štart: kalkulácia dostane upozornenie a všetko treba overiť podľa výkresov tejto zákazky.
- **Prázdna:** nechaj „– prázdna kalkulácia –“, zadaj množstvo a sadzbu €/h.

Potom pod každou tabuľkou pridáš riadok (operácia, materiál, nákup), čísla prepíšeš priamo v tabuľke a krížikom × riadok odstrániš.

### Import kalkulácie

V detaile zákazky vyber súbor šablóny (`.xls` alebo `.xlsx` zo zákazky) a klikni na **Importovať kalkuláciu**. Importér:

- načíta diely, polotovary, časy operácií, sadu tesnení, nakupované diely a dokumentáciu,
- porovná výpočet s ponukou v hárku KALKULAČNÍ,
- upozorní na chyby šablóny: iná sadzba v riadku, nesúlad množstiev, nezapočítané položky, zvyšky starých kalkulácií, chýbajúci zákazník, rozdiel oproti ponuke.

Kalkulácia sa uloží do `intake/_eos/kalkulacie/<zákazka>.json` (mimo gitu).

### Úpravy

- **Čas na kus, kusy, kg, €/kg, €/ks:** prepíš hodnotu v tabuľke a opusti pole. Cena sa hneď prepočíta a uloží.
- **Množstvo:** zmeň ho v paneli „Sadzba a scenáre“. Mení cenu za kus; kusy v operáciách uprav v tabuľke.
- **Sadzba práce:** zmeň ju v paneli „Sadzba a scenáre“.
- **Riadok s inou sadzbou:** pri ňom je červený štítok so sadzbou a odkaz „zjednotiť“.
- **Nákup:** tlačidlom v stĺpci „V cene“ položku pridáš do ceny alebo ju z ceny vyradíš.

Každá zmena sa zapíše do histórie (čas, pole, pôvodná a nová hodnota). **Opätovný import zo šablóny ručné zmeny prepíše.**

### Stav a feedback

Stránka **Stav** má dva stĺpce: **Pre Marca** (doména: entity, hodnoty, zdroje, rozsah fázy) a **Pre Robina** (technika: kód, testy, závislosti). Číslo pri odkaze Stav v hornej lište ukazuje otvorené správy.

- Agent tam pred každým commitom zapíše, čo našiel (skill `eos-pre-commit-review`).
- Novú správu napíšeš dole vo formulári. Pri správe môžeš odpovedať alebo ju označiť ako vyriešenú.
- Správy sa ukladajú do `status/spravy/` a idú s commitom do gitu. Druhý ich uvidí, keď si stiahne zmeny. **Nepíš do nich mená zákazníkov ani ceny**; aplikácia správu s názvom zákazky alebo zákazníka odmietne.

## Čo zatiaľ nevie

- Vypočítať časy operácií z výkresu. Kalkulácia podľa podobnej zákazky je odhad, ktorý treba overiť.
- Ponuku v PDF ani v Exceli.
- Prácu viacerých ľudí naraz alebo cez sieť.
- Záznamy EOS (materiály, procesy, diely) v databáze. To príde s entitou Job a etapou B.
