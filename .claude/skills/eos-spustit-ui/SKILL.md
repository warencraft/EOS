---
name: eos-spustit-ui
description: Stiahne najnovšiu verziu EOS, pripraví prostredie (Python 3.11+, knižnice UI) a spustí lokálnu aplikáciu v prehliadači. Použi, keď používateľ povie „spusti EOS“, „otvor UI“, „aktualizuj aplikáciu“, „chcem vidieť novú verziu“, „stiahni zmeny“, alebo keď UI nejde (stránka sa nenačíta, chýba modul).
---

# Spustenie a aktualizácia EOS UI

Používateľ (Marco) terminál nepoužíva. Všetky príkazy spustíš ty a výsledok mu povieš jednou-dvoma vetami po slovensky. Kde ťa prostredie (sandbox) požiada o povolenie, napr. na sieť pri `git fetch` a `pip install` alebo na beh na pozadí, vysvetli jednou vetou prečo a požiadaj oň.

Návod pre ľudí: `docs/manual/UI.md`. Aplikácia beží iba na tomto počítači (`127.0.0.1`), ADR-0021 a ADR-0022.

## Pravidlá

- Nikdy nemaž ani neprepisuj `intake/` (reálne zákazky) a `status/spravy/`.
- Ak sú v gite necommitnuté zmeny, **nič nesťahuj ani neprepínaj**. Povedz, čo je zmenené, a ponúkni skill `eos-git-publish`.
- Nepoužívaj `git reset --hard`, `git clean`, `git stash` ani `--force`.
- `.venv/` zmaž a vytvor znova iba so súhlasom používateľa (pozri krok 3).

## 1. Najnovšia verzia

```bash
git status --short
git branch --show-current
git fetch origin
```

- Ak používateľ chce vidieť konkrétny pull request alebo vetvu (napr. `feature/ui-zakazka-a-stav`) a ešte nie je zlúčená: `git switch <vetva>` (git ju sám prepojí s `origin/<vetva>`), potom `git pull --ff-only`.
- Inak: `git switch main` a `git pull --ff-only origin main`.
- Ak `pull --ff-only` zlyhá, zastav sa a vysvetli to. Nič neopravuj silou.

Povedz používateľovi, na akej verzii je: `git log --oneline -1`.

## 2. Python 3.11 alebo novší

Skús v tomto poradí a vezmi prvý, ktorý vypíše verziu ≥ 3.11:

- macOS / Linux: `python3.13 --version`, `python3.12 --version`, `python3.11 --version`, `python3 --version`
- Windows: `py -3.13 --version`, `py -3.12 --version`, `py -3.11 --version`, `python --version`

Ak žiadny nie je:

- macOS s Homebrew (`brew --version` funguje): so súhlasom používateľa `brew install python@3.12`.
- Inak sa zastav a povedz: „Potrebuješ Python 3.12. Stiahni ho z https://www.python.org/downloads/ a nainštaluj (na Windows zaškrtni *Add python.exe to PATH*). Potom mi napíš a pokračujem.“

Python 3.9 z Xcode (macOS) **nestačí**.

## 3. Prostredie `.venv`

Ak `.venv` existuje, over verziu: `.venv/bin/python --version` (Windows: `.venv\Scripts\python --version`).

- Verzia ≥ 3.11 → použi ho.
- Staršia alebo `.venv` nefunguje → povedz to a so súhlasom ho vytvor znova:
  - macOS / Linux: `rm -rf .venv && <python z kroku 2> -m venv .venv`
  - Windows (PowerShell): `Remove-Item -Recurse -Force .venv; py -3.12 -m venv .venv`
- `.venv` neexistuje → vytvor ho (`<python> -m venv .venv`).

Potom (aj pri existujúcom `.venv`, lebo nová verzia môže mať nové knižnice):

```bash
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[ui,import]"
```

Windows: `.venv\Scripts\python` namiesto `.venv/bin/python`.

## 4. Stará bežiaca verzia

Zisti, či port 8000 nepoužíva stará verzia EOS:

- macOS / Linux: `lsof -nP -iTCP:8000 -sTCP:LISTEN`
- Windows: `netstat -ano | findstr :8000`

Ak tam beží `python … scripts.web`, je to stará verzia EOS: ukonči ju (`kill <PID>`, Windows `taskkill /PID <PID>`) a povedz to. Ak tam beží niečo iné, nič neukončuj a použi port 8010 (`--port 8010`).

## 5. Spustenie na pozadí

macOS / Linux:

```bash
nohup .venv/bin/python -m scripts.web --port 8000 > .venv/eos-ui.log 2>&1 &
```

Windows (PowerShell):

```powershell
Start-Process -WindowStyle Hidden -FilePath .venv\Scripts\python -ArgumentList "-m","scripts.web","--port","8000" -RedirectStandardOutput .venv\eos-ui.log -RedirectStandardError .venv\eos-ui.err
```

Počkaj, kým odpovie (najviac ~15 s):

```bash
for i in $(seq 1 15); do curl -fsS -o /dev/null http://127.0.0.1:8000/ && break; sleep 1; done
```

Ak neodpovie, prečítaj `.venv/eos-ui.log`, vysvetli chybu a navrhni opravu (najčastejšie chýbajúca knižnica → krok 3).

Otvor prehliadač: macOS `open http://127.0.0.1:8000`, Windows `start http://127.0.0.1:8000`, Linux `xdg-open http://127.0.0.1:8000`.

Ak tvoje prostredie procesy na pozadí po skončení odpovede ukončuje, povedz používateľovi, že aplikácia beží iba počas tejto relácie, prípadne mu daj jeden príkaz na skopírovanie: `.venv/bin/python -m scripts.web`.

## 6. Záver pre používateľa

Napríklad:

> EOS beží na http://127.0.0.1:8000 (verzia `6fceb59`, vetva `feature/ui-zakazka-a-stav`). Otvoril som ti ho v prehliadači.
> Novinky nájdeš v hornej lište pod **Stav**, máš tam 2 správy.

Ak sú na nástenke otvorené správy pre používateľa (`python -m scripts.status zoznam --pre marco`), spomeň ich počet.

## Zastavenie

„Zastav EOS“: nájdi proces podľa kroku 4 a ukonči ho.
