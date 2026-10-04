# CDR-0013 Catalog-aware / Reference-integrity Integration Pre-design Review

Project: EOS – Engineering Operating System  
Contract Review ID: CDR-0013  
Review: Catalog-aware / Reference-integrity Integration  
Review type: Pre-design  
Phase: 0.2B.2.5
Version: 0.1  
Revision: 1
Status: Review  
Document basis: Accepted EOS architecture + four implemented catalog contracts

## 1. Purpose

Definovať najmenšiu bezpečnú integračnú architektúru, ktorá rozšíri dnešnú štrukturálnu a aplikačnú validáciu EOS o overenie existencie katalógových cieľov a o významovú kompatibilitu s načítanými katalógovými položkami. Review oddeľuje JSON Schema od runtime dát, stanovuje hranice validačných vrstiev a pripravuje implementáciu bez databázy, reálnych katalógových dát alebo zmien Accepted architektúry.

## 2. Scope

Review pokrýva:

- katalógové referencie `UNT-xxxxxx`, `CND-xxxxxx`, `PRP-xxxxxx` a `CLS-xxxxxx`;
- Quantity, ValueRange, MeasurementQuality, Condition, PropertyRecord, Observation a Classification;
- in-memory dodanie štyroch typov katalógových položiek;
- existenciu, typ, lifecycle použiteľnosť a významovú kompatibilitu;
- error model, JSON paths, poradie kontrol a dependency-aware potláčanie chýb;
- spätne kompatibilné rozšírenie verejného API validátora;
- testovaciu stratégiu bez produkčnej populácie katalógov;
- kritériá ukončenia Phase 0.2B.2.

Mimo rozsahu sú implementácia validačného kontextu alebo registry, všeobecné entity resolution, databáza, persistence, workflow engine, reálne katalógové dáta, konverzie, dimenzionálna kompatibilita, nové schémy, ADR, RFC a zmeny governance.

## 3. Reviewed Artifacts

Preskúmané boli:

- `AGENTS.md` a pravidlá `EOS-000`;
- `EOS-003_Identification_and_Versioning.md`;
- `EOS-006_Data_Validation_Standard.md`;
- `EOS-007_Validation_Capability_Matrix.md`;
- Accepted `RFC-0001_Engineering_Property_Model.md`;
- Accepted `RFC-0002_Engineering_Object_Taxonomy.md`;
- Accepted `RFC-0003_EOS_Engineering_Glossary.md`;
- Accepted `ADR-0015_Establish_engineering_knowledge_layer.md`;
- Accepted `ADR-0016_Treat_observation_as_first_class_evidence_entity.md`;
- `CDR-0008` až `CDR-0012`;
- sedem Knowledge Core schém;
- štyri katalógové schémy a spoločné kontrakty;
- `schema_loader.py`, `validator.py`, `cli.py` a verejný validačný modul;
- aktuálne testy, fixtures a validačná dokumentácia;
- `CHANGELOG.md`, `ROADMAP.md` a `BACKLOG.md`.

Pre-flight bol vykonaný na čistej vetve `feature/phase-0.2b-knowledge-contracts` a HEAD `3992d8f`. Existuje 20 schém, z toho 7 Knowledge Core a 4 katalógové. Kompletných 182 testov prešlo. Catalog-aware validácia, runtime catalog registry, storage layer, reálne katalógové položky ani implementácia 0.2C neexistujú.

## 4. Current Validation Architecture

Aktuálny `EosValidator` vykonáva:

1. načítanie a kontrolu JSON;
2. kontrolu schémy cez `Draft202012Validator` a `FormatChecker`;
3. existujúce EOS aplikačné pravidlá;
4. kompozičné spúšťanie pravidiel pre vnorené Knowledge Core kontrakty;
5. zber chýb do jednotného `ValidationResult`.

Existujúci error model obsahuje `errorCode`, `category`, `message`, `instancePath`, `schemaPath`, `recordId` a `severity`. Kategória `reference_integrity` sa dnes používa na hierarchickú konzistenciu JOB identifikátorov, nie na runtime rozlíšenie katalógových cieľov.

`SchemaRegistry` je registry schém a `$ref` zdrojov. Nesmie sa rozšíriť na registry dátových záznamov; JSON Schema registry a Catalog Registry majú odlišné vlastníctvo aj lifecycle.

## 5. Validation Layer Boundaries

| Vrstva | Zodpovednosť | Príklady | Nezodpovedá za |
| --- | --- | --- | --- |
| `schema_validation` | Lokálny serializačný kontrakt bez runtime dát. | Typ, required, enum, `PRP` pattern, `additionalProperties`. | Existenciu ID, katalógovú kompatibilitu, workflow. |
| `application_validation` | Významové invarianty jedného záznamu alebo jeho vnorených value objects. | Konečné čísla, poradie ValueRange, kladná resolution, source lifecycle pravidlo. | Lookup cieľov, katalógové allow-listy. |
| `reference_integrity` | Jednoznačné rozlíšenie referencie na existujúci cieľ očakávaného typu. | PRP/UNT/CND/CLS existuje, ID nie je duplicitné, target kind sedí. | Lifecycle použiteľnosť a semantic compatibility. |
| `catalog_validation` | Významová kompatibilita použitia s už rozlíšenou katalógovou položkou. | Povolený value type, unit, Condition form, CND allow-list a lifecycle policy. | JSON tvar, persistence transakcie, schvaľovací workflow. |
| Workflow/governance validácia | Povolené prechody, schvaľovanie, deprecácia a oprávnenia. | Kto môže schváliť entry, zákaz tichej zmeny Approved významu. | Serializáciu a bežný lookup. |
| Persistence validácia | Úložiskové a transakčné invarianty. | Unique key v databáze, optimistic locking, transakčný zápis. | Význam property alebo Condition. |

Klasifikácia príkladov:

- malformed PRP ID: `schema_validation`;
- well-formed PRP, ktorý neexistuje: `reference_integrity`;
- PRP nepovoľuje Quantity: `catalog_validation`;
- PRP nepovoľuje použité UNT: `catalog_validation`;
- CND alebo CLS neexistuje: `reference_integrity`;
- CND nepovoľuje hodnotovú formu: `catalog_validation`;
- Observation subject je formátovo správny, ale neexistuje: budúca entity `reference_integrity`, mimo 0.2B.2;
- Approved Catalog Entry bez provenance: existujúce `application_validation` source pravidlo;
- referencia na Deprecated entry: rozlíši sa, potom ju vyhodnotí `catalog_validation` podľa explicitnej policy.

## 6. Reference Integrity Definition

`reference_integrity` v rozsahu 0.2B.2 znamená, že:

1. referenčné ID sa nachádza v dodanom katalógovom snapshot-e;
2. ID rozlíši práve jednu položku;
3. položka patrí do očakávaného katalógového typu.

Reference integrity nekontroluje, či cieľ povoľuje konkrétnu hodnotovú formu, jednotku, Condition alebo lifecycle použitie. Nekontroluje pravdivosť dát, workflow ani automatickú migráciu na nástupcu.

Rozsah v1 je zámerne katalógový. Existencia `OBS`, `JOB`, `MAT`, `MAC`, `SRC` a ďalších entity referencií zostáva odložená, kým neexistuje príslušný entity resolver alebo autoritatívne repository. Platná katalogová referencia sa nesmie vydávať za dôkaz integrity všetkých referencií v zázname.

## 7. Catalog Validation Definition

`catalog_validation` začína až po úspešnom rozlíšení cieľa. Kontroluje, či je konkrétne použitie kompatibilné so strojovo čitateľnými pravidlami resolved entry a s explicitnou lifecycle policy.

V1 zahŕňa:

- `PropertyCatalogEntry.allowedValueTypes`;
- `PropertyCatalogEntry.allowedUnitIds`;
- neprítomnosť alebo obsah `allowedConditionTypeIds`;
- `ConditionTypeCatalogEntry.allowedValueForms`;
- `allowedReferencePrefixes` pri Condition `referenceId`;
- lifecycle použiteľnosť UNT/CND/PRP/CLS;
- upozornenie na Deprecated cieľ.

Nevykonáva dimension inference, conversion, required Conditions, multiplicitu, classification applicability, system/code mapping ani equivalence.

## 8. Quantity Integration

Quantity je vlastníkom svojej `unitId` referencie a pri catalog-aware validácii musí sama spustiť UNT lookup. Rovnaké pravidlo platí pre ValueRange a pre Quantity vnorené v MeasurementQuality, Condition, PropertyRecord alebo Observation.

Rozdelenie:

- formát `unitId`: `schema_validation`;
- existencia a Unit Catalog typ: `reference_integrity` na `$.unitId`;
- lifecycle použiteľnosť Unit Catalog Entry: `catalog_validation` na `$.unitId`;
- property-specific povolenie jednotky: kontroluje až rodičovský property compatibility helper na ceste k jeho result unit.

Quantity nekontroluje dimenziu, konverziu ani symbol. Parent-only vlastníctvo UNT lookupu sa odmieta, pretože by pri samostatnej alebo hlboko vnorenej Quantity vytváralo nekonzistentné správanie.

## 9. Condition Integration

Condition má reusable nested semantic validator. Určí aktívnu hodnotovú formu z existujúceho unionu a vykoná:

1. CND lookup na `conditionTypeId` ako `reference_integrity`;
2. lifecycle policy CND ako `catalog_validation`;
3. členstvo aktívnej formy v `allowedValueForms` ako `catalog_validation`;
4. pri `referenceId` členstvo skutočného ID prefixu v `allowedReferencePrefixes` ako `catalog_validation`;
5. pri Quantity alebo ValueRange vnorenú UNT existenciu cez ich vlastný reusable validator.

`evaluationMode` zostáva iba schema enumom. Unit restriction, multiplicita, duplicate Conditions a logické kombinácie sa nekontrolujú, pretože Condition Type Catalog v1 ich nemodeluje.

Ak `referenceId` smeruje na UNT alebo CND, katalogový resolver môže v rámci dostupných katalógov overiť jeho existenciu. Existencia ostatných povolených prefixov zostáva explicitne neoverená do zavedenia entity resolvera; prefix compatibility sa napriek tomu kontroluje.

## 10. PropertyRecord Integration

PropertyRecord používa spoločnú property compatibility funkciu s týmito krokmi:

1. PRP existencia a typ: `reference_integrity` na `$.propertyId`;
2. lifecycle PRP: `catalog_validation` na `$.propertyId`;
3. `valueType` je v `allowedValueTypes`: `catalog_validation` na `$.valueType`;
4. výsledný `quantity.unitId` alebo `valueRange.unitId` je v `allowedUnitIds`: `catalog_validation` na príslušnej `unitId` ceste;
5. ak `allowedConditionTypeIds` chýba, neprázdne `conditions` sú zakázané;
6. ak allow-list existuje, každý `conditionTypeId` v ňom musí byť;
7. každá Condition sa nezávisle validuje proti vlastnej CND položke.

MeasurementQuality quantity jednotky nepodliehajú `PropertyCatalogEntry.allowedUnitIds`; tento allow-list patrí meranej property hodnote, nie metrologickej neistote alebo rozlíšeniu. Ich UNT existencia sa však overí cez vlastný Quantity validator.

Duplicate Conditions sa vo v1 nekontrolujú. Katalóg nemodeluje multiplicitu, uniqueness scope ani kombinácie.

## 11. Observation Integration

Observation používa rovnaký shared property compatibility helper ako PropertyRecord. Mapuje svoje `propertyId`, `valueType`, výslednú Quantity/ValueRange a `conditions` na spoločný vstup bez duplikácie pravidiel.

Observation-specific zostáva evidence lifecycle, `subjectId`, `observationScope`, `observedAt`, provenance a budúca subject/scope integrita. Property compatibility nesmie meniť Observation na claim ani miešať evidence approval s katalógovým lifecycle.

Rozdiel vo root JSON paths dodáva caller helperu cez explicitný path context. Samotné compatibility pravidlá sú identické.

## 12. Classification Integration

Embedded Classification vo v1 vyžaduje:

- existujúce CLS správneho katalógového typu ako `reference_integrity` na `$.classificationId`;
- lifecycle použiteľnosť resolved Classification Catalog Entry ako `catalog_validation` na rovnakej ceste.

Nevynucuje sa target applicability, classification system, external code, hierarchy, equivalence, assignment multiplicity ani odvodená povinnosť assignment `sourceLinks`. Definition provenance entry a assignment provenance value objectu zostávajú oddelené.

Kontrola má byť reusable od začiatku, aby ju budúce entity mohli volať s vlastnou základnou cestou bez kopírovania logiky.

## 13. Catalog Lifecycle Policy

Catalog Registry musí rozlíšiť každú existujúcu položku bez ohľadu na status. Lifecycle nie je súčasťou existence/type resolution.

Odporúčaná default policy pre nové plné použitie:

| Status | Resolution | Default catalog-validation výsledok |
| --- | --- | --- |
| `Draft` | Áno | Error; povoliť iba explicitnou authoring policy. |
| `Review` | Áno | Error; povoliť iba explicitnou authoring policy. |
| `Approved` | Áno | Povolené. |
| `Deprecated` | Áno | Povolené s warning; uviesť `replacedBy`, ak existuje. |
| `Archived` | Áno | Error pre nové použitie; historické čítanie môže mať explicitnú policy. |

Nezavádza sa pojem runtime environment. `ValidationContext` nesie explicitnú a viditeľnú policy povolených statusov a severity pre Deprecated. Žiadna lifecycle policy nesmie byť skrytý globálny stav.

## 14. Supersession Policy

`replaces` a `replacedBy` nemenia identitu ani samy osebe nerobia odkaz neplatným.

- Deprecated entry sa naďalej rozlíši a defaultne vytvorí warning;
- `replacedBy` sa môže uviesť v správe ako odporúčaný nástupca;
- automatická migrácia, tiché prepísanie ID a automatické nasledovanie replacement reťazca sú zakázané;
- Archived entry defaultne nie je použiteľná pre nový záznam;
- existencia a očakávaný typ replacement cieľa patria do `reference_integrity` registry snapshotu;
- self-reference, obojsmerná konzistencia a cykly patria do budúcej catalog/governance integrity kontroly a nemusia blokovať prvý consumer-integration krok.

## 15. Validation Context

Explicitný `ValidationContext` je pred implementáciou plnej katalogovej validácie povinný. Má byť immutable pre jeden validačný beh a obsahovať:

- catalog resolver/registry snapshot;
- explicitnú lifecycle policy;
- budúce rozšíriteľné validačné voľby bez globálneho stavu.

Nemá obsahovať databázové spojenie, mutable workflow stav, conversion engine ani user session. Rovnaký instance a rovnaký context musia viesť k deterministickému výsledku.

## 16. Catalog Registry

Je potrebný jeden reusable in-memory `CatalogRegistry`, ktorý interne používa štyri typované mapy pre UNT, CND, PRP a CLS. Jeden koordinujúci objekt je vhodnejší než štyri nesúvisiace registry, pretože poskytuje jednotnú duplicate-ID kontrolu a jednotné resolver API, ale nesmie sa zmeniť na neoznačený `dict[str, Any]`.

Zodpovednosti:

- prijať už načítané a štrukturálne platné katalógové entry objekty;
- registrovať ich podľa stabilného ID a očakávaného typu;
- fail-closed odmietnuť duplicate ID;
- rozlíšiť ID na presne jednu typovanú položku;
- sprístupniť lifecycle a machine-readable v1 policy fields;
- po zostavení fungovať ako immutable snapshot.

Registry nesmie čítať databázu, vlastniť persistence, mutovať entries, vykonávať workflow, konverzie alebo samotnú consumer compatibility.

## 17. Reference Resolver

V1 sa odporúča malý catalog resolver contract implementovaný `CatalogRegistry`, nie všeobecný `ReferenceResolver`.

Generic resolver pre OBS/JOB/MAT/MAC/SRC a ďalšie budúce entity by pred 0.2C musel vymyslieť repository, typový register, not-found semantics a storage hranice. To je predčasné. `ValidationContext` môže neskôr prijať všeobecnejší resolver bez zmeny katalogových pravidiel, ak vzniknú autoritatívne entity repositories.

## 18. Real Data Boundary

Implementácia catalog-aware validácie nevyžaduje reálne engineering catalog dáta.

Testy majú zostaviť izolovaný in-memory registry z fiktívnych entry objektov umiestnených výhradne v test fixtures alebo priamo v test builderoch. Testovacie entries:

- nesmú byť načítané automaticky produkčným kódom;
- nesmú sa exportovať ako EOS catalog population;
- musia používať zjavne fiktívne názvy, hodnoty a ID;
- smú dokazovať iba správanie kontraktu.

Reálna populácia Unit, Condition Type, Property a Classification katalógov zostáva samostatným source-reviewed míľnikom.

## 19. Error Model

Existujúci `ValidationError` sa má zachovať. Pre integráciu sa odporúča voliteľné `referencedId`, aby strojový report nemusel parsovať ID zo správy. Ide o kompatibilné rozšírenie, nie nový error model.

Odporúčané kódy:

| Kód | Kategória | Význam |
| --- | --- | --- |
| `reference_integrity.reference_not_found` | `reference_integrity` | ID v registry neexistuje. |
| `reference_integrity.reference_type_mismatch` | `reference_integrity` | ID sa rozlíšilo na iný katalógový typ. |
| `reference_integrity.duplicate_identifier` | `reference_integrity` | Registry input obsahuje duplicate stable ID. |
| `catalog_validation.value_type_not_allowed` | `catalog_validation` | PRP nepovoľuje použitý value type. |
| `catalog_validation.unit_not_allowed` | `catalog_validation` | PRP nepovoľuje výsledné UNT. |
| `catalog_validation.condition_not_allowed` | `catalog_validation` | PRP nepovoľuje Conditions alebo konkrétne CND. |
| `catalog_validation.condition_value_form_not_allowed` | `catalog_validation` | CND nepovoľuje aktívnu hodnotovú formu. |
| `catalog_validation.reference_prefix_not_allowed` | `catalog_validation` | CND nepovoľuje prefix Condition reference. |
| `catalog_validation.catalog_status_not_allowed` | `catalog_validation` | Entry status nie je povolený context policy. |
| `catalog_validation.deprecated_reference` | `catalog_validation` | Deprecated cieľ sa použil; default severity `warning`. |

Kódy zachovávajú existujúcu lower-snake convention. `schemaPath` zostáva pri týchto chybách prázdny; `recordId` označuje validovaný root záznam a `referencedId` cieľ.

## 20. Error Path Rules

Chyba má smerovať na referenciu alebo hodnotu, ktorú používateľ môže opraviť:

| Chyba | Cesta |
| --- | --- |
| PRP chýba alebo má nepovolený lifecycle | `$.propertyId` |
| Property value type nie je povolený | `$.valueType` |
| Property unit nie je povolená | `$.quantity.unitId` alebo `$.valueRange.unitId` |
| Samostatné UNT neexistuje | cesta konkrétneho `unitId` |
| CND chýba | `$.conditionTypeId` alebo `$.conditions[i].conditionTypeId` |
| CND value form nie je povolená | cesta aktívnej hodnotovej vetvy, napr. `$.conditions[i].quantity` |
| Condition nie je povolená PRP | `$.conditions[i].conditionTypeId` |
| Reference prefix nie je povolený | `$.conditions[i].referenceId` |
| CLS chýba alebo lifecycle nie je povolený | `$.classificationId` |
| Duplicate registry ID | cesta `$.id` v označenom registry inpute, ak je dostupná; inak `$` s ID v `referencedId`. |

Observation používa rovnaké relative paths pod vlastným rootom. Vnorené helpery vždy prijímajú base path a nesmú stratiť index poľa.

## 21. Validation Order

Odporúčané poradie:

1. JSON syntax a schema definition;
2. `schema_validation`;
3. existujúce `application_validation` invarianty;
4. `reference_integrity` pre dostupné katalógové ID;
5. `catalog_validation` iba pre úspešne resolved targets;
6. workflow/governance kontrola v samostatnom caller kontexte;
7. persistence kontrola pri ukladaní.

Catalog/reference vrstvy sa nesmú spustiť pre kontrakt alebo podstrom, ktorý neprešiel štrukturálnou validáciou. Inak by napríklad číslo namiesto `propertyId` vytvorilo zároveň schema aj zavádzajúci not-found error. Workflow a persistence nie sú súčasťou bežného `EosValidator` consumer passu.

## 22. Error Accumulation

Odporúča sa hybridný dependency-aware zber:

- ak JSON alebo schema definition nemožno načítať, validácia skončí fail-fast;
- schema errors sa zhromaždia podľa dnešného modelu;
- po úspešnej štruktúre sa zhromaždia nezávislé application, reference a catalog errors;
- chyba nadradenej referencie potlačí iba kontroly, ktoré od resolved cieľa závisia;
- nezávislé vetvy sa validujú ďalej.

Ak PRP neexistuje, nehlási sa zároveň `value_type_not_allowed`, `unit_not_allowed` ani property condition allow-list. Vnorené Quantity UNT a Condition CND referencie sa však môžu kontrolovať, pretože sú od PRP lookupu nezávislé. Ak CND neexistuje, nehlási sa value-form ani prefix compatibility pre tú Condition.

## 23. Dependency Graph

```text
MeasurementQuality --> Quantity ------------------------> Unit Catalog Entry
ValueRange ---------------------------------------------> Unit Catalog Entry

Condition ----------> Condition Type Catalog Entry
    |                 +-- allowedReferencePrefixes
    +---------------> Quantity / ValueRange ------------> Unit Catalog Entry

PropertyRecord -----> Property Catalog Entry
    |                 +-------------------------------> Unit Catalog Entry
    |                 +-------------------------------> Condition Type Catalog Entry
    +---------------> Quantity / ValueRange / MeasurementQuality / Condition

Observation --------> Property Catalog Entry
    |                 +-------------------------------> Unit Catalog Entry
    |                 +-------------------------------> Condition Type Catalog Entry
    +---------------> Quantity / ValueRange / MeasurementQuality / Condition

Classification -----> Classification Catalog Entry
```

Katalógové entries nereferencujú consumer value objects. Property Catalog jednosmerne zužuje Unit a Condition Type použitie. Classification Catalog je nezávislý. Graf je acyklický.

## 24. Property Compatibility Reuse

PropertyRecord a Observation musia volať jednu shared semantic funkciu, konceptuálne `validate_property_value_against_catalog`.

Vstup má byť malý normalizovaný view:

- `propertyId`;
- `valueType`;
- result `unitId`;
- zoznam Conditions;
- base paths pre property, value type, unit a conditions;
- `ValidationContext`.

Helper nemá poznať claim/evidence lifecycle ani celé Python typy rodičov. Caller zodpovedá za extrakciu view a paths. Tým sa zachová identické správanie bez coupling PropertyRecord a Observation.

## 25. Condition Validation Reuse

Jedna reusable Condition semantic funkcia má validovať samostatnú aj vnorenú Condition. Prijíma Condition objekt, base path a context; rozlíši aktívnu formu, CND a prefix policy a deleguje vnorené Quantity/ValueRange pravidlá.

Parent Property helper vykonáva navyše iba PRP allow-list kontrolu. CND compatibility sa nekopíruje do PropertyRecord ani Observation. Pole index zostáva súčasťou base path.

## 26. Classification Validation Reuse

Reusable Classification semantic funkcia overí CLS existenciu, typ a lifecycle policy. Neobsahuje entity applicability ani assignment workflow. Budúce entity ju budú môcť volať s vlastným base path bez zmeny Classification kontraktu.

## 27. Validator API

Existujúce `validate(instance, schema_id, ...)` a `validate_json_file(...)` musia zostať spätne kompatibilné a naďalej znamenať contract validation: JSON Schema plus dnešné application rules.

Plná catalog-aware validácia má mať explicitný entry point, odporúčane:

```text
validate_with_context(instance, schema_id, context, ...)
validate_json_file_with_context(path, schema_id, context, ...)
```

Tento entry point najprv použije existujúci contract pass a potom pridá reference/catalog vrstvy. Samostatný názov zabraňuje tomu, aby neprítomný optional parameter potichu znamenal neúplnú „full“ validáciu. Existujúce API sa nerozbije a jeho výsledok sa nesmie označiť ako catalog-aware.

## 28. Missing Context Behavior

Bez contextu je povolená iba dnešná contract validation. Jej úspech znamená štrukturálne a lokálne aplikačne platný záznam, nie referenčne alebo katalógovo platný záznam.

Catalog-aware entry point musí `ValidationContext` vyžadovať. Chýbajúci alebo neúplný registry nesmie viesť k preskočeniu kontrol a výsledku `ok`; ide o explicitnú validačnú konfiguračnú chybu a volanie musí fail-closed pred catalog passom. CLI alebo iný caller musí rozlíšiť contract-only a catalog-aware režim vo svojom rozhraní a reporte.

## 29. Validation Levels

Formálny päťhodnotový enum `STRUCTURAL / SEMANTIC / REFERENCE_INTEGRITY / CATALOG_AWARE / FULL` sa teraz neodporúča. Vrstvy nie sú úplne nezávislé a enum by umožnil nezmyselné kombinácie, napríklad compatibility bez resolution.

Pre v1 stačia dve explicitné capabilities:

- contract validation: schema + existujúce application rules;
- catalog-aware validation: contract validation + catalog reference integrity + catalog compatibility.

Workflow/governance a persistence zostávajú samostatné operácie. Ak neskôr vznikne viac resolverov alebo validácií, capability model sa môže zaviesť samostatným review.

## 30. Duplicate ID Handling

JSON Schema nevie zistiť duplicate ID medzi súbormi. CatalogRegistry construction musí pred validáciou consumerov deterministicky odmietnuť:

- dve entries s rovnakým stable ID;
- jednu entry registrovanú pod typom, ktorý nezodpovedá ID rodine;
- nejednoznačné rozlíšenie.

Registry sa pri chybe nevytvorí čiastočne. Chyba používa `reference_integrity.duplicate_identifier`, obsahuje ID a podľa možnosti pôvod oboch vstupov. Databázový unique constraint môže neskôr pravidlo podporiť, ale nie je podmienkou in-memory testov.

## 31. Test Strategy

Budúci implementačný míľnik má použiť `unittest` a fiktívny test registry. Minimálne prípady:

- Quantity a ValueRange: UNT existuje/neexistuje, lifecycle policy;
- MeasurementQuality: vnorené UNT sa validuje s úplnou cestou;
- Condition: CND existuje/neexistuje, povolená/nepovolená forma, allowed/disallowed reference prefix, vnorené UNT;
- PropertyRecord: PRP existuje/neexistuje, allowed/disallowed value type, unit a Condition; Conditions zakázané pri chýbajúcom allow-liste;
- Observation: rovnaké property compatibility prípady a identické kódy s vlastnými paths;
- Classification: CLS existuje/neexistuje a lifecycle policy;
- Registry: duplicate ID, wrong type, immutable snapshot;
- API: contract validation bez contextu zostane kompatibilná; catalog-aware entry point bez contextu fail-closed;
- Lifecycle: Approved povolené, Draft/Review podľa explicitnej authoring policy, Deprecated warning, Archived default error;
- Dependency suppression: missing PRP nevytvorí odvodené compatibility errors;
- index/nested paths zostanú úplné;
- všetkých 182 existujúcich testov zostane úspešných.

Fiktívne katalógy majú byť vytvorené iba v test scope a nesmú byť dostupné ako produkčný catalog dataset.

## 32. Phase 0.2B.2 Completion Criteria

Phase 0.2B.2 možno označiť ako COMPLETE až keď platí všetko:

1. všetky štyri katalógové kontrakty sú implementované a validné;
2. existuje explicitný immutable ValidationContext a typed CatalogRegistry snapshot;
3. duplicate catalog IDs fail-closed;
4. UNT, CND, PRP a CLS existencia a typ sa kontrolujú ako `reference_integrity`;
5. lifecycle policy je explicitná, testovaná a nie je globálna;
6. Quantity/ValueRange a nested Quantity používajú UNT resolution;
7. Condition používa CND value-form a reference-prefix policy;
8. PropertyRecord a Observation zdieľajú PRP value-type/unit/condition compatibility;
9. Classification používa reusable CLS validation;
10. error categories, codes a paths sú testované;
11. dependency-aware suppression zabraňuje kaskádovým nezmyselným chybám;
12. contract-only API zostáva spätne kompatibilné a full validation bez contextu sa nevydáva za úspešnú;
13. všetky integračné a regresné testy prechádzajú;
14. implementačný výsledok a vedomé limity sú zdokumentované;
15. reálne engineering catalog dáta nie sú podmienkou dokončenia.

Entity reference resolution, SourceReference repository a reálna catalog population nie sú completion criteria 0.2B.2.

## 33. Risks

| Riziko | Priorita | Opatrenie |
| --- | --- | --- |
| JSON Schema začne vykonávať data lookup. | Critical | Lookup výlučne po schema/application passe v context-aware vrstve. |
| Chýbajúci registry sa potichu preskočí. | Critical | Samostatný context-aware entry point; context je povinný a fail-closed. |
| Existence a compatibility sa zmiešajú. | High | Oddelené kategórie, resolver a semantic helpery. |
| PropertyRecord a Observation dostanú rozdielne pravidlá. | High | Jeden normalizovaný property compatibility helper. |
| Condition pravidlá sa skopírujú do rodičov. | High | Reusable nested Condition validator s base path. |
| Registry sa zmení na persistence layer. | High | Prijíma už načítané objekty a je immutable; žiadne I/O ani workflow. |
| Generic resolver predčasne navrhne 0.2C repositories. | High | V1 iba catalog resolver; entity resolution deferred. |
| Lifecycle policy bude hidden global state. | High | Policy je povinná súčasť contextu. |
| Fixtures sa začnú používať ako reálne katalógy. | Critical | Test-only umiestnenie, explicitne fiktívne dáta, žiadny production loader. |
| Missing target vyvolá kaskádu compatibility chýb. | High | Dependency-aware suppression podľa resolved targetu. |
| Chybové paths sa pri vnorení stratia. | High | Každý helper prijíma base path a zachováva indexy. |
| Deprecated entry sa ticho prepíše nástupcom. | High | Iba warning s návrhom; žiadna automatická migrácia. |
| Parent property allow-list sa omylom aplikuje na MeasurementQuality. | High | PRP unit policy iba na hlavnú result vetvu. |
| Neoverené entity referencie sa vydajú za úplnú integritu. | Critical | Reportovať presný catalog-only scope; entity resolver odložiť. |

## 34. Deferred Concepts

Odložené sú:

- generic ReferenceResolver pre OBS/JOB/MAT/MAC/SRC a ďalšie entities;
- Observation subject a scope target existence;
- SourceReference repository a `sourceReferenceId` existence;
- databázová a cross-repository referenčná integrita;
- persistence adapter a catalog loader;
- conversion, dimension, quantity kind a unit equivalence;
- Condition unit policy, multiplicita, duplicate a logical-combination pravidlá;
- required Conditions a MeasurementQuality policy podľa PRP;
- Classification system, external code, hierarchy, equivalence a target applicability;
- replacement cycle, obojsmerná konzistencia a automatizovaná migrácia;
- workflow permissions a schvaľovací engine;
- produkčné validačné profily nad rámec explicitnej lifecycle policy;
- reálna populácia všetkých katalógov.

## 35. Implementation Preconditions

Implementácia môže začať iba ak dodrží tieto podmienky:

1. Existujúce JSON schémy sa nepoužijú na runtime lookup a nemenia význam.
2. `SchemaRegistry` zostane oddelený od nového CatalogRegistry.
3. CatalogRegistry bude in-memory, typed, immutable po zostavení a bez I/O.
4. ValidationContext bude explicitný a bude niesť registry aj lifecycle policy.
5. Existujúce `validate` API zostane contract-only a spätne kompatibilné.
6. Catalog-aware validácia dostane explicitný entry point a bez contextu fail-closed.
7. Reference integrity bude kontrolovať iba existence/uniqueness/type; compatibility bude samostatné `catalog_validation`.
8. Generic entity ReferenceResolver sa nevytvorí.
9. Quantity/ValueRange, Condition a Classification budú mať reusable semantic helpery.
10. PropertyRecord a Observation budú používať jeden shared property compatibility helper.
11. Missing target potlačí iba závislé compatibility chyby, nie nezávislé vetvy.
12. Default lifecycle policy povolí Approved, Deprecated označí warningom a odmietne Draft/Review/Archived pre nové použitie; odchýlka musí byť explicitná v contexte.
13. Testy budú používať iba izolované fiktívne entries.
14. Reálne katalógové dáta, 0.2C entity resolution, databáza, API a UI zostanú mimo rozsahu.
15. Accepted RFC a ADR sa nezmenia.

## 36. Readiness Verdict

Architektúra je dostatočne jasná na implementáciu obmedzeného katalogového integračného míľnika. Nie je potrebná oprava Accepted RFC alebo ADR. Hranice existence, compatibility, lifecycle policy, contextu, registry, API, error paths a testovacích dát sú definované.

Implementácia však musí zostať catalog-only, vyžadovať explicitný context, zachovať contract-only API a nevytvoriť generic entity resolver alebo produkčný catalog loader. Entity a SourceReference integrita, reálna catalog population a pokročilé katalógové semantics zostávajú odložené.

Implementácia Phase 0.2B.2.5 môže začať po prijatí týchto podmienok.

## 37. Implementation Outcome

Phase 0.2B.2.5 implementovala review bez zmeny Accepted RFC, ADR alebo JSON schém:

- `scripts/validation/catalog_context.py` poskytuje immutable `CatalogRegistry`, typované UNT/CND/PRP/CLS mapy, `CatalogRecord`, `ValidationContext` a explicitnú `CatalogLifecyclePolicy`;
- registry prijíma už kontraktovo validované záznamy, nevykonáva I/O a pri duplicate ID alebo nesprávnej ID rodine zlyhá ešte pred vytvorením snapshotu;
- `EosValidator.validate_with_context(...)` a `validate_json_file_with_context(...)` zachovávajú pôvodné `validate(...)` ako contract-only API a reportujú vykonané vrstvy cez `executedLayers`;
- chýbajúci context vracia `catalog_validation.context_required` a catalog-aware validácia sa potichu nepreskočí;
- `ValidationError` bol spätne kompatibilne rozšírený o `referencedId`; Deprecated cieľ vytvára warning a nemení `ValidationResult.ok` na false;
- UNT, CND, PRP a CLS lookup používa `reference_integrity`; lifecycle a allow-list pravidlá používajú `catalog_validation`;
- Quantity, ValueRange a vnorené Quantity zdieľajú UNT kontrolu; Condition zdieľa CND/value-form/prefix kontrolu; PropertyRecord a Observation zdieľajú jednu property compatibility implementáciu;
- Condition `referenceId` v tejto verzii kontroluje iba povolený prefix. Ani UNT/CND cieľ v tomto poli sa nerozlišuje, pretože všeobecná existencia entity referencie zostáva odložená do 0.2C;
- property unit allow-list sa vzťahuje iba na hlavný výsledok, nie na MeasurementQuality;
- default policy povoľuje Approved, povoľuje Deprecated s warningom a odmieta Draft, Review a Archived; authoring policy navyše povoľuje Draft a Review;
- implementovaný kód duplicate chyby je `reference_integrity.duplicate_catalog_id`, čo presnejšie odlišuje registry construction od všeobecnej entity identity;
- fiktívny snapshot s 15 entries je iba v `tests/fixtures/catalog-context/`; nevznikli produkčné katalógové dáta ani loader;
- 32 nových integračných testov a všetkých 182 pôvodných testov prešlo, spolu 214 testov bez zlyhania alebo chyby.

Vedome odložené zostávajú entity a SourceReference resolution, persistence, načítanie katalógov, replacement graph integrity, reálna catalog population, conversion, dimension inference, classification applicability a workflow validation. Implementácia nevytvorila generic resolver ani žiadny 0.2C kontrakt.

Phase 0.2B.2.5 je `COMPLETE`. Celá Phase 0.2B.2 čaká na krátky míľnik `Phase 0.2B.2-close - Knowledge Catalog Integration Closure Review`.

## 38. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-09-29 | 0.1 | 0 | Codex | Initial pre-design review defining validation-layer boundaries, catalog-only reference integrity, semantic compatibility, explicit context and registry ownership, lifecycle policy, error behavior and Phase 0.2B.2 completion criteria. |
| 2026-10-04 | 0.1 | 1 | Codex | Recorded the implemented immutable registry and context, explicit API, validation layers, lifecycle behavior, fictional integration fixtures, 214 passing tests and deferred 0.2C boundaries. |

READY FOR 0.2B.2 CLOSURE
