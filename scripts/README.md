# scripts

## Míľnik 0.2B.1.3 - MeasurementQuality Contract

Pre `MeasurementQuality` zostáva validácia rozdelená na dve vrstvy:

- JSON Schema kontroluje objekt, známe polia, notes-only pravidlo, vnorené `Quantity` cez `$ref`, `confidenceLevel` v rozsahu 0 až 1 a zákaz neznámych polí.
- EOS aplikačná validácia kontroluje významové pravidlá `uncertainty.value >= 0` a `resolution.value > 0`.

Validačná vrstva nevykonáva prevody jednotiek, nekontroluje existenciu Unit Catalog položky, nemodeluje tolerancie a nevytvára MeasurementMethod ani Instrument kontrakt.

## Míľnik 0.2B.1.2 - ValueRange Contract

Pre `ValueRange` zostáva validácia rozdelená na dve vrstvy:

- JSON Schema kontroluje štruktúru, typy, `unitId`, aspoň jednu hranicu, väzbu inkluzivity na hranicu a neznáme polia.
- EOS aplikačná validácia kontroluje významové pravidlá `minValue <= maxValue`, `lowerInclusive` bez `minValue` a `upperInclusive` bez `maxValue`.

Validačná vrstva nevykonáva prevody jednotiek, nekontroluje existenciu Unit Catalog položky a nezavádza konkrétne jednotky ani technické hodnoty.

## Míľnik 0.2B.1.1 - Quantity Contract

Validačná vrstva ostáva rozdelená na štandardnú JSON Schema validáciu cez `jsonschema` a EOS aplikačné pravidlá.

Pre `Quantity` sa štrukturálne kontrolujú povinné polia, typ `number`, centrálny `UNT-xxxxxx` identifikátor a `additionalProperties: false`.

Aplikačná vrstva genericky odmieta nekonečné a nečíselné numerické hodnoty ako `NaN` a `Infinity`, aby value objecty používali iba konečné numerické hodnoty.

Tento priečinok je určený pre budúce pomocné skripty.

Skripty musia byť účelové, testovateľné a nesmú obsahovať hardcoded strojárske hodnoty.

## validation

`scripts/validation/` obsahuje minimálnu validačnú vrstvu pre fázu 0.2A.

Aktuálne používa iba štandardnú knižnicu Pythonu, pretože v dostupnom runtime nie sú prítomné balíky `jsonschema` ani `pytest` a projekt zatiaľ nepridáva nové závislosti.

Validácia rozlišuje:

- syntaktickú kontrolu JSON záznamov proti podporovanej podmnožine JSON Schema,
- aplikačné pravidlá EOS, napríklad významové pravidlo pre `sourceLinks`.

Od fázy 0.2A.2 používa štrukturálna validácia knižnicu `jsonschema` a `Draft202012Validator`.

Interná EOS vrstva zostáva zodpovedná za aplikačné pravidlá, napríklad `sourceLinks`, hierarchické ID a rozlíšenie `schemaVersion` vs `documentVersion`.

Ak závislosť `jsonschema` chýba, validačný nástroj zobrazí jasnú inštalačnú správu a integračná validácia je blokovaná.

## Lokálne spustenie

V koreňovom priečinku projektu:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m unittest discover -s tests -p "test_*.py" -v
```

Ak príkaz `py` nie je dostupný, použi cestu k dostupnému Pythonu 3.11 alebo novšiemu.
