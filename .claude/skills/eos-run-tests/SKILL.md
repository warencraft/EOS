---
name: eos-run-tests
description: Spustí a vyhodnotí testy EOS (unittest + jsonschema). Použi po každej zmene schémy, fixtúry alebo validačného kódu a pred hlásením „hotovo“.
---

# Spustenie testov EOS

## 1. Prostredie

Over, že existuje `.venv` a je v ňom `jsonschema`:

```bash
.venv/bin/python -c "import jsonschema; print(jsonschema.__version__)"
```

Ak `.venv` chýba: `python3 -m venv .venv && .venv/bin/python -m pip install -e .`
(Windows: `py -m venv .venv` a `.\.venv\Scripts\python ...`)

Ak sa `jsonschema` nedá nainštalovať, **zastav sa**. Testy sú blokované a výsledok nehlás ako úspešný (AGENTS.md bod 13).

## 2. Celá sada

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Vždy spúšťaj celú sadu, nie iba testy, ktoré si menil.

## 3. Vyhodnotenie

- Porovnaj počet testov s posledným známym stavom: `python scripts/project_status.py` (ak skript existuje), inak posledný záznam v `CHANGELOG.md`.
- Počet má zostať rovnaký, alebo narásť iba o testy, ktoré si pridal. Ak klesol, niečo sa prestalo spúšťať. Zisti prečo.
- `skipped` > 0 nie je úspech, ak nejde o zámerný a zdokumentovaný skip.
- Pri zlyhaní oprav príčinu. Neoslabuj test ani schému len preto, aby prešli.

## 4. Hlásenie

Uveď presne: počet testov, failures, errors, skipped, verziu Pythonu a `jsonschema`. Ak sa počty zmenili, zapíš ich do `CHANGELOG.md`.
