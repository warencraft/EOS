# EOS-009 - Architecture Closure Plan

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-009  
**Version:** 0.1  
**Revision:** 0  
**Status:** Draft  
**Author:** Codex  
**Last updated:** 2026-07-25  
**Document basis:** Internal governance proposal  

## 1. Purpose

Tento dokument navrhuje plán formálneho uzatvorenia architektonickej prípravy pred `Phase 0.2B.1 Knowledge Core Contracts`.

Cieľom je previesť findings z `RFC-0001-0003_Cross_Consistency_Review.md` do riadeného governance postupu bez začatia implementácie `0.2B.1`, bez tvorby JSON schém a bez prijatia nových ADR v tejto úlohe.

## 2. Scope

Dokument pokrýva:

- ktoré CRC findings boli zapracované revíziou RFC-0001, RFC-0002 a RFC-0003,
- ktoré findings zostávajú deferred,
- ktoré ADR kandidáty treba pripraviť pred prijatím RFC,
- ktoré prefixy bude potrebné doplniť do `EOS-003`,
- odporúčané poradie akceptácie RFC,
- vstupné kritériá pre `0.2B.1`,
- výstupné kritériá Architecture Closure.

Dokument nepokrýva:

- JSON schémy,
- zmeny existujúcich schém,
- implementáciu validačnej alebo aplikačnej logiky,
- prijatie RFC do stavu `Accepted`,
- zmenu `EOS-003`,
- vytvorenie ADR.

## 3. Preconditions

Pred formálnym uzatvorením architektúry musia platiť tieto podmienky:

- aktuálna vetva je `feature/phase-0.2b-knowledge-contracts`,
- RFC-0001, RFC-0002 a RFC-0003 existujú,
- `RFC-0001-0003_Cross_Consistency_Review.md` existuje,
- `EOS-008_Architecture_Baseline.md` existuje v stave Draft,
- počet JSON schém ostáva 10,
- počet ADR súborov ostáva 14,
- nové knowledge-core JSON schémy ešte neexistujú,
- Phase 0.2B.1 ešte nebola implementovaná.

## 4. Findings Addressed By The Coordinated Revision

| Finding | Closure state | Resolution |
| --- | --- | --- |
| `CRC-0001` | Closed | `MeasurementQuality` je jediný preferovaný názov; `ValueQuality` je zakázané autoritatívne použitie |
| `CRC-0002` | Closed | `Observation Scope` je definovaný a `Observation` používa koncept `observationScope` |
| `CRC-0003` | Closed | `PropertyRecord` je definovaný ako embedded claim-like value object |
| `CRC-0005` | Closed | Fázovanie je zosúladené na `0.2B.1`, `0.2B.2` a `0.2C` |
| `CRC-0006` | Closed | RFC-0003 dopĺňa chýbajúce glossary pojmy potrebné pre architektonické uzatvorenie |
| `CRC-0007` | Closed for architecture closure | `Decision` je boundary koncept pre `0.2B.1`; stored kontrakt je odložený bez samostatného rozhodnutia |
| `CRC-0008` | Closed for architecture closure | `Snapshot` je definovaný ako zmrazený auditovateľný obraz vstupov; stored kontrakt zostáva deferred |
| `CRC-0011` | Closed | Preferovaný názov vrstvy je `Engineering Knowledge Layer`; `Knowledge Layer` je iba informatívny alias |
| `CRC-0012` | Closed | `Source Classification` je definovaná a odlíšená od `Document basis` |
| `CRC-0013` | Closed | Prah pre first-class `Relationship` je definovaný |
| `CRC-0014` | Closed | `Condition` a `Classification` môžu byť v `0.2B.1` value-object kontrakty alebo odkazy; katalógové entity patria do `0.2B.2` |

## 5. Findings Deferred

| Finding | Deferred state | Reason |
| --- | --- | --- |
| `CRC-0004` | Partially closed | Terminológia embedded observation records je zapracovaná; `AvailabilityRecord` a `CommercialObservation` sú mimo minimálneho scope `0.2B.1` |
| `CRC-0009` | Deferred | RFC lifecycle vyžaduje samostatný governance krok alebo ADR; tento dokument ho iba navrhuje |
| `CRC-0010` | Deferred | Prefixy musia byť doplnené do `EOS-003` v samostatnej governance úlohe |

## 6. Required ADRs Before RFC Acceptance

### 6.1 Establish RFC Governance Lifecycle

**Need:** Required.

**Reason:** RFC dokumenty už používajú stavy `Draft`, `Review`, `Accepted`, `Rejected` a `Superseded`, ale ich lifecycle ešte nie je formálne prijatý governance rozhodnutím.

**Scope:** Stavový model RFC, pravidlá pre prechod do `Accepted`, vzťah RFC a ADR, pravidlá pre supersede a zodpovednosť za schválenie.

**Alternatives considered:**

- ponechať RFC lifecycle iba v texte RFC,
- doplniť ho priamo do `EOS-002`,
- vytvoriť samostatné ADR a neskôr aktualizovať governance dokumenty.

**Blocks RFC acceptance:** Yes.

**Blocks start of 0.2B.1:** Yes, ak sa má `0.2B.1` opierať o Accepted RFC.

### 6.2 Establish Engineering Knowledge Layer

**Need:** Required.

**Reason:** Engineering Knowledge Layer je nová architektonická vrstva medzi governance pravidlami a konkrétnymi knowledge entities. Bez rozhodnutia by budúce kontrakty mohli miešať všeobecné knowledge pravidlá s doménovými entitami.

**Scope:** Názov vrstvy, zodpovednosť vrstvy, povolené závislosti a hranice voči Knowledge Core Contracts, Knowledge Catalogs a Knowledge Entities.

**Alternatives considered:**

- ponechať pravidlá priamo v entity RFC,
- zlúčiť vrstvu s Governance Layer,
- zaviesť samostatnú Engineering Knowledge Layer.

**Blocks RFC acceptance:** Yes, pre RFC-0002 a RFC-0003.

**Blocks start of 0.2B.1:** Yes.

### 6.3 Treat Observation As First-Class Evidence Entity

**Need:** Required.

**Reason:** `Observation` je jadrová evidence entita s dopadom na ID, lifecycle, audit, sourceLinks a povýšenie tvrdení. Musí byť jasne odlíšená od embedded observation records.

**Scope:** First-class `Observation` so stabilným `OBS-xxxxxx`, `observationScope`, append-only orientácia, evidence úloha a zákaz automatickej zmeny autoritatívnych `PropertyRecord`.

**Alternatives considered:**

- modelovať všetky pozorovania iba ako vnorené records,
- vytvoriť samostatné typy pre job/project/experiment observations,
- použiť jednotnú first-class `Observation` so scope a odlíšiť embedded observation records.

**Blocks RFC acceptance:** Yes, pre RFC-0001 a RFC-0002.

**Blocks start of 0.2B.1:** Yes, ak je `Observation` v minimálnom scope.

### 6.4 ADRs Not Required Before 0.2B.1

Samostatný ADR pre Hybrid DDD Taxonomy sa zatiaľ neodporúča vytvárať, pokiaľ ďalšie review nepreukáže reálny konflikt medzi entity/value object/aggregate modelom a schválenou architektúrou.

Samostatný ADR pre Reference Catalog vs Knowledge Catalog sa odporúča odložiť minimálne do prípravy `0.2B.2`, pokiaľ nebude potrebný na prijatie RFC-0002.

## 7. Required EOS-003 Identifier Updates

`EOS-003` sa v tejto úlohe nemení. Pred implementáciou schém však musí vzniknúť samostatná governance aktualizácia alebo ADR s nadväznou zmenou `EOS-003`.

### Required Before 0.2B.1

- `RFC-xxxx` pre RFC dokumenty,
- `OBS-xxxxxx` pre first-class `Observation`,
- `PRP-xxxxxx` pre Property Catalog Entry alebo stabilný property identifier,
- `UNT-xxxxxx` pre Unit Catalog Entry alebo stabilný unit identifier.

### Potentially Required Before 0.2B.1

- `DEC-xxxxxx` ako kandidátsky prefix pre `Decision`, iba ak `Decision` dostane samostatný stored kontrakt.

`DEC-xxxxxx` nie je týmto dokumentom prijatý ako autoritatívny prefix.

### Required Before 0.2B.2

- `CLS-xxxxxx` pre Classification Catalog Entry,
- `CND-xxxxxx` pre Condition Type Catalog Entry.

### Deferred

- `REL-xxxxxx` pre first-class Relationship,
- `EVT-xxxxxx` pre všeobecný Event object.

## 8. RFC Acceptance Sequence

Odporúčané poradie:

1. Pripraviť ADR pre RFC Governance Lifecycle.
2. Pripraviť ADR pre Engineering Knowledge Layer.
3. Pripraviť ADR pre Observation as First-Class Evidence Entity.
4. Aktualizovať `EOS-003` o prefixy required before `0.2B.1`.
5. Skontrolovať, že RFC-0001 Revision 2, RFC-0002 Revision 2 a RFC-0003 Revision 1 sú vzájomne konzistentné.
6. Presunúť RFC-0003 z `Review` do `Accepted`, ak slovník už neobsahuje blokujúce otázky pre `0.2B.1`.
7. Presunúť RFC-0001 z `Review` do `Accepted`.
8. Presunúť RFC-0002 z `Review` do `Accepted`.
9. Až potom začať `Phase 0.2B.1 Knowledge Core Contracts`.

RFC nemajú byť označené `Accepted` v tejto úlohe.

## 9. Entry Criteria For Phase 0.2B.1

Pred začatím `0.2B.1` musia byť splnené:

- RFC-0001, RFC-0002 a RFC-0003 sú `Accepted` alebo výslovne schválené ako vstup pre implementáciu,
- required ADR z časti 6 sú prijaté alebo výslovne odložené s dôvodom,
- `EOS-003` obsahuje required prefixy pre `0.2B.1`,
- `MeasurementQuality`, `Observation Scope`, `PropertyRecord`, `Claim`, `Embedded Claim`, `Source Classification`, `Snapshot` a `Relationship` sú terminologicky stabilné,
- je rozhodnuté, či `Decision` je stored kontrakt alebo iba boundary koncept,
- počet existujúcich JSON schém je pred začiatkom implementácie známy a zmeny sú kontrolované,
- validačné testy prechádzajú.

Odporúčaný minimálny scope `0.2B.1`:

- `Quantity`,
- `ValueRange`,
- `MeasurementQuality`,
- `Condition`,
- `Classification`,
- `PropertyRecord`,
- `Observation`.

`Decision` sa odporúča ponechať ako boundary koncept bez samostatného stored kontraktu v prvom scope, pokiaľ governance nerozhodne inak.

`Snapshot` sa odporúča ponechať ako definovaný auditový pojem bez samostatného stored kontraktu v prvom scope, pokiaľ sa v `0.2B.1` neimplementuje `Derived Result`.

Do `0.2B.1` zatiaľ nepatria:

- `AvailabilityRecord`,
- `CommercialObservation`,
- Property Catalog,
- Unit Catalog,
- Classification Catalog,
- Condition Type Catalog,
- `Relationship`,
- `Material`,
- `Machine`,
- `Supplier`,
- `StockMaterial`,
- `ManufacturingProcess`.

## 10. Exit Criteria For Architecture Closure

Architecture Closure môže byť uzavretá, keď:

- RFC-0001, RFC-0002 a RFC-0003 majú schválený cieľový stav,
- všetky Critical a High findings z cross-consistency review sú uzavreté alebo formálne odložené,
- required ADR sú prijaté alebo odložené s explicitným dôvodom,
- required prefixy pre `0.2B.1` sú schválené v governance,
- `EOS-008` alebo jeho nástupca zodpovedá finálnemu stavu,
- nie je otvorený terminologický konflikt blokujúci JSON kontrakty,
- testy validácie prechádzajú,
- Phase `0.2B.1` je stále nezačatá až do formálneho schválenia vstupu.

## 11. Risks

- Ak sa `EOS-003` neaktualizuje pred schémami, ID prefixy sa môžu dostať do kontraktov bez autoritatívnej opory.
- Ak sa `Decision` začne implementovať bez ADR alebo samostatného RFC, môže vzniknúť nejasná aggregate boundary.
- Ak sa katalógy posunú príliš ďaleko, `PropertyRecord.propertyId` a `Quantity.unitId` budú mať stabilný formát bez autoritatívneho významu.
- Ak sa `Observation` a embedded observation records zmiešajú, vznikne konflikt lifecycle a audit pravidiel.
- Ak sa `Relationship` vytvorí príliš skoro, model sa môže zbytočne skomplikovať pred graph DB potrebou.

## 12. Change History

| Date | Version | Revision | Author | Summary |
| --- | --- | --- | --- | --- |
| 2026-07-25 | 0.1 | 0 | Codex | Initial architecture closure plan for preparing RFC-0001, RFC-0002 and RFC-0003 for governance acceptance before Phase 0.2B.1 |
