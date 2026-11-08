# ADR-0020 - Run tests on every pull request

**Status:** Draft  
**Date:** 2026-11-08  

## Context

Do `main` sa dostáva veľa zmien rýchlo za sebou: od 6. do 8. 11. bolo zlúčených osem pull requestov (#6 až #13), každý s vlastnou regresiou spustenou ručne na jednom počítači. Výsledok testov je dnes iba tvrdenie v popise PR a v CDR; GitHub ho neoveruje. Testy bežali na Windows (Python 3.12) aj Linuxe (Python 3.11), no nikdy nie všetky kombinácie pre ten istý commit.

TECH_STACK.md §7 už uvádza GitHub Actions ako navrhovaný nástroj pre vývojára (`unittest` pri každom pushi a PR, Python 3.11 a 3.12). O CI rozhoduje Software Architect (ADR-0018).

## Decision

1. Workflow `.github/workflows/tests.yml` sa spustí pri každom pull requeste a pri pushi do `main`.
2. Kombinácie: Ubuntu s Pythonom 3.11 (minimum podľa `pyproject.toml`), Ubuntu s 3.12 a Windows s 3.12 (prostredie Chief Engineering Knowledge Architecta).
3. Kroky: `pip install -e .`, kontrola dostupnosti `jsonschema`, celá sada `python -m unittest discover -s tests -v` a `python scripts/job_intake.py check` (žiadny súbor reálnej zákazky v gite, ADR-0019).
4. Workflow používa iba oficiálne akcie `actions/checkout` a `actions/setup-python`, oprávnenie iba na čítanie obsahu a žiadne tajomstvá. Neinštaluje nič mimo `pyproject.toml`.
5. Odporúčanie pre správcu repozitára: v nastaveniach vetvy `main` zapnúť povinný úspešný výsledok tohto workflow pred zlúčením.

Etapa projektu sa nemení. Workflow je nástroj vývojára, nie runtime závislosť.

## Alternatives Considered

| Možnosť | Posúdenie |
| --- | --- |
| Ponechať ručné spúšťanie | Bez nákladov, ale výsledok nie je overiteľný a závisí od jedného počítača. |
| Iba jedna kombinácia (Ubuntu, 3.12) | Rýchlejšie; neodhalí rozdiely Windows ani minimálnej verzie Pythonu. |
| Pre-commit hook lokálne | Dá sa obísť a nevidno ho v PR. Môže dopĺňať CI neskôr. |
| `ruff` v tom istom kroku | TECH_STACK.md §7 ho vedie ako samostatný návrh; zmiešanie by zmenilo kritérium úspechu PR bez rozhodnutia. |

## Consequences

- Každý pull request ukáže zelený alebo červený výsledok pre tri prostredia.
- PR s chybou testov alebo s podkladmi zákazky v gite sa dá zastaviť pred zlúčením.
- Beh trvá niekoľko minút; pre súkromný repozitár spotrebúva minúty GitHub Actions v rámci limitu účtu.

## Risks

- Test závislý od prostredia môže na CI zlyhať, hoci lokálne prechádza. Opatrenie: `fail-fast: false`, výsledok každej kombinácie je samostatne viditeľný.
- Bez povinnej kontroly vo vetve `main` sa dá červený PR stále zlúčiť. Opatrenie: bod 5 rozhodnutia.

## Related Documents

- `adr/ADR-0018_Define_target_technology_stack.md`, `TECH_STACK.md` §7
- `adr/ADR-0019_Keep_real_job_intake_outside_git.md`
- `.github/workflows/tests.yml`, `.github/pull_request_template.md`

## Review Date

Pri zmene etapy podľa TECH_STACK.md alebo pri pridaní ďalšieho nástroja do CI.
