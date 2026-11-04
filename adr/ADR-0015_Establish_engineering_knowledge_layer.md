# ADR-0015 - Establish Engineering Knowledge Layer

**Status:** Accepted  
**Date:** 2026-08-01  

## Title

Establish Engineering Knowledge Layer

## Context

EOS smeruje k implementácii `Phase 0.2B.1 - Knowledge Core Contracts`. Pred vytvorením konkrétnych JSON schém je potrebné autoritatívne rozhodnúť, kde v architektúre ležia spoločné znalostné pojmy, evidence pravidlá, katalógy, zdrojové väzby a hranice medzi pozorovaním, odvodeným výsledkom a rozhodnutím.

RFC-0001, RFC-0002 a RFC-0003 zavádzajú a stabilizujú pojem `Engineering Knowledge Layer`, ale tieto RFC sú stále v stave `Review`. `EOS-010_Architecture_Readiness_Review.md` označuje rozhodnutie o Engineering Knowledge Layer ako nutnú podmienku pred začatím Knowledge Core Contracts.

Bez samostatného ADR hrozí, že znalostný model bude zamieňaný s databázovou štruktúrou, JSON schémami, API DTO, výpočtovým enginom alebo workflow pravidlami. Takéto miešanie by oslabilo dlhodobú použiteľnosť EOS pre PostgreSQL, graph DB, REST API, AI layer, quotation engine aj manufacturing engine.

## Decision

EOS zavádza `Engineering Knowledge Layer` ako autoritatívnu architektonickú vrstvu technických znalostí.

`Engineering Knowledge Layer` opisuje technickú realitu, význam znalostných objektov, evidence pravidlá, katalógové významy, referencie, podmienky platnosti, pozorovania a hranice rozhodovania.

Táto vrstva nepopisuje, ako sa dáta ukladajú, zobrazujú, počítajú, importujú, exportujú alebo procesne používajú v konkrétnej firme.

Engineering Knowledge Layer je nezávislá od:

- databázy,
- SQL schémy,
- graph databázy,
- REST API,
- CLI,
- UI,
- programovacieho jazyka,
- Python tried,
- ORM modelu,
- frameworku,
- fyzického formátu súboru.

JSON Schema je v EOS iba serializačný a validačný kontrakt pre výmenu a kontrolu dát. JSON Schema nie je samotný Knowledge Model.

## Scope Of Engineering Knowledge Layer

Do Engineering Knowledge Layer patria najmä:

- `Quantity`,
- `ValueRange`,
- `MeasurementQuality`,
- `Condition`,
- `Classification`,
- `PropertyRecord`,
- `Observation`,
- `Material`,
- `ManufacturingProcess`,
- `Machine`,
- `Supplier`,
- `CuttingTool`,
- `NormReference`,
- `SourceReference`,
- `DocumentRecord`,
- knowledge catalogs,
- `Property Catalog`,
- `Unit Catalog`,
- budúce katalógy typov podmienok a klasifikácií,
- pravidlá pre `SourceLink` a evidence použitie,
- pravidlá porovnateľnosti vlastností,
- konceptuálne hranice pre `Derived Result` a `Decision`.

Do Engineering Knowledge Layer nepatria:

- GUI,
- REST API,
- CLI,
- business workflow,
- calculation engine,
- cost calculation,
- scheduler,
- optimization,
- import,
- export,
- authentication,
- authorization,
- database server,
- persistence implementation,
- framework-specific model,
- ORM mapping,
- cache,
- reporting view.

## Layer Separation

EOS používa nasledujúce architektonické oddelenie:

| Layer | Zodpovednosť | Nepatrí sem |
| --- | --- | --- |
| Governance Layer | Manifest, dokumentačné pravidlá, identifikácia, lifecycle, ADR, RFC a validačné štandardy | konkrétne technické znalosti a runtime implementácia |
| Engineering Knowledge Layer | Význam technických znalostí, základné znalostné objekty, evidence, katalógy, pozorovania, zdrojové väzby a rozhodovacie hranice | UI, workflow, databáza, API a kalkulačné algoritmy |
| Process Layer | Firemné a operačné postupy, schvaľovacie kroky, obchodné alebo výrobné workflow | autoritatívny význam technických objektov |
| Application Layer | Validácia, služby, API operácie, orchestrace, integračné správanie a pravidlá používania znalostí | definícia znalostného významu ako takého |
| Presentation Layer | Používateľské rozhranie, zobrazenie, navigácia a interakcia | autoritatívna znalosť a výpočtová logika |
| Infrastructure Layer | Úložisko, databáza, súborový systém, runtime, deployment a technické adaptéry | doménové rozhodnutia a znalostný význam |

## Authoritative Principles

Engineering Knowledge Layer sa riadi týmito pravidlami:

- Knowledge Layer nesmie obsahovať UI logiku.
- Knowledge Layer nesmie obsahovať kalkulačné algoritmy.
- Knowledge Layer nesmie obsahovať firemné business pravidlá.
- Knowledge Layer opisuje, čo objekt je, nie ako sa v konkrétnom procese používa.
- Engineering knowledge je immutable by meaning: význam schváleného znalostného záznamu sa nesmie meniť tichou reinterpretáciou.
- Interpretácia nesmie zmeniť význam autoritatívneho záznamu.
- `Derived Result` nikdy nesmie prepísať source-backed claim.
- `Observation` je evidence, nie automaticky autoritatívna vlastnosť.
- `Decision` rozhoduje, či sa evidence, odvodený výsledok alebo odporúčanie prijíma, odmieta alebo používa podmienene.
- Knowledge Layer neobsahuje Decision Workflow; definuje iba hranicu a význam objektu `Decision`.

## Relationship To DDD

Engineering Knowledge Layer používa DDD pojmy ako modelovacie hranice, nie ako konkrétnu implementáciu.

`Aggregate Root` je entita, ktorá riadi konzistentnú hranicu zmeny a vlastní vnorené objekty. Aggregate root nikdy nevlastní iný aggregate root; môže ho iba referencovať stabilným ID.

`Entity` má stabilnú identitu, vlastný lifecycle a auditovateľnú históriu. Príkladmi sú `Material`, `Machine`, `ManufacturingProcess`, `Supplier`, `SourceReference`, `NormReference`, `DocumentRecord` a first-class `Observation`.

`Value Object` je definovaný hodnotou a reviduje sa cez rodičovský objekt. Príkladmi sú `Quantity`, `ValueRange`, `MeasurementQuality`, `Condition`, `Classification` a `PropertyRecord`, ak je použitý ako embedded claim-like value object.

`Reference Object` reprezentuje autoritatívny zdroj alebo externý význam používaný inými objektmi. Príkladmi sú `SourceReference` a `NormReference`.

`Catalog Entry` je autoritatívna položka riadeného katalógu, napríklad budúca položka `Property Catalog` alebo `Unit Catalog`.

`Observation` je first-class evidence entity, ak má stabilné `OBS-xxxxxx`, vlastný lifecycle a môže podporovať viac tvrdení. Embedded observation records, napríklad `AvailabilityRecord` alebo `CommercialObservation`, nemajú byť zamieňané s plnohodnotnou first-class `Observation`.

## JSON Schema Relationship

JSON schémy v EOS majú vyjadriť serializačný kontrakt schváleného znalostného modelu.

Pravidlá:

- JSON Schema nesmie zavádzať nový znalostný význam, ktorý neexistuje v governance, Accepted ADR alebo Accepted RFC.
- JSON Schema má používať názvy objektov a polí konzistentné s glossary a prijatými rozhodnutiami.
- JSON Schema validuje štruktúru, typy, povinnosť polí a podporované syntaktické pravidlá.
- Aplikačná validácia EOS zostáva zodpovedná za významové pravidlá, referenčnú integritu, lifecycle pravidlá, kompatibilitu zdrojov, rozhodovacie hranice a pravidlá, ktoré JSON Schema nevie vyjadriť.
- JSON Schema nie je databázový model, ORM model ani aplikačný service contract.

## Rejected Alternatives

### 1. Knowledge Layer = Database

Odmietnuté, pretože databáza je infraštruktúrny spôsob uloženia dát. Znalostný význam musí zostať stabilný aj pri budúcej migrácii z JSON súborov do PostgreSQL, graph DB alebo iného úložiska.

### 2. Knowledge Layer = JSON

Odmietnuté, pretože JSON je formát reprezentácie. Rovnaký znalostný význam musí byť použiteľný aj cez API, databázu, export alebo interný engine bez zmeny významu.

### 3. Knowledge Layer = JSON Schema

Odmietnuté, pretože JSON Schema je kontrakt štruktúry a validácie. Nezachytáva celý význam engineering knowledge, rozhodovacie hranice, referenčnú integritu ani všetky aplikačné pravidlá.

### 4. Knowledge Layer = ORM

Odmietnuté, pretože ORM mapping je implementačný detail persistence vrstvy. Autoritatívny model nesmie závisieť od budúceho databázového frameworku.

### 5. Knowledge Layer = Python Classes

Odmietnuté, pretože Python triedy sú implementačný prostriedok. EOS musí zachovať význam znalostí nezávisle od konkrétneho jazyka alebo runtime.

### 6. Knowledge Layer = API DTO

Odmietnuté, pretože DTO opisuje prenosový tvar pre konkrétne rozhranie. API tvar môže byť optimalizovaný pre klienta a nemusí byť totožný s autoritatívnym knowledge modelom.

### 7. Knowledge Layer = SQL Schema

Odmietnuté, pretože SQL schéma optimalizuje ukladanie a dotazovanie. Nemá sama určovať význam objektov, lifecycle, evidence ani DDD hranice.

### 8. Knowledge Layer = Calculation Engine

Odmietnuté, pretože calculation engine počíta z explicitných vstupov. Výsledok výpočtu je `Derived Result`, nie zdrojová znalosť, a nesmie automaticky prepísať source-backed claim.

### 9. Knowledge Layer = Workflow

Odmietnuté, pretože workflow opisuje postup použitia, schválenia alebo prevádzky. Knowledge Layer má opisovať význam objektov, nie firemný proces ich používania.

## Consequences

Pozitívne dôsledky:

- Phase 0.2B.1 môže začať z jasnej architektonickej vrstvy.
- Znalostný model nebude závislý od databázy, API, JSON súborov ani Python implementácie.
- `Observation`, `SourceReference`, `SourceLink`, `PropertyRecord`, katalógy a budúce rozhodnutia majú spoločný významový rámec.
- Budúce PostgreSQL, graph DB, REST API, AI layer, Quotation Engine a Manufacturing Engine môžu používať rovnaký model bez zásadného redizajnu.
- Oddelí sa zdrojová znalosť, evidence, odvodený výsledok a engineer decision.

Nevýhody:

- Pribúda samostatná architektonická vrstva, ktorú treba udržiavať konzistentne s RFC, ADR a schémami.
- Implementácia 0.2B.1 musí rešpektovať viac hraníc a nemôže začať priamo od entitných JSON schém.
- Niektoré aplikačné pravidlá nebude možné pokryť iba JSON Schema validáciou.

Riziká:

- Ak sa vrstva nebude dôsledne udržiavať, môže vzniknúť paralelná terminológia medzi dokumentáciou, schémami a implementáciou.
- Ak sa do Knowledge Layer prenesú workflow alebo výpočtové pravidlá, začne sa miešať význam znalostí s použitím znalostí.
- Ak budú JSON schémy považované za samotný knowledge model, budúca migrácia do databázy alebo API môže vyžadovať zbytočný redizajn.

## Compliance and Validation

Budúce review a implementačné kontroly majú overovať:

- či nové znalostné objekty patria do Engineering Knowledge Layer alebo do inej vrstvy,
- či JSON schéma nezavádza nový autoritatívny význam bez Accepted ADR alebo Accepted RFC,
- či výpočtový výstup ostáva `Derived Result` a neprepisuje source-backed claim,
- či `Observation` zostáva evidence a nie automatická autoritatívna vlastnosť,
- či process, UI, persistence a infrastructure pravidlá nie sú vložené do knowledge kontraktov,
- či aggregate roots referencujú iné aggregate roots cez stabilné ID.

Toto ADR nevytvára validátor, JSON schému ani aplikačnú implementáciu.

## Open Follow-up Actions

- Vytvoriť následné ADR pre `Observation` ako first-class evidence entity.
- Aktualizovať `EOS-003` o potrebné prefixy v samostatnej governance úlohe.
- Formálne uzatvoriť prijatie RFC-0001, RFC-0002 a RFC-0003 podľa ADR-0014.
- Spustiť `Phase 0.2B.1 - Knowledge Core Contracts` až po splnení architecture closure podmienok.
- V ďalšej fáze rozhodnúť presný rozsah `Property Catalog`, `Unit Catalog` a ďalších knowledge catalogs.

## Related Documents

- `docs/governance/EOS-000_Development_Manifesto.md`
- `docs/governance/EOS-001_System_Architecture.md`
- `docs/governance/EOS-003_Identification_and_Versioning.md`
- `docs/governance/EOS-004_Core_Data_Model.md`
- `docs/governance/EOS-008_Architecture_Baseline.md`
- `docs/governance/EOS-009_Architecture_Closure_Plan.md`
- `docs/governance/EOS-010_Architecture_Readiness_Review.md`
- `docs/rfc/RFC-0001_Engineering_Property_Model.md`
- `docs/rfc/RFC-0002_Engineering_Object_Taxonomy.md`
- `docs/rfc/RFC-0003_EOS_Engineering_Glossary.md`
- `adr/ADR-0014_Establish_RFC_governance_lifecycle.md`

## Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-08-01 | 0.1 | 0 | Codex | Initial accepted ADR establishing Engineering Knowledge Layer |

## Review Date

2026-08-15
