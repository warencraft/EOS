# scripts

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
