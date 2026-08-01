# tests

## Míľnik 0.2B.1.3 - MeasurementQuality Contract

Testy pre `MeasurementQuality` používajú iba `unittest` a existujúcu validačnú vrstvu.

Platné a neplatné fixture sú v:

- `tests/fixtures/valid/knowledge-core/`
- `tests/fixtures/invalid/knowledge-core/`

Pokrytie zahŕňa:

- `uncertainty`, nulovú `uncertainty`, `resolution` a `confidenceLevel`,
- hranice `confidenceLevel` 0 a 1,
- kombinácie štruktúrovaných polí a voliteľné `notes`,
- empty object a notes-only objekt ako neplatné,
- zápornú neistotu cez aplikačnú validáciu,
- nulové a záporné rozlíšenie cez aplikačnú validáciu,
- neplatné vnorené `Quantity`,
- presné cesty k vnoreným chybám,
- zákaz metadát, lifecycle polí, `sourceLinks`, `verificationStatus`,
- zákaz tolerančných polí a odložených polí `accuracy`, `repeatability`, `reproducibility`,
- rozlíšenie `schema_validation` a `application_validation`,
- dostupnosť `MeasurementQuality` cez centrálny schema index.

## Míľnik 0.2B.1.2 - ValueRange Contract

Testy pre `ValueRange` používajú iba `unittest` a existujúcu validačnú vrstvu.

Platné a neplatné fixture sú v rovnakých Knowledge Core priečinkoch ako `Quantity`:

- `tests/fixtures/valid/knowledge-core/`
- `tests/fixtures/invalid/knowledge-core/`

Pokrytie zahŕňa:

- uzavretý, otvorený a polootvorený rozsah,
- jednostranne ohraničené rozsahy,
- rovnaké hranice,
- zápornú až kladnú fiktívnu hodnotu,
- voliteľné `notes`,
- chýbajúci `unitId`,
- chýbajúce obe hranice,
- obrátené hranice cez aplikačnú validáciu,
- inkluzivitu bez príslušnej hranice,
- nesprávne typy hraníc,
- neplatný `UNT` identifikátor,
- `additionalProperties: false`,
- zákaz entity metadát, `sourceLinks`, `tolerance` a `uncertainty`,
- rozlíšenie `schema_validation` a `application_validation`,
- dostupnosť `ValueRange` cez centrálny schema index.

## Míľnik 0.2B.1.1 - Quantity Contract

Testy pre `Quantity` používajú iba `unittest` a existujúcu validačnú vrstvu.

Platné fixture sú v:

- `tests/fixtures/valid/knowledge-core/`

Neplatné fixture sú v:

- `tests/fixtures/invalid/knowledge-core/`

Pokrytie zahŕňa:

- platné celé číslo,
- platné desatinné číslo,
- platnú zápornú hodnotu,
- platnú nulu,
- platné voliteľné `notes`,
- chýbajúce povinné polia,
- nesprávny typ `value`,
- neplatný prefix `unitId`,
- malé písmená v prefixe `unitId`,
- neúplné nulové doplnenie `unitId`,
- `additionalProperties: false`,
- zákaz metadát entity vo value objecte,
- viac chýb v jednom zázname,
- presné cesty k chybným poliam,
- dostupnosť `Quantity` cez centrálny schema index.

Tento priečinok je určený pre budúce testy schém, dátových kontraktov a kalkulačných modulov.

Vo fáze 0.2A obsahuje testy základných dátových kontraktov.

Používa sa `unittest` zo štandardnej knižnice Pythonu. Projekt zatiaľ neprechádza na `pytest`.

Fixtures sú fiktívne a netechnické. Nesmú obsahovať reálne materiálové hodnoty, normové tabuľky, výrobné časy, ceny ani rezné podmienky.

Phase 0.2A.1 dopĺňa auditné testy pre:

- lokálne `$ref`,
- povinné polia,
- enumy,
- regex patterny,
- `additionalProperties: false`,
- neplatné dátumy a verzie,
- vnorený `SourceLink`,
- nepodporované JSON Schema kľúčové slová,
- viac chýb v jednom zázname,
- presné cesty k chybným poliam.

## Lokálne spustenie testov

V koreňovom priečinku projektu:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m unittest discover -s tests -p "test_*.py" -v
```

Ak `jsonschema` nie je nainštalované, integračné testy validácie sú blokované. Takýto stav sa nesmie považovať za úspešný testovací beh.
