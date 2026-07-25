# RFC-0001 až RFC-0003 - Cross Consistency Review

**Project:** EOS - Engineering Operating System  
**Review ID:** RFC-0001-0003  
**Version:** 0.1  
**Revision:** 0  
**Status:** Draft  
**Author:** Codex  
**Last updated:** 2026-07-25  
**Document basis:** Internal architecture review  

## 1. Purpose

Tento dokument porovnáva aktuálny stav dokumentov:

- `RFC-0001_Engineering_Property_Model.md`,
- `RFC-0002_Engineering_Object_Taxonomy.md`,
- `RFC-0003_EOS_Engineering_Glossary.md`.

Cieľom je odhaliť terminologické, architektonické a implementačné nesúlady pred vstupom do fázy `0.2B.1 Knowledge Core Contracts`.

Review nevykonáva zmenu RFC dokumentov, nevytvára JSON schémy a neprijíma architektonické rozhodnutia. Slúži ako vstup pre revíziu RFC dokumentov, governance rozhodnutia a budúce ADR.

## 2. Scope

Review pokrýva:

- jednotnosť významu pojmov,
- jednotnosť názvov objektov,
- hranice medzi entitou, value object, reference object, catalog entry, observation, event, aggregate root a derived result,
- model `Observation`,
- model `PropertyRecord`,
- modely `Quantity`, `ValueRange` a `MeasurementQuality`,
- `Condition`, `Classification`, `Capability`, `AvailabilityRecord` a `CommercialObservation`,
- `SourceReference`, `SourceLink`, `Decision`, `Derived Result`, `Snapshot` a `Relationship`,
- katalógy,
- lifecycle, `verificationStatus`, `sourceLinks`,
- identifikátory a prefixy.

## 3. Executive Summary

RFC-0001 až RFC-0003 sú koncepčne kompatibilné. Spoločné jadro návrhu je silné: vlastnosti sú oddelené od meraní, zdroje sú explicitné, pozorovanie nie je automaticky autoritatívna zmena a katalógy majú niesť význam riadených identifikátorov.

Návrh však ešte nie je pripravený na priame spustenie `0.2B.1`. Blokujúce sú najmä:

- neuzavretý názov `MeasurementQuality` verzus `ValueQuality`,
- neúplne zosúladený model `Observation.observationScope`,
- nepresná definícia `PropertyRecord` ako embedded claim-like value object,
- chýbajúce autoritatívne glossary definície pre niektoré jadrové pojmy,
- neformálne zavedené prefixy mimo `EOS-003`,
- zatiaľ neschválené ADR pre vrstvu Engineering Knowledge Layer, hybridnú DDD taxonómiu a RFC lifecycle.

Odporúčanie je pripraviť revízie RFC-0001, RFC-0002 a RFC-0003 predtým, než začne tvorba kontraktov fázy `0.2B.1`.

## 4. Cross-Consistency Findings

### CRC-0001 - Neuzavretý názov `MeasurementQuality` verzus `ValueQuality`

**Affected documents:** RFC-0001, RFC-0002, RFC-0003  
**Severity:** High  
**Blocks 0.2B.1:** Yes  

RFC-0001 stále ponecháva otvorenú voľbu medzi `MeasurementQuality` a `ValueQuality`. RFC-0002 a RFC-0003 už používajú `MeasurementQuality` ako preferovaný pojem.

**Recommended authoritative wording:**  
EOS používa objekt `MeasurementQuality` ako value object opisujúci kvalitu, dôveru a obmedzenia hodnoty, merania alebo pozorovania. Názov `ValueQuality` sa v autoritatívnych dokumentoch nepoužíva.

**Document to update:** RFC-0001

### CRC-0002 - `Observation` nemá jednotne definovaný scope

**Affected documents:** RFC-0001, RFC-0002, RFC-0003  
**Severity:** Critical  
**Blocks 0.2B.1:** Yes  

RFC-0001 zavádza `Observation`, ale nevyžaduje `observationScope`. RFC-0002 odporúča jednotný model s poľom `observationScope` namiesto rozdelenia na viac typov pozorovania. RFC-0003 nemá samostatnú glossary položku `Observation Scope`.

**Recommended authoritative wording:**  
`Observation` je first-class evidence entity so stabilným ID `OBS-xxxxxx`. Kontext vzniku sa určuje poľom `observationScope` s hodnotami `GLOBAL`, `JOB`, `PROJECT` alebo `EXPERIMENT`, nie samostatnými typmi pozorovania.

**Document to update:** RFC-0001, RFC-0003

### CRC-0003 - `PropertyRecord` potrebuje presnejšie označenie ako embedded claim-like value object

**Affected documents:** RFC-0001, RFC-0002, RFC-0003  
**Severity:** High  
**Blocks 0.2B.1:** Yes  

RFC-0001 definuje `PropertyRecord` ako vnorený value object so `sourceLinks` a `verificationStatus`. RFC-0002 ho spresňuje ako embedded claim-like value object, pretože nejde o obyčajnú hodnotu. RFC-0003 túto nuansu ešte nevysvetľuje dostatočne autoritatívne.

**Recommended authoritative wording:**  
`PropertyRecord` je embedded claim-like value object. Nemá vlastnú identitu konkrétneho záznamu, ale nesie tvrdenie o vlastnosti cez `propertyId`, hodnotu, podmienky, `verificationStatus` a `sourceLinks`.

**Document to update:** RFC-0001, RFC-0003

### CRC-0004 - `AvailabilityRecord` a `CommercialObservation` majú byť embedded observation records

**Affected documents:** RFC-0001, RFC-0002, RFC-0003  
**Severity:** High  
**Blocks 0.2B.1:** Yes, if included in 0.2B.1 contracts  

RFC-0001 ich opisuje ako value objecty so zdrojmi. RFC-0002 ich presnejšie klasifikuje ako embedded observation records s časovou citlivosťou a append-only správaním. RFC-0003 ich definuje, ale neobsahuje samostatný pojem `Embedded Claim` alebo `Embedded Observation Record`.

**Recommended authoritative wording:**  
`AvailabilityRecord` a `CommercialObservation` sú embedded observation records. Sú vlastnené rodičovskou entitou, nemajú samostatnú globálnu identitu a po schválení sa majú meniť novým záznamom alebo revíziou, nie tichým prepisom.

**Document to update:** RFC-0001, RFC-0003

### CRC-0005 - Fázovanie v RFC-0001 nezodpovedá neskoršiemu rozdeleniu 0.2B.1 / 0.2B.2 / 0.2C

**Affected documents:** RFC-0001, RFC-0002  
**Severity:** Medium  
**Blocks 0.2B.1:** No, if baseline explicitly overrides sequencing  

RFC-0001 navrhuje implementačné kroky priamo smerom k schémam vlastností, pozorovaní a katalógov. RFC-0002 zavádza presnejšie fázovanie: `0.2B.1 Knowledge Core Contracts`, `0.2B.2 Knowledge Catalogs`, `0.2C Knowledge Entities`.

**Recommended authoritative wording:**  
Po prijatí baseline má byť implementačné poradie: najprv jadrové kontrakty, potom katalógy, potom konkrétne znalostné entity.

**Document to update:** RFC-0001, ROADMAP v samostatnej governance úlohe

### CRC-0006 - RFC-0003 nemá všetky pojmy potrebné pre 0.2B.1

**Affected documents:** RFC-0003  
**Severity:** Critical  
**Blocks 0.2B.1:** Yes  

Chýbajú alebo sú nepresné viaceré termíny potrebné pre kontrakty: `Knowledge Core`, `Claim`, `Embedded Claim`, `Observation Scope`, `Reference Catalog`, `Knowledge Catalog`, `Aggregate Boundary`, `Transaction Boundary`, `Referential Integrity`, `Source Classification`, `Authoritative Data`, `Derived Data`, `Append-only`, `Immutable`, `Property Catalog Entry`, `Unit Catalog Entry` a `Snapshot`.

**Recommended authoritative wording:**  
RFC-0003 má byť pred implementáciou `0.2B.1` rozšírený na Revision 1 a má obsahovať autoritatívnu definíciu každého pojmu použitého v kontraktoch.

**Document to update:** RFC-0003

### CRC-0007 - `Decision` je zavedený neskôr než property model

**Affected documents:** RFC-0001, RFC-0002, RFC-0003  
**Severity:** High  
**Blocks 0.2B.1:** Yes, if `Decision` is part of 0.2B.1  

RFC-0002 zavádza `Decision` ako schvaľovací objekt medzi dôkazmi, odvodeným výsledkom a autoritatívnou zmenou. RFC-0001 opisuje `Observation` ako dôkaz pre zmenu `PropertyRecord`, ale neobsahuje explicitný rozhodovací krok.

**Recommended authoritative wording:**  
`Observation` alebo `Derived Result` nesmie automaticky zmeniť autoritatívny `PropertyRecord`. Prijatie, odmietnutie alebo povýšenie tvrdenia musí byť reprezentované objektom `Decision` alebo ekvivalentným schváleným governance mechanizmom.

**Document to update:** RFC-0001, RFC-0002

### CRC-0008 - `Snapshot` nemá dostatočnú definíciu pre audit odvodených výsledkov

**Affected documents:** RFC-0002, RFC-0003  
**Severity:** Medium  
**Blocks 0.2B.1:** No, unless `Derived Result` is implemented in 0.2B.1  

RFC-0002 definuje `Snapshot` ako zmrazený obraz vstupov. RFC-0003 ho uvádza iba ako otvorenú otázku, nie ako autoritatívny pojem.

**Recommended authoritative wording:**  
`Snapshot` je append-only záznam vstupného stavu použitý pri výpočte, rozhodnutí alebo audite. Nie je živou referenciou na aktuálny stav entity.

**Document to update:** RFC-0003

### CRC-0009 - Lifecycle RFC dokumentov nie je ešte governance kontrakt

**Affected documents:** RFC-0001, RFC-0002, RFC-0003, EOS-002, EOS-003  
**Severity:** High  
**Blocks 0.2B.1:** Yes  

RFC dokumenty používajú stav `Draft`, `Review` a budúci `Accepted`, ale lifecycle RFC nie je samostatne ukotvený v governance pravidlách ani ADR.

**Recommended authoritative wording:**  
RFC dokument môže prejsť do `Accepted` iba po explicitnom review, zapísanej zmene histórie a potvrdení, že nemení prijaté ADR alebo governance dokument bez nadväzujúceho ADR.

**Document to update:** nový ADR a prípadne EOS-002/EOS-003 v samostatnej úlohe

### CRC-0010 - Prefixy pre knowledge objekty sú zatiaľ iba navrhnuté

**Affected documents:** RFC-0001, RFC-0002, RFC-0003, EOS-003  
**Severity:** Critical  
**Blocks 0.2B.1:** Yes  

Prefixy `RFC-xxxx`, `OBS-xxxxxx`, `PRP-xxxxxx`, `UNT-xxxxxx`, `CLS-xxxxxx`, `CND-xxxxxx`, `REL-xxxxxx` a `EVT-xxxxxx` sú v RFC dokumentoch navrhnuté, ale nie sú zapísané v autoritatívnom identifikačnom štandarde `EOS-003`.

**Recommended authoritative wording:**  
Žiadny nový prefix sa nesmie použiť v JSON schéme ako autoritatívny formát, kým nie je zapísaný v `EOS-003` alebo schválený ADR s nadväznou aktualizáciou `EOS-003`.

**Document to update:** EOS-003 v samostatnej governance úlohe

### CRC-0011 - Názov vrstvy je nejednotný

**Affected documents:** RFC-0002, RFC-0003  
**Severity:** Medium  
**Blocks 0.2B.1:** Yes, if layer names are encoded in contracts or docs  

RFC-0002 používa `Engineering Knowledge Layer`. RFC-0003 preferuje kratší termín `Knowledge Layer`.

**Recommended authoritative wording:**  
Preferovaný názov vrstvy je `Engineering Knowledge Layer`. Skrátený výraz `Knowledge Layer` môže byť iba informatívny alias, nie autoritatívny názov.

**Document to update:** RFC-0003

### CRC-0012 - `Source Classification` nie je glossary pojem

**Affected documents:** RFC-0001, RFC-0002, RFC-0003, EOS-004  
**Severity:** Medium  
**Blocks 0.2B.1:** Yes, if `SourceLink.sourceClass` is included  

RFC a governance dokumenty používajú triedy zdrojov a `sourceClass`, ale RFC-0003 nemá autoritatívny pojem `Source Classification`.

**Recommended authoritative wording:**  
`Source Classification` je riadená klasifikácia technického tvrdenia podľa pôvodu zdroja. Nie je governance pôvod dokumentu a nesmie sa používať pre hlavičku governance dokumentov.

**Document to update:** RFC-0003

### CRC-0013 - `Relationship` je správne odložený, ale musí mať hranicu

**Affected documents:** RFC-0002, RFC-0003  
**Severity:** Medium  
**Blocks 0.2B.1:** No  

RFC-0002 odporúča first-class `Relationship` až neskôr. RFC-0003 definuje pojem všeobecne, ale neobsahuje pravidlo, kedy sa vzťah ešte modeluje obyčajným ID poľom a kedy už potrebuje samostatný objekt.

**Recommended authoritative wording:**  
`Relationship` sa stane first-class objektom až vtedy, keď vzťah nesie vlastné zdroje, stav overenia, časovú platnosť, audit, vlastnú identitu alebo graph export význam.

**Document to update:** RFC-0003, budúci RFC podľa potreby

### CRC-0014 - `Classification` a `Condition` majú katalógovú budúcnosť, ale nie jednotný štart

**Affected documents:** RFC-0001, RFC-0002, RFC-0003  
**Severity:** Medium  
**Blocks 0.2B.1:** No, blocks 0.2B.2 if unresolved  

RFC-0001 ponecháva `Classification` ako value object s možným budúcim katalógom. RFC-0002 už navrhuje `Classification Catalog` a `Condition Type Catalog` s prefixmi `CLS-xxxxxx` a `CND-xxxxxx`.

**Recommended authoritative wording:**  
`Classification` a `Condition` môžu začať ako value objecty, ale ich katalógové položky a prefixy patria do `0.2B.2 Knowledge Catalogs`, nie do základného kontraktu `0.2B.1`, pokiaľ nie sú nevyhnutné pre prvé schémy.

**Document to update:** RFC-0002, RFC-0003

## 5. Glossary Completeness Review

| Term | Current state in RFC-0003 | Required action |
| --- | --- | --- |
| Engineering Knowledge Layer | Imprecise: RFC-0003 uses `Knowledge Layer` | Add preferred term `Engineering Knowledge Layer`; keep `Knowledge Layer` only as alias |
| Knowledge Core | Missing | Add definition before 0.2B.1 |
| Claim | Missing | Add definition before 0.2B.1 |
| Embedded Claim | Missing | Add definition before 0.2B.1 |
| Observation Scope | Missing | Add definition before 0.2B.1 |
| Evidence | Present | No blocking action |
| Decision | Present | Clarify ID/lifecycle when ADR decides scope |
| Derived Result | Present | Clarify relation to `Snapshot` before implementation |
| Snapshot | Missing as authoritative entry | Add definition before derived-result contracts |
| Relationship | Present | Add first-class threshold rule |
| Reference Catalog | Missing | Add definition before 0.2B.2 |
| Knowledge Catalog | Missing | Add definition before 0.2B.2 |
| Catalog Entry | Present | Clarify subtype naming |
| Property Catalog Entry | Missing | Add definition before 0.2B.2 |
| Unit Catalog Entry | Missing | Add definition before 0.2B.2 |
| Aggregate Boundary | Missing | Add definition before 0.2B.1 |
| Transaction Boundary | Missing | Add definition before 0.2B.1 |
| Referential Integrity | Missing | Add definition before 0.2B.1 |
| Source Classification | Missing | Add definition before 0.2B.1 |
| Verification Status | Present as `VerificationStatus` | Add naming note: JSON field/object term is `VerificationStatus`; prose alias may be informative only |
| Authoritative Data | Missing | Add definition before 0.2B.1 |
| Derived Data | Missing | Add definition before derived-result contracts |
| Append-only | Missing | Add definition before observation and decision contracts |
| Immutable | Missing | Add definition before observation and decision contracts |
| Superseded | Present | No blocking action |
| Deprecated | Present | No blocking action |

## 6. Identifier Prefix Review

| Prefix | Intended object | Classification | Rationale |
| --- | --- | --- | --- |
| `RFC-xxxx` | RFC document | Required before 0.2B.1 | RFC documents already exist and need formal governance lifecycle |
| `OBS-xxxxxx` | `Observation` | Required before 0.2B.1 | Observation is proposed as first-class evidence entity |
| `PRP-xxxxxx` | Property Catalog Entry | Required before 0.2B.1 | `PropertyRecord.propertyId` depends on a stable property identifier even before full catalog implementation |
| `UNT-xxxxxx` | Unit Catalog Entry | Required before 0.2B.1 | `Quantity.unitId` depends on a stable unit identifier even before full catalog implementation |
| `CLS-xxxxxx` | Classification Catalog Entry | Required before 0.2B.2 | Needed when Classification Catalog is introduced |
| `CND-xxxxxx` | Condition Type Catalog Entry | Required before 0.2B.2 | Needed when Condition Type Catalog is introduced |
| `REL-xxxxxx` | First-class Relationship | Deferred | Relationship is not planned for 0.2B.1 or 0.2B.2 |
| `EVT-xxxxxx` | General Event | Deferred | No approved general event model exists yet |

No reviewed prefix is currently rejected. `Decision` also needs a prefix decision if it becomes a stored first-class object in `0.2B.1`.

## 7. Governance Closure Proposal

### RFC-0001 Required Fixes

- Replace unresolved `MeasurementQuality` / `ValueQuality` wording with authoritative `MeasurementQuality`.
- Add `Observation.observationScope` as required concept if Observation enters 0.2B.1.
- Clarify that `PropertyRecord` is an embedded claim-like value object.
- Clarify that `AvailabilityRecord` and `CommercialObservation` are embedded observation records.
- Align implementation sequencing with `0.2B.1`, `0.2B.2` and `0.2C`.
- Add the `Decision` step as the mechanism that prevents evidence from silently changing authoritative records.

### RFC-0002 Required Fixes

- Keep Revision 1 in Review until prefix and glossary blockers are resolved.
- Clarify whether `Decision` is included in `0.2B.1` or only reserved for later.
- Clarify whether `Observation` must always have global `OBS-xxxxxx` identity or whether job-owned embedded observations are allowed.
- Mark catalog hierarchy decisions as binding only after the relevant ADR or accepted RFC update.

### RFC-0003 Required Fixes

- Add missing glossary entries listed in section 5.
- Rename preferred `Knowledge Layer` term to `Engineering Knowledge Layer`.
- Add alias rules for prose terms such as `Verification Status` versus programmatic `VerificationStatus`.
- Add explicit rules for first-class `Relationship`, append-only evidence, authoritative data and derived data.

### Suggested Order

1. Revise RFC-0003 from Draft to Review Revision 1 with missing terms.
2. Revise RFC-0001 to Review Revision 2 for naming, Observation scope, PropertyRecord and Decision alignment.
3. Revise RFC-0002 to Review Revision 2 only if required after RFC-0003 and RFC-0001 changes.
4. Create required ADRs.
5. Move RFC-0001, RFC-0002 and RFC-0003 to Accepted together or in a clearly documented sequence.

### ADRs Recommended Before Acceptance

- ADR - Establish RFC governance lifecycle.
- ADR - Establish Engineering Knowledge Layer.
- ADR - Adopt hybrid DDD engineering object taxonomy.
- ADR - Treat Observation as first-class evidence entity.
- ADR - Separate Reference Catalogs and Knowledge Catalogs, required before `0.2B.2`, not necessarily before `0.2B.1`.

## 8. Architecture Assessment

### Strong Points

- The proposal separates knowledge, evidence, derived results and implementation concerns.
- `Observation` is correctly prevented from silently becoming authoritative data.
- `PropertyRecord` remains embedded, which avoids premature proliferation of entity tables.
- Catalogs are treated as authority for meanings, not as incidental lookup lists.
- Source traceability through `SourceReference` and `SourceLink` is consistent with EOS governance.
- Aggregate root ownership is directionally aligned with DDD.

### Risks

- `PropertyRecord` can become too generic if `Property Catalog` is delayed without strict ID governance.
- `Observation` can become ambiguous if `observationScope` is not mandatory.
- `Decision` may create a new aggregate boundary that is not yet governed.
- `Reference Catalog` and `Knowledge Catalog` may share schema shape but require different approval rules.
- Missing glossary terms can leak into JSON schemas as inconsistent field names.

### Architectural Defects To Correct Before 0.2B.1

- Missing formal prefix governance for `RFC`, `OBS`, `PRP` and `UNT`.
- Missing authoritative glossary entries for core contract terms.
- Unresolved `MeasurementQuality` naming in RFC-0001.
- Incomplete decision boundary between evidence, derived result and accepted engineering knowledge.

## 9. Recommendation

Do not mark RFC-0001, RFC-0002 or RFC-0003 as Accepted yet.

Recommended next state:

- RFC-0001: keep Review and prepare Revision 2.
- RFC-0002: keep Review Revision 1 until related glossary and ADR work is complete.
- RFC-0003: keep Draft and prepare Revision 1.

After these fixes and the recommended ADRs, the set can be considered for Accepted status as the baseline for `0.2B.1 Knowledge Core Contracts`.

## 10. Change History

| Date | Version | Revision | Author | Summary |
| --- | --- | --- | --- | --- |
| 2026-07-25 | 0.1 | 0 | Codex | Initial cross-consistency review of RFC-0001, RFC-0002 and RFC-0003 before Phase 0.2B.1 |
