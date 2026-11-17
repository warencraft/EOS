# ADR-0022 - Zadanie zákazky v UI a stavová nástenka

**Status:** Proposed  
**Date:** 2026-11-17  
**Decided by:** Software Architect (IT strana projektu); schvaľuje Chief Engineering Knowledge Architect zlúčením PR  

## Context

UI v0 (ADR-0021) vie iba zobraziť zákazky a importovať excelovú kalkuláciu. Strojár (Marco) nemohol:

- založiť zákazku bez príkazového riadku (`scripts/job_intake.py new`),
- nahrať a pozrieť si podklady (výkresy v PDF),
- vytvoriť kalkuláciu, keď zákazka nemá excelovú šablónu.

Zároveň chýba spoločné miesto, kde si strojár, IT strana a agent vymieňajú spätnú väzbu. Pripomienky sa strácajú v chate a agent pred commitom nikomu nehlási, čo našiel.

## Decision

1. **Zákazka v UI.** Stránka „Nová zákazka“ pridelí ďalšie voľné číslo `JOB-<rok>-<nnnn>`, založí priečinok cez `job_intake.cmd_new` a uloží nahraté podklady do zvoleného podpriečinka. Manifest doplní `job_intake.cmd_scan`. Pravidlá ADR-0019 platia bez zmeny: všetko ostáva v `intake/`, mimo gitu, `aiProcessingAllowed` je predvolene `false`.
2. **Náhľad podkladov.** UI zobrazí PDF a obrázky zo zákazky v rámci stránky. Číta iba súbory uvedené v manifeste, iba známe typy (PDF, PNG, JPG, GIF, WEBP, SVG, TXT); SVG v sandboxe.
3. **Kalkulácia bez Excelu.** Kalkuláciu možno vytvoriť prázdnu alebo **podľa podobnej zákazky**. Kópia prevezme diely, operácie s časmi na kus, materiál a nákup; kusy operácií, kg materiálu a kusy nákupu prepočíta pomerom množstiev. Tento pomer **nie je technologické pravidlo**: kópia nesie upozornenie, že všetko treba overiť podľa výkresov. Riadky sa dajú pridať, upraviť a odobrať; každá zmena ide do histórie. Formát kalkulácie (ADR-0021) sa nemení.
4. **Stavová nástenka.** Správy sú v repozitári v `status/spravy/`, **jeden JSON súbor na správu** (súbežné správy nespôsobia konflikt pri zlučovaní). Formát `scripts/status/sprava.schema.json` je nástrojový, nie kontrakt EOS. Správa má autora (`marco`, `robino`, `agent`), adresáta (`marco`, `robino`, `oba`), typ, stav, prípadne závažnosť a odpoveď na inú správu. UI má stránku **Stav** s dvoma stĺpcami (Pre Marca, Pre Robina), odpoveďou a označením „vyriešené“. Príkazový riadok `python -m scripts.status`.
5. **Ochrana údajov zákaziek.** Nástenka je v gite, preto správu s názvom zákazky alebo zákazníka z lokálneho `intake/` odmietne UI aj príkazový riadok; `python -m scripts.status kontrola` to overí pre všetky správy.
6. **Kontrola pred commitom.** Nový skill `eos-pre-commit-review`: testy, kontrola EOS, prezretie zmien; nálezy rozdelí na doménové (Marco) a technické (Robino) a zapíše ich na nástenku do toho istého commitu. `eos-git-publish` ho spúšťa vždy pred commitom. Platí pre Clauda aj Codex (`.agents/skills/`).

7. **Zmeny iba z vlastných stránok.** Keďže UI už zapisuje súbory, odmieta POST z cudzej stránky (hlavička `Origin` mimo localhost alebo `Sec-Fetch-Site: cross-site`).

Bez novej závislosti: nahrávanie súborov používa `python-multipart`, ktorý už je v `.[ui]`.

## Alternatives Considered

| Možnosť | Posúdenie |
| --- | --- |
| GitHub Issues alebo komentáre v PR | Mimo UI, Marco by ich musel sledovať zvlášť; agent v Codexe ich bez prístupu ku GitHubu nezapíše. |
| Jeden súbor `STATUS.md` | Jednoduchý, ale dvaja ľudia naraz = konflikt pri zlučovaní. |
| Databáza (SQLite) | Etapa B; nástenka by nebola v gite a nepreniesla by sa medzi počítačmi. |
| Kalkulácia z výkresu automaticky (časy z geometrie) | Doménový model normovania neexistuje; rozhoduje Chief Engineering Knowledge Architect. Kópia z podobnej zákazky je priznaný odhad, nie výpočet. |

## Consequences

- Marco založí zákazku, nahrá výkresy, pozrie si ich a pripraví kalkuláciu bez príkazového riadku a bez Excelu.
- Každý commit cez agenta nesie správy z kontroly; obaja ich vidia v UI po stiahnutí zmien.
- Do gitu pribúda priečinok `status/spravy/`. Staré vyriešené správy sa dajú neskôr archivovať; zatiaľ sa nemažú.

## Risks

- **Kópia kalkulácie sa bude brať ako hotová cena.** Opatrenie: upozornenie v kalkulácii, UI to uvádza pri vytvorení.
- **Citlivý údaj v správe, ktorý nie je v intake/** (napr. meno, ktoré nie je v názve zákazky). Kontrola ho nezachytí; pravidlo je v skille a v UI.
- **Nástenka sa stane úložiskom rozhodnutí.** Rozhodnutia patria do ADR alebo CDR; správa na ne iba odkazuje.

## Related Documents

- `adr/ADR-0019_Keep_real_job_intake_outside_git.md`, `adr/ADR-0021_Local_UI_v0_and_working_calculation.md`
- `status/README.md`, `docs/manual/UI.md`
- `.agents/skills/eos-pre-commit-review/SKILL.md`, `.agents/skills/eos-git-publish/SKILL.md`
- `scripts/status/`, `scripts/web/`, `tests/test_status.py`, `tests/test_web_ui.py`, `tests/test_kalkulacia.py`

## Review Date

Po mesiaci používania nástenky alebo 2027-01-31, podľa toho, čo nastane skôr.
