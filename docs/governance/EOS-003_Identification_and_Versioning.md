# EOS-003 - Identifikácia a verziovanie

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-003  
**Version:** 0.1  
**Revision:** 2  
**Status:** Approved  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-08-01  
**Document basis:** Internal governance decision  

---

## 1. Účel

Tento dokument definuje stabilné identifikátory, pomenovanie súborov, verziovanie, revízie a životný cyklus záznamov v EOS.

## 2. Typy ID

Tabuľka rozlišuje skutočný prefix, hierarchický formát a governance stav.

Stavy:

- `Active` - prefix alebo formát je schválený pre použitie v EOS,
- `Candidate` - prefix je rezervovaný pre budúci kontrakt, ale nesmie sa používať pre autoritatívne uložené záznamy, kým nevznikne príslušný stored contract,
- `Deferred` - prefix je pomenovaný pre budúcu potrebu, ale nie je schválený na použitie v aktuálnej fáze.

| Typ ID | Význam | Formát | Stav |
| --- | --- | --- | --- |
| `EOS` | projektové a governance dokumenty | `EOS-xxx` | Active |
| `RFC` | návrhové dokumenty RFC | `RFC-xxxx` | Active |
| `ADR` | architektonické rozhodnutia | `ADR-xxxx` | Active |
| `MET` | metodiky | `MET-xxx` | Active |
| `STD` | interné technické štandardy a pravidlá EOS | `STD-xxx` | Active |
| `NRM` | externé normy, štandardy a záväzné technické predpisy | `NRM-xxxx` | Active |
| `SRC` | autoritatívne zdrojové referencie | `SRC-xxxxxx` | Active |
| `MAT` | materiálové karty | `MAT-xxxx` | Active |
| `POL` | polotovary a skladové formy | `POL-xxxx` | Active |
| `TEC` | výrobné technológie a procesy | `TEC-xxxx` | Active |
| `MAC` | stroje a výrobné zariadenia | `MAC-xxxx` | Active |
| `TOOL` | rezné nástroje a nástrojové zostavy | `TOOL-xxxx` | Active |
| `SUP` | dodávatelia | `SUP-xxxx` | Active |
| `JOB` | reálne zákazky | `JOB-yyyy-xxxx` | Active |
| `JOB Operation` | operácia zákazky vlastnená zákazkou | `JOB-yyyy-xxxx-OP-xxx` | Active |
| `JOB TimeRecord` | časový záznam operácie zákazky | `JOB-yyyy-xxxx-OP-xxx-TM-xxx` | Active |
| `JOB Risk` | riziko zákazky | `JOB-yyyy-xxxx-RSK-xxx` | Active |
| `JOB QuotationNote` | poznámka do cenovej ponuky | `JOB-yyyy-xxxx-QN-xxx` | Active |
| `OBS` | first-class observation ako evidence entity | `OBS-xxxxxx` | Active |
| `PRP` | property catalog entry alebo stabilný property identifier | `PRP-xxxxxx` | Active |
| `UNT` | unit catalog entry alebo stabilný unit identifier | `UNT-xxxxxx` | Active |
| `CLS` | classification catalog entry | `CLS-xxxxxx` | Active |
| `CND` | condition type catalog entry | `CND-xxxxxx` | Active |
| `DEC` | decision, ak vznikne samostatný stored Decision contract | `DEC-xxxxxx` | Candidate |
| `REL` | budúci first-class relationship object | `REL-xxxxxx` | Deferred |
| `EVT` | budúci všeobecný event object | `EVT-xxxxxx` | Deferred |
| `CAL` | kalkulátory | `CAL-xxxx` | Active |
| `FRM` | formuláre a šablóny | `FRM-xxxx` | Active |

### 2.1 Príklady ID

Príklady používajú iba fiktívne identifikátory:

- `EOS-003`,
- `RFC-0001`,
- `ADR-0016`,
- `SRC-000001`,
- `NRM-0001`,
- `OBS-000001`,
- `PRP-000001`,
- `UNT-000001`,
- `CLS-000001`,
- `CND-000001`,
- `JOB-2026-0001`,
- `JOB-2026-0001-OP-001`,
- `JOB-2026-0001-OP-001-TM-001`,
- `JOB-2026-0001-RSK-001`,
- `JOB-2026-0001-QN-001`.

`DEC-000001`, `REL-000001` a `EVT-000001` sú iba formátové príklady. Nesmú sa použiť ako autoritatívne uložené záznamy, kým ich stav nebude zmenený z `Candidate` alebo `Deferred` na `Active`.

## 3. Prideľovanie nových ID

Nové ID sa prideľuje pred vytvorením autoritatívneho záznamu.

ID sa nesmie meniť pri premenovaní súboru.

ID sa nesmie recyklovať po zrušení alebo archivácii záznamu.

Pre `JOB-yyyy-xxxx` znamená `yyyy` rok registrácie zákazky a `xxxx` poradové číslo v danom roku.

Entity vlastnené zákazkou používajú hierarchické ID, aby bolo z ID jasné, ku ktorej zákazke patria. Napríklad `JOB-2026-0001-OP-001` je operácia zákazky `JOB-2026-0001`.

`DocumentRecord` používa ID dokumentu, ktorý eviduje. Samostatný prefix pre `DocumentRecord` sa nezavádza.

### 3.1 Governance pravidlá prefixov

Každý nový prefix alebo nový hierarchický formát musí byť doplnený do tohto dokumentu pred tým, ako sa použije v JSON schéme, RFC, ADR alebo autoritatívnom dátovom zázname.

Jeden prefix nesmie mať dva významy.

Jeden význam nesmie mať dva aktívne prefixy, pokiaľ nie je explicitne uvedený migračný dôvod.

Skutočný prefix je počiatočný stabilný segment ID pred prvým číselným rozsahom alebo pred hierarchickým pokračovaním. Označenia ako `JOB Operation` alebo `JOB TimeRecord` sú typy hierarchických ID, nie samostatné prefixy.

Prefix `STD-xxx` je vyhradený pre interné technické štandardy alebo pravidlá EOS.

Prefix `NRM-xxxx` je vyhradený pre externé normy, štandardy alebo záväzné technické predpisy.

Prefix `DEC-xxxxxx` zostáva `Candidate`, kým nevznikne samostatný stored `Decision` contract. Dovtedy je `Decision` architektonická decision boundary podľa ADR-0015 a ADR-0016, nie povinný uložený záznam.

Prefixy `REL-xxxxxx` a `EVT-xxxxxx` sú `Deferred`. Nesmú sa použiť v schémach `0.2B.1` bez nového ADR, RFC alebo aktualizácie tohto dokumentu.

Prefixy `PRP-xxxxxx`, `UNT-xxxxxx`, `CLS-xxxxxx` a `CND-xxxxxx` sú schválené pre identifikáciu katalógových položiek alebo stabilných katalógových významov. Samotné katalógové kontrakty vzniknú až v príslušnej implementačnej fáze.

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
| 2026-08-01 | 0.1 | 2 | Codex | Phase 0.2B.0: doplnenie RFC, Observation, property, unit, classification, condition, decision, relationship a event prefix governance; označenie `DEC` ako Candidate a `REL`/`EVT` ako Deferred; zjednotenie hierarchických JOB ID |
