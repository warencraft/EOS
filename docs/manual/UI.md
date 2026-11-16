# EOS UI v0 – návod

Lokálna aplikácia v prehliadači (ADR-0021). Ukazuje zákazky z `intake/`, importuje excelovú kalkuláciu, upozorní na chyby v šablóne a prepočíta cenu pri zmene času alebo sadzby. Beží iba na tvojom počítači a nič neposiela von.

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
| **Zákazky** | Všetky zákazky z `intake/`, počet podkladov, cena z kalkulácie a z ponuky, počet upozornení. Červený štítok „nesedí s ponukou“, keď výpočet z riadkov nedáva cenu ponuky. |
| **Detail zákazky** | Podklady z manifestu, import kalkulácie z excelovej šablóny, súhrn ceny (EOS oproti Excelu), sadzba a scenáre, upozornenia, operácie s časmi, materiál, nákup a história ručných zmien. |
| **Model** | Čo model EOS ešte nevie (z vertical slice) a prehľad všetkých schém. |

### Import kalkulácie

V detaile zákazky vyber súbor šablóny (`.xls` alebo `.xlsx` zo zákazky) a klikni na **Importovať kalkuláciu**. Importér:

- načíta diely, polotovary, časy operácií, sadu tesnení, nakupované diely a dokumentáciu,
- porovná výpočet s ponukou v hárku KALKULAČNÍ,
- upozorní na chyby šablóny: iná sadzba v riadku, nesúlad množstiev, nezapočítané položky, zvyšky starých kalkulácií, chýbajúci zákazník, rozdiel oproti ponuke.

Kalkulácia sa uloží do `intake/_eos/kalkulacie/<zákazka>.json` (mimo gitu).

### Úpravy

- **Čas na kus:** prepíš hodnotu v tabuľke operácií a opusti pole. Cena sa hneď prepočíta a uloží.
- **Sadzba práce:** zmeň ju v paneli „Sadzba a scenáre“.
- **Riadok s inou sadzbou:** pri ňom je červený štítok so sadzbou a odkaz „zjednotiť“.
- **Nákup:** tlačidlom v stĺpci „V cene“ položku pridáš do ceny alebo ju z ceny vyradíš.

Každá zmena sa zapíše do histórie (čas, pole, pôvodná a nová hodnota). **Opätovný import zo šablóny ručné zmeny prepíše.**

## Čo zatiaľ nevie

- Novú zákazku ani kalkuláciu bez Excelu (zákazku založ cez `scripts/job_intake.py`).
- Ponuku v PDF ani v Exceli.
- Prácu viacerých ľudí naraz alebo cez sieť.
- Záznamy EOS (materiály, procesy, diely) v databáze. To príde s entitou Job a etapou B.
