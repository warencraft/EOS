# CDR-0011 Property Catalog Pre-design Review

Project: EOS – Engineering Operating System  
Contract Review ID: CDR-0011  
Contract: Property Catalog  
Review type: Pre-design  
Phase: 0.2B.2.3-prep  
Version: 0.1  
Revision: 0  
Status: Review  
Document basis: Accepted EOS architecture + implemented Unit and Condition Type catalogs

## 1. Purpose

Určiť najmenší bezpečný kontrakt `Property Catalog Entry` verzie 1, ktorý dá autoritatívny význam existujúcim odkazom `PRP-xxxxxx` v `PropertyRecord` a `Observation`. Review vyberá hranice kontraktu, závislosti a validačné zodpovednosti bez vytvorenia JSON schémy, reálnych katalógových údajov alebo aplikačného validátora.

## 2. Scope

Review pokrýva rolu katalógu, typ položky, identitu `PRP`, hodnotové formy, jednotkové obmedzenia, podmienky, `MeasurementQuality`, zdrojovú dohľadateľnosť, lifecycle, klasifikácie, aliasy, rovnosť vlastností a závislosti na implementovaných katalógoch.

Mimo rozsahu sú dimenzionálny model, konverzie jednotiek, rule engine, Classification Catalog, porovnateľnosť konkrétnych záznamov, reálne technické vlastnosti, databáza, API a zmeny existujúcich kontraktov.

## 3. Reviewed Artifacts

Preskúmané boli:

- `AGENTS.md`;
- `EOS-003_Identification_and_Versioning.md`;
- `EOS-006_Data_Validation_Standard.md`;
- `EOS-007_Validation_Capability_Matrix.md`;
- Accepted `RFC-0001_Engineering_Property_Model.md`;
- Accepted `RFC-0002_Engineering_Object_Taxonomy.md`;
- Accepted `RFC-0003_EOS_Engineering_Glossary.md`;
- Accepted `ADR-0015_Establish_engineering_knowledge_layer.md`;
- `CDR-0006_PropertyRecord_PreDesign_Review.md`;
- `CDR-0008_Knowledge_Core_Integration_Review.md`;
- `CDR-0009_Unit_Catalog_PreDesign_Review.md`;
- `CDR-0010_Condition_Type_Catalog_PreDesign_Review.md`;
- implementované schémy `PropertyRecord`, `Observation`, `Quantity`, `ValueRange`, `MeasurementQuality` a `Condition`;
- implementované schémy Unit Catalog Entry a Condition Type Catalog Entry;
- spoločné schémy identifikátorov, metadát a `SourceLink`;
- schema index a súvisiaca projektová dokumentácia.

Pre-flight bol vykonaný na vetve `feature/phase-0.2b-knowledge-contracts`, na čistom HEAD `c822c30`. Existujú Unit Catalog Entry, Condition Type Catalog Entry, PropertyRecord a Observation. Property Catalog schéma, reálne PRP položky ani Classification Catalog neexistujú. Kompletných 152 existujúcich testov prešlo.

## 4. Authoritative Findings

| Oblasť | Klasifikácia | Zistenie |
| --- | --- | --- |
| Rola katalógu | AUTHORITATIVE | Property Catalog je Knowledge Catalog podľa RFC-0002 a RFC-0003 G-0025/G-0078. |
| Typ položky | AUTHORITATIVE | Je to `Catalog Entry` so stabilnou identitou, samostatným lifecycle, revíziou, auditom a citovateľnosťou. |
| Aggregate boundary | IMPLIED | Vzhľadom na vlastné ID, lifecycle a audit je položka samostatný Aggregate Root; iné aggregate roots ju iba referencujú. |
| Identita | AUTHORITATIVE | `PRP-xxxxxx` identifikuje jeden Property Catalog Entry alebo jeho stabilný autoritatívny property význam. |
| Spotrebitelia | AUTHORITATIVE | `PropertyRecord.propertyId` a `Observation.propertyId` odkazujú na ten istý PRP význam. |
| Hodnotové formy | AUTHORITATIVE | Aktuálne kontrakty spotrebiteľov podporujú iba `quantity` a `valueRange`. |
| Jednotky | AUTHORITATIVE | Obidve aktuálne hodnotové formy nesú `unitId`; Unit Catalog v1 zatiaľ nemá dimenziu ani konverziu. |
| Condition význam | AUTHORITATIVE | Condition Type Catalog definuje význam a základnú hodnotovú formu CND; property-specific povolenie patrí Property Catalogu. |
| Povinné Conditions | OPEN | Accepted architektúra neurčuje, či rovnaká povinnosť platí rovnako pre dôkazový Observation a claim-like PropertyRecord. |
| MeasurementQuality policy | OPEN | Architektúra povoľuje MeasurementQuality v oboch spotrebiteľoch, ale neurčuje property-specific required/allowed politiku. |
| Lifecycle a zdroje | AUTHORITATIVE | Catalog Entry má vlastný record lifecycle a source provenance; claim verification je od neho oddelená. |
| Classification | DEFERRED | Classification Catalog ešte neexistuje a property-specific klasifikačný profil nie je prijatý. |
| Alias a ekvivalencia | DEFERRED | Nie je prijatá collision, lokalizačná, externá kódová ani equivalence policy. |
| Rozmery a konverzie | DEFERRED | Unit Catalog v1 neposkytuje quantity kind, dimension ani conversion semantics. |

Žiadne zistenie nevyžaduje opravu Accepted RFC alebo ADR.

## 5. Catalog Role

Property Catalog je **Knowledge Catalog**. Definuje interný EOS význam používaný v znalostných tvrdeniach a dôkazoch; nie je iba registrom externého referenčného významu.

Jedna Property Catalog Entry je:

- `Catalog Entry` a `Entity` so stabilným ID;
- samostatný Aggregate Root pre lifecycle, versioning, revíziu a audit;
- nezávisle uložená, citovateľná a referencovateľná;
- source-backed podľa spoločných pravidiel;
- referencovaná z PropertyRecord a Observation cez `propertyId`.

Nie je Value Object, konkrétna hodnota vlastnosti, PropertyRecord, Observation result ani Reference Object externého zdroja.

## 6. PRP Identifier Semantics

`PRP-xxxxxx` identifikuje presne jednu Property Catalog Entry a jej stabilný autoritatívny význam. Koreň položky má používať pole `id`, konzistentne s ostatnými catalog entry aggregate roots. Pole `propertyId` patrí spotrebiteľom, ktorí položku referencujú.

PRP neidentifikuje:

- inštanciu PropertyRecord;
- Observation alebo jeho výsledok;
- Quantity, ValueRange alebo Condition;
- jednotku alebo klasifikáciu;
- názov, definíciu ani kombináciu názvu a jednotky.

Zmena významu schválenej PRP položky sa nesmie vykonať tichou reinterpretáciou. Významová nekompatibilita vyžaduje nový PRP alebo riadené nahradenie podľa governance.

## 7. Relationship to PropertyRecord

PropertyRecord je rodičom vlastnený claim-like Value Object. Ukladá konkrétne tvrdenie: `propertyId`, jednu hodnotovú vetvu, voliteľné MeasurementQuality a Conditions, `verificationStatus` a `sourceLinks`.

Property Catalog Entry definuje význam `propertyId` a v1 má riadiť:

- povolené hodnotové formy;
- presný zoznam povolených Unit Catalog ID;
- voliteľne presný zoznam povolených Condition Type ID.

Property Catalog Entry nepreberá konkrétnu hodnotu, claim verification, zdroje konkrétneho tvrdenia ani lifecycle rodičovskej entity. `PropertyRecord.verificationStatus` nesmie byť odvodený z `Property Catalog Entry.status`.

## 8. Relationship to Observation

Observation je first-class dôkazová Entity a Aggregate Root. Používa rovnaký PRP význam a rovnaké property-specific obmedzenia hodnotovej formy, jednotky a povolených condition types ako PropertyRecord.

Spoločný PRP význam nezlučuje ich zodpovednosti:

- Observation ostáva evidence;
- PropertyRecord ostáva claim-like knowledge;
- katalógová kompatibilita neznamená pravdivosť, prijatie ani povýšenie dôkazu na tvrdenie;
- lifecycle a source provenance každého spotrebiteľa zostávajú samostatné.

## 9. Candidate Field Inventory

| Pole alebo skupina | Rozhodnutie | Dôvod |
| --- | --- | --- |
| `id` | REQUIRED NOW | Stabilné `PRP-xxxxxx`. |
| common metadata | REQUIRED NOW | Rovnaký metadata pattern ako existujúce katalógy. |
| `name` | REQUIRED NOW | Kanonický neprázdny ľudsky čitateľný názov. |
| `description` | REQUIRED NOW | Autoritatívna slovná definícia významu; nenahrádza štruktúrované pravidlá. |
| `allowedValueTypes` | REQUIRED NOW | Uzavrie kompatibilitu s aktuálnymi spotrebiteľmi. |
| `allowedUnitIds` | REQUIRED NOW | Pri dnešných výlučne unit-bearing hodnotách poskytne presný fail-closed UNT allow-list. |
| `canonicalUnitId` | DEFER | Bez konverzií a dimenzie by význam normalizácie bol neúplný. |
| `allowedConditionTypeIds` | OPTIONAL NOW | Ak chýba, Conditions nie sú pre property povolené; ak existuje, je to uzavretý CND allow-list. |
| `requiredConditionTypeIds` | DEFER | Povinnosť môže mať odlišný význam pre evidence a claim completeness. |
| condition multiplicity | DEFER | Vyžaduje property/context rule semantics. |
| `measurementQualityAllowed` | DEFER | Zbytočne by duplikovalo dnešnú schopnosť spotrebiteľských kontraktov. |
| `measurementQualityRequired` | DEFER | Meraná a deklarovaná hodnota nemajú rovnaké požiadavky. |
| permitted MQ fields | DEFER | Patrí budúcej metrologickej alebo method-aware politike. |
| `allowedVerificationStatuses` | REJECT | Claim workflow nie je property význam. |
| `classifications` / `classificationIds` | DEFER | Classification Catalog nie je implementovaný. |
| `sourceLinks` | REQUIRED NOW | Súčasť common metadata a provenance katalógového významu. |
| `status` | REQUIRED NOW | Record lifecycle katalógovej položky. |
| root `verificationStatus` | REJECT | Nesmie sa miešať lifecycle položky s verifikáciou claimu. |
| `aliases` | DEFER | Chýba typ, jazyk, externý systém a collision policy. |
| `notes` | OPTIONAL NOW | Neautoritatívny doplnok; nesmie niesť štruktúrovanú politiku. |
| `replaces` / `replacedBy` | OPTIONAL NOW | Konzistentné riadené PRP replacement odkazy. |

## 10. Name / Description

`name` je povinný, neprázdny, kanonický ľudsky čitateľný názov. Nie je identita, lookup key ani dôkaz rovnosti dvoch properties.

`description` je povinná neprázdna autoritatívna slovná definícia významu property. Je potrebná, pretože samotný názov, value type a unit allow-list nedokážu bezpečne odlíšiť významovo podobné properties. Text však nesmie nahradiť `allowedValueTypes`, `allowedUnitIds`, condition policy ani budúce strojovo spracovateľné pravidlá.

## 11. Allowed Value Types

Odporúča sa povinné pole `allowedValueTypes` ako neprázdne pole unikátnych hodnôt z uzavretého v1 enumu:

- `quantity`;
- `valueRange`.

Položka môže povoliť jednu alebo obe hodnotové formy. Poradie nemá prioritu ani fallback význam. Jeden konkrétny PropertyRecord alebo Observation naďalej obsahuje presne jednu vetvu zodpovedajúcu svojmu `valueType`.

Model jedného povinného typu by zbytočne rozdeľoval rovnaký property význam, ak je prípustný skalár aj interval. Model preferred type + fallback nemá prijatú semantiku. Bez obmedzenia by katalóg neplnil základnú kompatibilitnú úlohu. Textové, boolean a referenčné hodnoty sa vo v1 nepridávajú.

## 12. Unit Restriction Decision

V1 má obsahovať povinné `allowedUnitIds` ako neprázdny zoznam unikátnych `UNT-xxxxxx` odkazov. Dôvody:

- všetky aktuálne povolené hodnotové formy nesú jednotku;
- presný allow-list je overiteľný bez predstierania dimenzionálnej kompatibility;
- rovnaké pravidlo sa dá aplikovať na PropertyRecord aj Observation;
- chybná alebo nepovolená jednotka môže byť odmietnutá fail-closed.

Zoznam je presná whitelist politika, nie tvrdenie, že uvedené jednotky sú navzájom konvertibilné alebo rozmerovo ekvivalentné. Rozšírenie zoznamu je riadená revízia katalógovej položky. Tento model môže byť rigidný, ale je bezpečnejší než neoverená dimenzionálna inferencia a neskôr sa dá rozšíriť o samostatný quantity-kind/dimension model.

## 13. Canonical Unit Decision

`canonicalUnitId` sa vo v1 odkladá. Pole by mohlo znamenať normalizačnú jednotku, zobrazovaciu preferenciu alebo engineering reference unit; Accepted architektúra tento význam nerozlišuje. Bez conversion graphu nie je možné bezpečne zaručiť prevod z každej povolenej jednotky.

Presentation preference nepatrí do Property Catalog významu. Normalizačná jednotka môže vzniknúť až spolu s prijatou dimension/conversion semantikou.

## 14. Condition Policy

Condition Type Catalog vlastní význam CND a jeho základné hodnotové formy. Property Catalog smie vytvoriť užší property-specific profil, ale nesmie nanovo definovať CND.

V1 má voliteľne podporiť `allowedConditionTypeIds` ako neprázdny unikátny zoznam `CND-xxxxxx`. Rozhodnutie je fail-closed:

- ak pole chýba, property nepovoľuje Conditions;
- ak pole existuje, spotrebiteľ smie použiť iba uvedené CND;
- existencia, lifecycle použiteľnosť a kompatibilita konkrétnej Condition s CND sa kontrolujú katalógovo uvedomelo.

`requiredConditionTypeIds` sa vo v1 odkladá. Povinnosť môže znamenať štrukturálnu platnosť, úplnosť claimu, úplnosť evidence alebo podmienku povýšenia evidence; bez oddelenia týchto významov by jedno pole nesprávne spájalo PropertyRecord a Observation workflow.

`forbiddenConditionTypeIds` sa odmieta ako redundantné voči uzavretému allow-listu.

## 15. Condition Multiplicity

V1 nedefinuje minimum, maximum, uniqueness podľa CND ani logickú kombináciu Conditions. Existujúce polia `conditions` sú zoznamy bez autoritatívneho významu poradia.

Presná multiplicita vyžaduje rozhodnutie, či ide o intrinsic property pravidlo, evidence completeness, claim completeness alebo aplikačný kontext. Do vyriešenia sa Property Catalog nesmie správať ako rule engine.

## 16. MeasurementQuality Policy

V1 neobsahuje `measurementQualityAllowed`, `measurementQualityRequired` ani zoznam povolených MeasurementQuality polí.

MeasurementQuality opisuje kvalitu konkrétneho meraného, pozorovaného alebo reportovaného výsledku. Aktuálne ho môžu niesť PropertyRecord aj Observation. Jeho povinnosť závisí aj od metódy, pôvodu hodnoty a workflow, nie iba od abstraktného property významu. Boolean policy by preto vytvorila nejasnú väzbu a potenciálne odlišné potreby evidence a claimu.

Budúca policy musí rozlišovať measured, observed, declared a derived hodnoty a nesmie zamieňať measurement quality s výrobnou toleranciou.

## 17. Source Traceability

`sourceLinks` je povinné štrukturálne pole prevzaté zo spoločných metadát. Používa existujúci SourceLink kontrakt; Property Catalog nevytvára jeho lokálnu kópiu.

- `Draft` môže mať prázdne `sourceLinks`.
- `Review` a `Approved` položka s overiteľným technickým alebo normatívnym významom musí mať najmenej jeden zdroj podľa EOS aplikačnej validácie.
- Internal governance decision môže byť evidované podľa platných source/provenance pravidiel, ale nesmie sa zamieňať s externou normou.
- Zdroje katalógového významu nenahrádzajú zdroje konkrétneho PropertyRecord alebo Observation.

## 18. Lifecycle

Property Catalog Entry používa rovnaký record lifecycle a common metadata pattern ako Unit Catalog Entry a Condition Type Catalog Entry:

- `Draft`;
- `Review`;
- `Approved`;
- `Deprecated`;
- `Archived`.

Položka má vlastné `schemaVersion`, `recordVersion`, `revision`, auditné timestamps a actor fields, `changeSummary` a replacement väzby. Koreň nemá `verificationStatus`. `status` opisuje zrelosť katalógovej položky; `PropertyRecord.verificationStatus` opisuje konkrétne tvrdenie.

## 19. Classification Boundary

V1 neobsahuje `classifications` ani `classificationIds`. Classification Catalog ešte neexistuje a nie je určené, či klasifikácia property predstavuje taxonómiu, doménu použitia, externý kód alebo viac nezávislých systémov.

Odklad zabraňuje predčasnej cyklickej závislosti a nebráni neskoršiemu rozšíreniu Property Catalog Entry po prijatí Classification Catalog kontraktu.

## 20. Alias Model

Aliasy sa vo v1 odkladajú. Neexistuje prijaté pravidlo pre:

- alternatívny názov verzus historický názov;
- jazyk a lokalizáciu;
- externý systém a externý kód;
- case sensitivity a normalizáciu;
- kolízie medzi PRP položkami;
- presmerovanie aliasu po deprecácii.

Voľné textové aliases by oslabili autoritu PRP identity. Migráciu má dočasne riešiť explicitné mapovanie mimo autoritatívnej položky, kým nevznikne riadený alias contract.

## 21. Property Identity / Equivalence

Identita property je výlučne PRP ID. Názov, opis, unit allow-list ani value type neurčujú identitu.

Dve významovo podobné properties môžu zostať samostatnými PRP položkami, ak majú odlišný odborný význam, zdrojový kontext alebo governance históriu. Podobnosť, substituovateľnosť, širší/užší význam a ekvivalencia sú samostatné vzťahy a vo v1 sa nemodelujú.

## 22. Candidate Models

### Candidate A

Common metadata + `id`, `name`, `allowedValueTypes`.

- Minimality: vysoká.
- Semantic value: nedostatočná; nekontroluje jednotku a bez definície nevytvára bezpečne odlíšiteľný význam.
- Compatibility: iba value-branch kontrola.
- Migration cost: neskôr vyžaduje doplnenie jednotkovej politiky ku každej položke.
- Verdict: odmietnuť ako príliš slabý model.

### Candidate B

Common metadata + `id`, `name`, `description`, `allowedValueTypes`, `allowedUnitIds`.

- Minimality: dobrá.
- Semantic value: riadi dve dnes implementované osi kompatibility.
- Compatibility: rovnaká pre PropertyRecord aj Observation.
- Dependencies: iba Unit Catalog.
- Migration cost: nízky; dimension model môže neskôr doplniť alebo nahradiť explicitný allow-list.
- Verdict: bezpečné jadro v1.

### Candidate C

Candidate B + `allowedConditionTypeIds` + `requiredConditionTypeIds`.

- Semantic value: vysoká, ale required semantics nie je rozlíšená medzi evidence a claim completeness.
- Dependencies: Unit aj Condition Type Catalog.
- Overdesign risk: stredný až vysoký pri multiplicite, logike a required semantics.
- Verdict: neprijať celý model; prevziať iba voliteľný CND allow-list.

### Candidate D – odporúčaný

Candidate B + voliteľné `allowedConditionTypeIds`; voliteľne `notes`, `replaces`, `replacedBy`.

- Minimality: zachováva iba deterministicky overiteľné semantic constraints.
- Semantic value: value type, jednotka a povolené typy podmienok.
- Compatibility: rovnaký property profil pre PropertyRecord aj Observation bez zlúčenia ich lifecycle.
- Dependencies: jednosmerne na Unit a Condition Type Catalog.
- Migration cost: umožňuje neskôr pridať dimension, required conditions, MQ a classifications bez reinterpretácie existujúcich polí.
- Verdict: odporúčaný v1 model.

## 23. Recommended Minimal Model

Odporúčaný Property Catalog Entry v1 obsahuje:

```json
{
  "id": "PRP-xxxxxx",
  "schemaVersion": "...",
  "recordVersion": "...",
  "revision": 0,
  "status": "Draft",
  "createdAt": "...",
  "createdBy": "...",
  "updatedAt": "...",
  "updatedBy": "...",
  "sourceLinks": [],
  "changeSummary": "...",
  "name": "Fictional property name",
  "description": "Fictional property definition.",
  "allowedValueTypes": ["quantity"],
  "allowedUnitIds": ["UNT-xxxxxx"],
  "allowedConditionTypeIds": ["CND-xxxxxx"]
}
```

Príklad je iba tvar kontraktu. Nezakladá reálnu PRP, UNT ani CND položku a neobsahuje technické údaje.

`allowedConditionTypeIds` je voliteľné. `notes`, `replaces` a `replacedBy` sú voliteľné. Všetky ostatné zobrazené polia sú povinné.

## 24. Field Requirement Matrix

| Pole | V1 stav | Pravidlo |
| --- | --- | --- |
| `id` | REQUIRED | Centrálne `PRP-xxxxxx`. |
| `schemaVersion` | REQUIRED | Common metadata. |
| `recordVersion` | REQUIRED | Common metadata. |
| `revision` | REQUIRED | Nezáporné celé číslo. |
| `status` | REQUIRED | Existujúci RecordStatus. |
| `createdAt`, `updatedAt` | REQUIRED | Existujúci date-time contract. |
| `createdBy`, `updatedBy` | REQUIRED | Neprázdne actor hodnoty. |
| `sourceLinks` | REQUIRED | Draft môže byť prázdny; lifecycle source rule je aplikačné pravidlo. |
| `changeSummary` | REQUIRED | Neprázdne. |
| `name` | REQUIRED | Neprázdny kanonický názov; nie identita. |
| `description` | REQUIRED | Neprázdna autoritatívna slovná definícia. |
| `allowedValueTypes` | REQUIRED | 1 až 2 unikátne hodnoty: `quantity`, `valueRange`. |
| `allowedUnitIds` | REQUIRED | Neprázdne unique pole UNT odkazov. |
| `allowedConditionTypeIds` | OPTIONAL | Ak chýba, Conditions sú zakázané; inak neprázdne unique pole CND odkazov. |
| `notes` | OPTIONAL | Neautoritatívna poznámka. |
| `replaces`, `replacedBy` | OPTIONAL | PRP odkazy; integrita a lifecycle sa overia aplikačne. |
| `canonicalUnitId` | DEFERRED | Chýba conversion/dimension význam. |
| `requiredConditionTypeIds` | DEFERRED | Chýba evidence/claim completeness význam. |
| condition multiplicity | DEFERRED | Chýba rule semantics. |
| MQ policy | DEFERRED | Chýba origin/method-aware politika. |
| classifications | DEFERRED | Classification Catalog neexistuje. |
| aliases | DEFERRED | Chýba riadený alias model. |
| root `verificationStatus` | REJECTED | Patrí claimu alebo SourceLink, nie catalog lifecycle. |

## 25. Validation Responsibility

### JSON Schema structural validation

- uzavretý tvar objektu a required fields;
- PRP, UNT a CND formát cez centrálne `$ref`;
- common metadata, lifecycle enum a SourceLink tvar;
- neprázdny `name` a `description`;
- uzavretý, neprázdny a unique `allowedValueTypes`;
- neprázdny a unique `allowedUnitIds`;
- neprázdny a unique `allowedConditionTypeIds`, ak existuje;
- PRP formát replacement odkazov.

### Catalog-aware validation

- existencia a použiteľný lifecycle odkazovaných UNT a CND položiek;
- `PropertyRecord.valueType` a `Observation.valueType` sú povolené PRP položkou;
- konkrétny `unitId` patrí do `allowedUnitIds`;
- každé použité `conditionTypeId` patrí do `allowedConditionTypeIds`;
- Condition hodnota je kompatibilná s príslušným Condition Type Catalog Entry;
- deprecated/replaced catalog references sa používajú podľa governance.

### Reference integrity

- existencia referencovaného PRP pre PropertyRecord a Observation;
- existencia UNT a CND referencií z Property Catalog Entry;
- existencia a konzistencia `replaces`/`replacedBy` cieľov;
- existencia SRC cieľov v SourceLinks.

### PropertyRecord / Observation application validation

- aplikácia rovnakého PRP semantic profile na konkrétnu hodnotu;
- zachovanie oddelenia evidence a claim lifecycle;
- vnorené ValueRange a MeasurementQuality významové pravidlá;
- source lifecycle pravidlá podľa typu a stavu rodiča;
- budúce completeness a Decision pravidlá.

### Calculation Layer

- konverzia jednotiek;
- dimenzionálna kompatibilita a normalizácia;
- numerické porovnanie po explicitnej konverzii.

Property Catalog nesmie implementovať výpočty.

### Governance

- prijatie, deprecácia, archivácia a nahradenie katalógovej položky;
- zákaz tichej zmeny schváleného významu;
- pravidlá zdrojovej dohľadateľnosti a revízií.

## 26. Dependency Graph

Odporúčaná závislosť je acyklická:

```text
PropertyRecord -----> Property Catalog Entry -----> Unit Catalog Entry
       |                       |
       |                       +-------------------> Condition Type Catalog Entry
       +-----> Quantity / ValueRange / Condition

Observation -------> Property Catalog Entry
       +------------> Quantity / ValueRange / Condition
```

Unit Catalog Entry ani Condition Type Catalog Entry nereferencujú PRP. Property Catalog iba zužuje ich použitie a nanovo nedefinuje ich význam. Classification Catalog nie je do grafu v1 pridaný. Cyklická závislosť nevzniká.

## 27. Real Data Boundary

Tento review nevytvára žiadnu reálnu PRP položku ani technické hodnoty. Implementačný míľnik smie používať iba fiktívne fixture identifikátory, názvy a hodnoty na preukázanie kontraktu.

Populácia reálnych engineering properties patrí do samostatného source-reviewed míľnika po schválení schémy, provenance postupu a catalog-aware validácie.

## 28. Risks

| Riziko | Priorita | Opatrenie |
| --- | --- | --- |
| Property Catalog sa zmení na rule engine. | High | V1 obmedziť na enumy a ID allow-listy; logiku, multiplicitu a výpočty odložiť. |
| `allowedUnitIds` bude príliš rigidné. | High | Zdokumentovať exact whitelist význam; rozšírenie robiť revíziou a neskôr pridať dimension model. |
| Canonical unit začne implicitne znamenať konverziu. | High | Pole vo v1 nepridať. |
| Required Conditions nesprávne zlúčia evidence a claim completeness. | High | `requiredConditionTypeIds` odložiť. |
| Význam sa rozdelí medzi voľný text a štruktúrované polia. | High | Vyžadovať definíciu, ale kompatibilitu riadiť iba štruktúrovanými poľami. |
| Unit alebo Condition význam sa zdvojí v Property Catalogu. | High | Referencovať UNT/CND; nenahrádzať ich definície lokálnym textom. |
| Lifecycle sa zamení s claim verification. | High | Zakázať root `verificationStatus`. |
| Neriadené aliasy vytvoria druhú identitu. | Medium | Aliasy odložiť do riadeného modelu. |
| Názov alebo jednotka sa použije ako property identity. | High | Identita je iba PRP. |
| Budúce nenumerické formy si vyžiadajú migráciu. | Medium | Uzavrieť v1 na implementované formy; rozšírenie vykonať verziovanou zmenou. |
| Optional condition allow-list bude nesprávne interpretovaný. | Medium | Explicitne stanoviť: neprítomnosť znamená, že Conditions nie sú povolené. |
| Deprecated UNT/CND zostanú v aktívnej PRP položke. | Medium | Catalog-aware lifecycle kontrola a governance review. |

## 29. Deferred Concepts

Odložené sú:

- quantity kind, dimension a rozmerová kompatibilita;
- conversion graph, normalizácia a canonical unit;
- property domain taxonomy;
- required/recommended Conditions;
- Condition multiplicita, poradie, logická kombinácia a evaluation-mode policy;
- MeasurementQuality allowed/required/method-aware politika;
- Classification Catalog väzby;
- aliases, lokalizácia a externé property kódy;
- property equivalence, broader/narrower a substitution relationships;
- pravidlá automatickej porovnateľnosti;
- domain ranges a engineering limity;
- nenumerické property value forms;
- reálne PRP catalog data;
- catalog-aware integračná implementácia pre PropertyRecord a Observation.

## 30. Implementation Preconditions

Implementácia Property Catalog Entry v1 môže začať, ak dodrží tieto podmienky:

1. Property Catalog zostane Knowledge Catalog a položka samostatný Catalog Entry Aggregate Root.
2. Koreň použije `id` vo formáte PRP a rovnaký common metadata pattern ako existujúce katalógy.
3. `name` a `description` budú povinné a neprázdne; nebudú určovať identitu.
4. `allowedValueTypes` bude neprázdny unique zoznam iba `quantity` a `valueRange`.
5. `allowedUnitIds` bude povinný neprázdny unique UNT allow-list bez dimension alebo conversion inferencie.
6. `allowedConditionTypeIds` bude voliteľný neprázdny unique CND allow-list; neprítomnosť bude znamenať zákaz Conditions.
7. Required Conditions, multiplicita a rule semantics nebudú súčasťou v1.
8. Canonical unit a MeasurementQuality policy nebudú súčasťou v1.
9. Root nebude mať `verificationStatus`, classifications ani aliases.
10. Lifecycle, provenance a replacement fields znovu použijú existujúce kontrakty.
11. Schema a fixture dáta budú iba fiktívne; nevznikne reálny PRP katalógový obsah.
12. Catalog-aware kontroly budú jasne oddelené od štrukturálnej schémy; ak sa v implementačnom míľniku ešte nevytvoria, budú explicitne označené ako následný integračný krok.
13. Existing PropertyRecord, Observation, Unit Catalog Entry a Condition Type Catalog Entry sa významovo nezmenia.

## 31. Readiness Verdict

Property Catalog Entry v1 je možné implementovať bez opravy Accepted architektúry. Rola Knowledge Catalogu, PRP identita, aggregate boundary, aktuálne hodnotové formy a jednosmerné katalógové závislosti sú dostatočne jasné.

Implementácia je bezpečná iba pri explicitnom obmedzení na presné value-type, UNT a voliteľné CND allow-listy. Required Conditions, multiplicita, canonical unit, dimension/conversion, MeasurementQuality policy, classifications, aliases a equivalence zostávajú odložené. Samotná entry schéma nebude dokazovať existenciu referencií ani kompatibilitu konkrétneho PropertyRecord alebo Observation; to zostane catalog-aware aplikačnej validácii.

## 32. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-09-24 | 0.1 | 0 | Codex | Initial pre-design review of Property Catalog role, PRP identity, value-type, unit and condition policy, lifecycle, dependencies and implementation readiness. |

READY WITH CONDITIONS
