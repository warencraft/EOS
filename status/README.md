# Stavová nástenka

Správy medzi Marcom (doména), Robinom (technika) a agentom (ADR-0022). V UI ich vidíš na stránke **Stav** (`python -m scripts.web`, potom http://127.0.0.1:8000/stav).

- `spravy/` – jedna správa = jeden JSON súbor. Nepíš ich ručne; použi UI alebo `python -m scripts.status`.
- Agent sem pred každým commitom zapíše výsledok kontroly (skill `eos-pre-commit-review`) a rozdelí ho: doménové veci pre Marca, technické pre Robina.
- Správy idú do gitu. **Žiadne mená zákazníkov, názvy zákaziek ani ceny.** Odkazuj číslom zákazky (`JOB-…`).

```bash
python -m scripts.status zoznam                 # otvorené správy pre oboch
python -m scripts.status zoznam --pre marco
python -m scripts.status nova --autor robino --pre marco --typ otazka --tema "…" --text "…"
python -m scripts.status vyries <id> --kto marco
python -m scripts.status kontrola               # formát a citlivé údaje
```
