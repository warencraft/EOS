# EOS-003 - Identifikácia a verziovanie

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-003  
**Version:** 0.1  
**Revision:** 1  
**Status:** Draft  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-13  
**Document basis:** Internal governance decision  

---

## 1. Účel

Tento dokument definuje stabilné identifikátory, pomenovanie súborov, verziovanie, revízie a životný cyklus záznamov v EOS.

## 2. Typy ID

| Prefix | Význam | Formát |
| --- | --- | --- |
| `EOS` | projektové a governance dokumenty | `EOS-xxx` |
| `MET` | metodiky | `MET-xxx` |
| `STD` | interné technické štandardy a pravidlá EOS | `STD-xxx` |
| `NRM` | externé normy, štandardy a záväzné technické predpisy | `NRM-xxxx` |
| `SRC` | autoritatívne zdrojové referencie | `SRC-xxxxxx` |
| `MAT` | materiálové karty | `MAT-xxxx` |
| `POL` | polotovary a skladové formy | `POL-xxxx` |
| `TEC` | výrobné technológie a procesy | `TEC-xxxx` |
| `MAC` | stroje a výrobné zariadenia | `MAC-xxxx` |
| `TOOL` | rezné nástroje a nástrojové zostavy | `TOOL-xxxx` |
| `SUP` | dodávatelia | `SUP-xxxx` |
| `JOB` | reálne zákazky | `JOB-yyyy-xxxx` |
| `JOB-OP` | operácia zákazky | `JOB-yyyy-xxxx-OP-xxx` |
| `JOB-TM` | časový záznam operácie zákazky | `JOB-yyyy-xxxx-OP-xxx-TM-xxx` |
| `JOB-RSK` | riziko zákazky | `JOB-yyyy-xxxx-RSK-xxx` |
| `JOB-QN` | poznámka do cenovej ponuky | `JOB-yyyy-xxxx-QN-xxx` |
| `CAL` | kalkulátory | `CAL-xxxx` |
| `FRM` | formuláre a šablóny | `FRM-xxxx` |
| `ADR` | architektonické rozhodnutia | `ADR-xxxx` |

## 3. Prideľovanie nových ID

Nové ID sa prideľuje pred vytvorením autoritatívneho záznamu.

ID sa nesmie meniť pri premenovaní súboru.

ID sa nesmie recyklovať po zrušení alebo archivácii záznamu.

Pre `JOB-yyyy-xxxx` znamená `yyyy` rok registrácie zákazky a `xxxx` poradové číslo v danom roku.

Entity vlastnené zákazkou používajú hierarchické ID, aby bolo z ID jasné, ku ktorej zákazke patria. Napríklad `JOB-2026-0001-OP-001` je operácia zákazky `JOB-2026-0001`.

`DocumentRecord` používa ID dokumentu, ktorý eviduje. Samostatný prefix pre `DocumentRecord` sa nezavádza.

## 4. Pomenovanie súborov

Odporúčaný formát:

```text
ID_Descriptive_Name.md
```

Príklady:

```text
EOS-001_System_Architecture.md
ADR-0001_Use_Markdown_for_governed_documentation.md
```

Názov súboru môže pomôcť čitateľnosti, ale autoritatívne ID je pole v dokumente alebo zázname.

## 5. Verzia a revízia

Verzia vyjadruje významnú obsahovú alebo kontraktovú zmenu.

Revízia vyjadruje opravu, doplnenie alebo menšiu úpravu v rámci rovnakej verzie.

Pravidlo:

- zmena významu alebo štruktúry zvyšuje `version`,
- oprava textu alebo spresnenie bez zmeny významu zvyšuje `revision`.

## 6. Životný cyklus dokumentu

Povolené stavy:

- `Draft` - pracovný návrh,
- `Review` - pripravené na kontrolu,
- `Approved` - schválené na používanie,
- `Deprecated` - nahradené alebo neodporúčané,
- `Archived` - historicky uchované bez aktívneho používania.

Prechod do `Approved` vyžaduje kontrolu obsahu a súlad s `EOS-000`.

## 7. Spätná kompatibilita

Stabilné ID nesmie meniť význam bez zaznamenania dôvodu.

Ak sa mení štruktúra dátového záznamu, musí byť jasné:

- čo sa zmenilo,
- ako sa spracujú staršie záznamy,
- či je potrebná migrácia,
- či zmena vyžaduje ADR.

## 8. Nahradenie alebo zrušenie záznamu

Pri nahradení záznamu sa pôvodný záznam neodstraňuje.

Pôvodný záznam sa označí ako `Deprecated` alebo `Archived` a doplní sa odkaz na nový záznam.

Pri zrušení sa uvedie:

- dôvod zrušenia,
- dátum,
- autor rozhodnutia,
- náhrada, ak existuje.

## 9. Súvisiace dokumenty

- `EOS-000_Development_Manifesto.md`
- `EOS-002_Documentation_Standard.md`
- `ADR-0004_Use_stable_object_identifiers_independent_of_filenames.md`

## 10. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-13 | 0.1 | 0 | Chief Engineering Knowledge Architect + Codex | Initial draft |
| 2026-07-13 | 0.1 | 1 | Codex | Governance Alignment 0.1.1: oddelenie `STD-xxx` a `NRM-xxxx`, doplnenie ID pre zdroje, dodávateľov a entity vlastnené zákazkou |
