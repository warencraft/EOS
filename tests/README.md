# tests

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
