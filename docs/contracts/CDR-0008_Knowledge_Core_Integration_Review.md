# CDR-0008 - Knowledge Core Integration Review

**Project:** EOS - Engineering Operating System  
**Contract Review ID:** CDR-0008  
**Review:** Knowledge Core Integration  
**Phase:** 0.2B.1-close  
**Version:** 0.1  
**Revision:** 1
**Status:** Review  
**Document basis:** Accepted EOS architecture + implemented 0.2B.1 contracts

---

## 1. Purpose

Tento dokument posudzuje, či sedem implementovaných Knowledge Core kontraktov tvorí konzistentné, skladateľné, validované a implementačne pripravené jadro pre nasledujúcu fázu Knowledge Catalogs.

Review nemení architektúru ani implementáciu. Findings pomenúvajú iba preukázané nedostatky, riziká a odložené zodpovednosti.

## 2. Scope

Review zahŕňa:

- objektovú taxonómiu, identity, vlastníctvo a lifecycle,
- identifikátory a ich centralizáciu,
- graf JSON Schema závislostí,
- štrukturálnu, aplikačnú, katalógovú, workflow a persistence hranicu,
- rekurzívnu aplikáciu významových pravidiel,
- zdrojovú dohľadateľnosť,
- konzistenciu value modelu, Conditions, Classification, PropertyRecord a Observation,
- serializačné konvencie, fixtures, testy a dokumentáciu,
- pripravenosť závislostí UNT, CND, PRP a CLS na fázu 0.2B.2.

Mimo rozsahu je zmena schém, validátora, testov, governance, RFC, ADR, backlogu alebo roadmapy. Review nevytvára katalógové záznamy ani nový Knowledge Core kontrakt.

## 3. Reviewed Artifacts

### Governance and architecture

- `AGENTS.md`
- `docs/governance/EOS-003_Identification_and_Versioning.md`
- `docs/governance/EOS-006_Data_Validation_Standard.md`
- `docs/governance/EOS-007_Validation_Capability_Matrix.md`
- `docs/governance/EOS-009_Architecture_Closure_Plan.md`
- `docs/governance/EOS-010_Architecture_Readiness_Review.md`
- `docs/rfc/RFC-0001_Engineering_Property_Model.md`
- `docs/rfc/RFC-0002_Engineering_Object_Taxonomy.md`
- `docs/rfc/RFC-0003_EOS_Engineering_Glossary.md`
- `adr/ADR-0014_Establish_RFC_governance_lifecycle.md`
- `adr/ADR-0015_Establish_engineering_knowledge_layer.md`
- `adr/ADR-0016_Treat_observation_as_first_class_evidence_entity.md`

Všetky tri RFC a všetky tri uvedené ADR sú `Accepted`.

### Contracts and schemas

- `CDR-0001` až `CDR-0007`
- všetkých sedem súborov v `schemas/knowledge-core/`
- všetky schémy v `schemas/common/`
- `schemas/index.schema.json`

### Validation, tests and documentation

- `scripts/validation/`
- `tests/test_validation.py`
- všetky validné a nevalidné Knowledge Core fixtures
- `schemas/README.md`, `scripts/README.md`, `tests/README.md`
- `CHANGELOG.md`, `ROADMAP.md`, `BACKLOG.md`

## 4. Contract Inventory

| Contract | Object type | Identity and ownership | Lifecycle | Required fields | Optional or conditional fields | Schema and ID dependencies | Application and deferred dependencies |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Quantity | Immutable Value Object | Bez ID; vlastní ho rodič | Cez rodiča | `value`, `unitId` | `notes` | `UNT`; identifiers | konečnosť čísla; existencia, stav, dimenzia a konverzia UNT v katalógu |
| ValueRange | Immutable Value Object | Bez ID; vlastní ho rodič | Cez rodiča | `unitId`, najmenej jedna hranica | `minValue`, `maxValue`, `lowerInclusive`, `upperInclusive`, `notes` | `UNT`; identifiers | poradie hraníc a konečnosť; UNT existencia, dimenzia a konverzia |
| MeasurementQuality | Immutable Value Object | Bez ID; vlastní ho rodič | Cez rodiča | najmenej jedna z `uncertainty`, `resolution`, `confidenceLevel` | uvedené štruktúrované polia a `notes` | Quantity, nepriamo `UNT` | nezáporná neistota, kladné rozlíšenie; metrologická kompatibilita a budúce charakteristiky |
| Condition | Immutable Value Object | Bez vlastného ID; `conditionTypeId` je referencia | Cez rodiča | `conditionTypeId`, `evaluationMode`, presne jedna hodnotová forma | `quantity`, `valueRange`, `textValue`, `booleanValue`, `referenceId`, `notes` | `CND`, Quantity, ValueRange a riadené cieľové ID | vnorené ValueRange pravidlá; CND existencia, povolená forma, dimenzia, referencia, kombinovanie a vyhodnotenie |
| Classification | Embedded reference Value Object | Bez vlastného ID; `classificationId` je referencia | Cez rodiča | `classificationId` | `sourceLinks` | `CLS`, SourceLink, nepriamo `SRC` | CLS existencia, stav, systém, hierarchia, kompatibilita a povinnosť zdrojov podľa pôvodu |
| PropertyRecord | Embedded claim-like Value Object | Bez ID; vlastní ho budúca doménová entita | Cez rodiča; vlastný claim `verificationStatus` | `propertyId`, `valueType`, `verificationStatus`, `sourceLinks`, presne jedna výsledková vetva | `quantity`, `valueRange`, `measurementQuality`, `conditions` | `PRP`, Quantity, ValueRange, MeasurementQuality, Condition, VerificationStatus, SourceLink | vnorené významové pravidlá; explicitný parent context pre zdroje; PRP, UNT a CND kompatibilita; workflow prijatia |
| Observation | First-class Entity a Aggregate Root | Stabilné `id` vo formáte `OBS-xxxxxx`; samostatne uložená a iba referencuje iné aggregate roots | Vlastný record lifecycle; dôkazový obsah append-only | entity metadata, `subjectId`, `observationScope`, `observedAt`, `propertyId`, `valueType`, `sourceLinks`, presne jedna výsledková vetva | `scopeReferenceId` pre JOB, `quantity`, `valueRange`, `measurementQuality`, `conditions`, `notes` | `OBS`, subject ID rodiny, `JOB`, `PRP`, metadata, Quantity, ValueRange, MeasurementQuality, Condition, SourceLink | vnorené významové pravidlá a source lifecycle; existencia subjektu/JOB/PRP, immutability, korekcie a Decision workflow sú odložené |

Inventár potvrdzuje, že katalógové ID vo Value Objectoch nie sú identitou vnorenej inštancie.

## 5. Object Taxonomy Review

| Contract | RFC-0002 classification | Result |
| --- | --- | --- |
| Quantity | Value Object | Consistent |
| ValueRange | Value Object | Consistent |
| MeasurementQuality | Value Object | Consistent |
| Condition | Value Object | Consistent |
| Classification | Embedded reference Value Object | Consistent |
| PropertyRecord | Embedded claim-like Value Object | Consistent |
| Observation | Entity and Aggregate Root | Consistent |

Žiadny Value Object nemá stabilné ID vlastnej inštancie. Polia `unitId`, `conditionTypeId`, `classificationId` a `propertyId` identifikujú externý riadený význam, nie vnorený objekt.

Observation je jediná first-class Entity a jediný Aggregate Root implementovaný v 0.2B.1. Neobsahuje PropertyRecord ani iný Aggregate Root. Subject a JOB scope sú ID referencie. Schema index je discovery a integračný test container; jeho polia nie sú DDD vlastníctvom ani persistence aggregate.

Výsledok: bez taxonomickej alebo aggregate-boundary nekonzistencie.

## 6. Identifier Review

### Identifier dependency matrix

| Identifier | Governed semantics | Consumers | Central schema | Result |
| --- | --- | --- | --- | --- |
| `OBS-xxxxxx` | Observation entity instance | Observation `id` | `$defs/OBS` | Consistent |
| `PRP-xxxxxx` | Property Catalog Entry alebo stabilný property význam | PropertyRecord, Observation | `$defs/PRP` | Consistent; existencia deferred |
| `UNT-xxxxxx` | Unit Catalog Entry alebo stabilný unit význam | Quantity, ValueRange, nepriamo ďalšie kontrakty | `$defs/UNT` | Consistent; existencia deferred |
| `CND-xxxxxx` | Condition Type Catalog Entry | Condition | `$defs/CND` | Consistent; existencia deferred |
| `CLS-xxxxxx` | Classification Catalog Entry | Classification | `$defs/CLS` | Consistent; existencia deferred |
| `JOB-yyyy-xxxx` | Job entity | Observation JOB scope a subject | `$defs/JOB` | Consistent; existencia deferred |
| `MAT`, `POL`, `TEC`, `MAC`, `TOOL`, `SUP`, `JOB`, `JOB_OPERATION` | Povolené subject rodiny prvého Observation profilu | Observation `subjectId` | príslušné centrálne `$defs` | Consistent; existencia deferred |

Všetky uvedené formáty sú `Active` v EOS-003 a všetky Knowledge Core schémy používajú centrálne `$ref`. V Knowledge Core schémach nie je inline regex.

Static union `Condition.referenceId` však nemá explicitnú dlhodobú target policy a po pridaní ďalších aktívnych ID rodín už nereprezentuje všetky centrálne podporované ID. Toto je finding KCI-0003; automatické pridanie ďalších rodín bez katalógovej semantiky sa neodporúča.

## 7. Dependency Graph

```text
Quantity -> UNT
ValueRange -> UNT
MeasurementQuality -> Quantity -> UNT
Condition -> CND, Quantity, ValueRange, governed reference ID families
Classification -> CLS, SourceLink -> SRC, VerificationStatus
PropertyRecord -> PRP, Quantity, ValueRange, MeasurementQuality,
                  Condition, SourceLink, VerificationStatus
Observation -> OBS, subject ID families, JOB, PRP, common metadata,
               Quantity, ValueRange, MeasurementQuality, Condition, SourceLink
```

Automatický audit načítal 16 schém a nenašiel žiadny cyklus. Všetkých 103 `$ref` bolo možné rozlíšiť. Reusable kontrakty sa používajú cez `$ref`; Quantity, ValueRange, MeasurementQuality, Condition ani SourceLink nie sú lokálne kopírované.

Smer závislostí je od zložených objektov k menším Value Objectom a spoločným foundation kontraktom. Observation ani PropertyRecord sa navzájom nereferencujú.

## 8. Nested Validation Review

| Invariant | Standalone | PropertyRecord | Observation | Result |
| --- | --- | --- | --- | --- |
| ValueRange `minValue <= maxValue` | `$.minValue` | `$.valueRange.minValue` | `$.valueRange.minValue` | Application error at all levels |
| MeasurementQuality `uncertainty.value >= 0` | `$.uncertainty.value` | `$.measurementQuality.uncertainty.value` | `$.measurementQuality.uncertainty.value` | Application error at all levels |
| MeasurementQuality `resolution.value > 0` | `$.resolution.value` | `$.measurementQuality.resolution.value` | `$.measurementQuality.resolution.value` | Application error at all levels |
| Condition structural validity | root/nested field | `$.conditions[0]...` | `$.conditions[0]...` | Schema error at all levels |
| ValueRange semantics inside Condition | nested ValueRange path | `$.conditions[0].valueRange.minValue` | `$.conditions[0].valueRange.minValue` | Application error composed recursively |
| Observation source lifecycle through index | n/a | n/a | `$.observations[0].sourceLinks` | Application error preserves parent path |

`EMBEDDED_CONTRACT_FIELDS` skladá existujúce validátory podľa schema ID. Významové kontroly ValueRange a MeasurementQuality nie sú kopírované do PropertyRecord ani Observation.

Výsledok: nested semantic validation je funkčná a zachováva presné cesty.

## 9. Validation Responsibility Matrix

| Contract or invariant | JSON Schema | EOS application | Catalog-aware | Workflow/governance | Persistence |
| --- | --- | --- | --- | --- | --- |
| Quantity shape, value type, UNT format | Yes | finite number | UNT existence, state, dimension | No | parent ownership |
| ValueRange shape and boundary presence | Yes | boundary order; finite number | UNT semantics | No | parent ownership |
| Inclusive flag requires matching boundary | Yes | currently duplicated | No | No | No |
| MeasurementQuality shape and confidence range | Yes | uncertainty/resolution sign | unit and method compatibility | No | parent ownership |
| Condition form discriminator and CND format | Yes | nested ValueRange rules | CND existence, value form, target and dimension | applicability/composition policy | parent ownership |
| Classification shape and SourceLink structure | Yes | SourceLink ID check currently overlaps schema | CLS existence, origin, system, hierarchy and parent compatibility | provenance policy | parent ownership |
| PropertyRecord typed branch and verification token | Yes | nested core rules | PRP/value/unit/condition compatibility | parent context, evidence requirement, promotion authority | parent transaction/history |
| Observation identity, scope shape and typed branch | Yes | nested rules and non-empty source rule by status | PRP/unit/condition compatibility | Decision/promotion and correction policy | referential integrity and append-only enforcement |

JSON Schema nepotvrdzuje existenciu katalógových položiek ani subjektov. VerificationStatus token sám nepotvrdzuje oprávnenie alebo audit rozhodnutia. Immutability Observation nemôže garantovať serializačný kontrakt.

Finding KCI-0002 identifikuje prekrývanie formátovej a reference-integrity kontroly SourceLink. Finding KCI-0008 identifikuje zámerne zdokumentované, ale nadbytočné dvojité vynucovanie inclusive flag pravidiel.

## 10. Source Traceability Review

| Contract | Structural behavior | Semantic behavior | Result |
| --- | --- | --- | --- |
| Classification | `sourceLinks` optional; pri uvedení používa common SourceLink | externý pôvod a relevantnosť zdrojov čakajú na CLS catalog context | Consistent |
| PropertyRecord | pole je required, prázdne pole je štrukturálne platné | neprázdnosť závisí od lifecycle rodiča a explicitného parent contextu | Consistent and explicitly deferred |
| Observation | pole je required; Draft môže byť prázdny | Review/Approved bez zdroja je application error aj cez schema index | Consistent with evidence principle |

SourceLink štruktúra sa nekopíruje. Classification a PropertyRecord referencujú common SourceLink priamo; Observation používa tú istú definíciu cez common metadata. Multiplicita ostáva konzistentná ako pole bez nezdokumentovaného `uniqueItems`.

Zdroj definície katalógovej položky a dôkaz konkrétneho zaradenia alebo tvrdenia zostávajú oddelené. SourceLink nie je payload ani náhrada budúcej referenčnej integrity.

## 11. Value Model Review

- Quantity nesie jeden scalar a `unitId`; neobsahuje interval, neistotu, podmienku ani zdroj.
- ValueRange nesie jeden interval a `unitId`; neobsahuje nominal value ani tolerančný význam.
- MeasurementQuality nesie vybrané metrologické charakteristiky, nie meraný výsledok. Manufacturing tolerance zostáva v budúcom requirement/tolerance modeli.
- PropertyRecord aj Observation používajú uzavretý discriminator `valueType` a presne jednu vetvu Quantity alebo ValueRange.
- PropertyRecord a Observation sa navzájom nevkladajú. Evidence a claim ostávajú oddelené.
- Neexistuje arbitrary JSON payload ani všeobecný free-text value escape hatch.
- MeasurementQuality je voliteľná kvalifikácia výsledku a nemení hodnotovú vetvu.

Výsledok: value model je konzistentný a bez kolízie hodnoty, rozsahu, kvality a tolerancie.

## 12. Condition Review

Condition vyžaduje `conditionTypeId`, `evaluationMode` a presne jednu z piatich hodnotových foriem. Nevykonáva evaluation engine. Quantity a ValueRange sa znovu používajú cez `$ref`; arrays v PropertyRecord a Observation odkazujú na rovnakú schému a poradie nemá autoritatívny význam.

Rozpory, duplicity, dedenie a kompatibilita sú odložené. Pred katalógovým použitím treba určiť, či viac podmienok s rovnakým `conditionTypeId` znamená konjunkciu, alternatívu, chybu alebo legitímne viacnásobné obmedzenie. Toto patrí do CND katalógovej semantiky, nie do aktuálnej schémy.

Condition nepovoľuje vlastné SourceLinks. Zdrojovanie konkrétnej vnorenej podmienky preto musí zatiaľ zabezpečiť SourceLink rodiča s presným `supportedField`; budúci CND návrh musí potvrdiť, či je to dostatočné voči širšiemu pravidlu RFC-0001 pre samostatne zdrojované podmienky.

Výsledok: core kontrakt je použiteľný; cieľová referencia a multi-condition semantics vyžadujú explicitné katalógové pravidlá.

## 13. Classification Review

Classification je embedded reference Value Object, nie Condition ani Catalog Entry. `classificationId` odkazuje na budúcu CLS položku a nie je identitou vnorenej Classification. Textový fallback, lokálna hierarchia, systém, kód a lifecycle nie sú povolené.

Hierarchy, system/version, existencia, active state a kompatibilita s rodičom zostávajú v Classification Catalog. SourceLinks sú štrukturálne voliteľné; externý pôvod bude možné vynútiť až z katalógového kontextu.

Výsledok: katalógové semantics neunikli do 0.2B.1.

## 14. PropertyRecord Review

PropertyRecord je embedded claim-like Value Object bez vlastného ID a bez record lifecycle. Vyžaduje riadený `propertyId`, discriminator, práve jednu číselnú vetvu, claim `verificationStatus` a pole `sourceLinks`.

MeasurementQuality a Conditions sú voliteľné a používajú spoločné kontrakty. Observation, Decision, derived-data promotion, identity, revision a lifecycle polia sú odmietnuté.

VerificationStatus vyjadruje stav overenia tvrdenia, nie lifecycle rodiča ani podpis oprávnenej osoby. Samostatná validácia PropertyRecord zámerne neodvodzuje parent status a neprázdnosť zdrojov. Budúci rodič musí odovzdať explicitný lifecycle a evidence context.

Výsledok: hranica claim, workflow a rodičovského vlastníctva je zachovaná.

## 15. Observation Review

Observation je Entity a Aggregate Root so stabilným OBS ID, spoločnými entity metadátami a samostatným auditom. Referencuje jeden subjekt a v počiatočnom profile podporuje iba GLOBAL alebo JOB scope.

`observedAt` je doménový čas udalosti; `createdAt` je čas vytvorenia EOS záznamu. `recordedAt` nevznikol. Observation nesie jeden typed property measurement result, nie PropertyRecord ani arbitrary payload.

Source-backed evidence princíp je zachovaný. Root nemá claim `verificationStatus`. Dôkazový obsah má byť append-only, ale technické vynútenie, korekcia a supersession patria persistence a budúcemu workflow.

Výsledok: implementácia zodpovedá RFC-0001 Revision 5, RFC-0002 a ADR-0016 bez evidence/claim kolízie.

## 16. Serialization Consistency

Všetkých sedem schém:

- deklaruje Draft 2020-12 a kanonické `https://eos.local/...` ID,
- má title, description, root `type: object` a `additionalProperties: false`,
- používa camelCase polia a riadené enum tokeny,
- odmieta `null`, pokiaľ nie je explicitne povolený,
- je registrovaných v `$defs` aj integračných properties schema indexu,
- nepoužíva inline identifier regex.

MeasurementQuality nemá root `required`, ale ekvivalentnú požiadavku najmenej jednej štruktúrovanej charakteristiky vyjadruje cez `anyOf`; nejde o odchýlku.

Enum casing je významovo konzistentný: record lifecycle používa PascalCase tokeny, Observation scope uppercase tokeny a value discriminators/evaluation modes lowercase tokeny podľa príslušného kontraktu.

Nízka nekonzistencia ostáva pri `notes`: Quantity, ValueRange, MeasurementQuality a Condition vyžadujú neprázdny text, kým Observation používa common metadata `notes`, ktoré povoľuje prázdny string. Pozri KCI-0007.

## 17. Fixture Coverage

| Contract | Valid | Invalid | Coverage assessment |
| --- | ---: | ---: | --- |
| Quantity | 5 | 12 | minimum/full-with-notes, required, ID, type, null, unknown field, metadata; non-finite values sú testované programovo |
| ValueRange | 8 | 20 | one/both boundaries, inclusivity, required, ID, type, null, metadata, unknown and semantic order |
| MeasurementQuality | 10 | 29 | jednotlivé a kombinované charakteristiky, bounds, nested Quantity, deferred/tolerance fields, metadata and semantic signs |
| Condition | 7 | 31 | všetkých päť value forms, discriminator, modes, IDs, nested contracts, null, unknown and forbidden metadata |
| Classification | 4 | 26 | id-only, sources, IDs, SourceLink nesting, null, unknown, free-text and metadata exclusions |
| PropertyRecord | 10 | 40 | both branches, optional children, discriminator, verification, sources, nested structural and semantic failures |
| Observation | 10 | 45 | identity, subjects, scopes, time, branches, sources, metadata, exclusions and nested semantic failures |

Knowledge Core spolu obsahuje 54 validných a 203 nevalidných fixtures. Celý projekt obsahuje 57 validných a 203 nevalidných fixtures; tri ďalšie validné patria foundation kontraktom.

Pokrytie blokujúcich invariantov je dostatočné. Všeobecné invalid-fixture slučky však pri viacerých kontraktoch kontrolujú iba neúspech, nie zamýšľaný error code a path. Pozri KCI-0006.

## 18. Test Quality

Kompletná sada obsahuje 120 unittest testov. Kritické semantické testy overujú kategóriu, error code aj presnú nested path. Schema index má integračné testy pre všetkých sedem kontraktov. Testy rozlišujú `schema_validation`, `application_validation` a `reference_integrity`.

Reversed ValueRange, záporná uncertainty a nulová resolution dosahujú aplikačný validátor samostatne aj v PropertyRecord a Observation bez nesúvisiaceho schema failure. Nested Condition validita sa kontroluje na skutočnej nested ceste. Testy teda nie sú zelené iba vďaka generickému skoršiemu zlyhaniu pri kritických významových prípadoch.

Simulácia neprítomného `jsonschema` však vykonala 120 testov ako 120 skipped a `unittest` výsledok bol `successful=True`, `OK (skipped=120)`. Správa nie je tichá, ale process status môže byť nesprávne interpretovaný ako úspech. To odporuje validačnému governance pravidlu; pozri KCI-0001.

## 19. Documentation Consistency

Schemas, scripts a tests README dokumentujú všetkých sedem kontraktov. CHANGELOG a ROADMAP uvádzajú sedem technicky implementovaných kontraktov, 0.2B.1 zatiaľ formálne neuzatvárajú a Phase 0.2B.2 neoznačujú ako začatú.

BACKLOG však stále uvádza začatie 0.2B.1, návrh jeho siedmich schém a rozhodnutie o začatí testov ako otvorené úlohy. To je v rozpore s repository state a ROADMAP; pozri KCI-0004.

`scripts/README.md` obsahuje starú vetu, že validácia používa iba štandardnú knižnicu a `jsonschema` nie je dostupné, hoci nasledujúce odseky, pyproject a runtime potvrdzujú opak; pozri KCI-0005.

## 20. Catalog Readiness

| Prefix | Current structural role | Missing catalog semantics | Expected first contract | Downstream consumers |
| --- | --- | --- | --- | --- |
| UNT | identifikuje jednotku v Quantity a ValueRange | názov/symbol, dimenzia, stav, canonical unit, konverzná politika | Unit Catalog Entry | všetky číselné kontrakty, PropertyRecord, Observation, Condition |
| CND | identifikuje význam Condition | povolená value form, unit/dimension, reference target, multiplicita, applicability | Condition Type Catalog Entry | Condition, PropertyRecord, Observation |
| PRP | identifikuje význam technickej vlastnosti | value type, unit/dimension, required Conditions, porovnateľnosť, domain applicability | Property Catalog Entry | PropertyRecord, Observation a budúce knowledge entities |
| CLS | identifikuje riadenú kategóriu | system/version, hierarchy, origin, lifecycle, parent compatibility and provenance rule | Classification Catalog Entry | Classification a budúce knowledge entities |

Odporúčaný dependency order je:

1. Unit Catalog,
2. Condition Type Catalog,
3. Property Catalog,
4. Classification Catalog.

Unit semantics sú najnižšia spoločná závislosť. CND má predchádzať plnej PRP kompatibilite, pretože Property Catalog môže deklarovať povinné alebo povolené condition types. Classification Catalog je relatívne nezávislý, ale vyžaduje samostatnú source-origin a hierarchy politiku.

## 21. Technical Debt

| Deferred item | Target | Note |
| --- | --- | --- |
| UNT, CND, PRP a CLS existencia, lifecycle a compatibility | required in 0.2B.2 | Základná katalógová zodpovednosť |
| Property/unit/valueType/dimension compatibility | required in 0.2B.2 | Nevyhnutné pred autoritatívnym použitím PropertyRecord a Observation |
| Condition target, value-form, duplication and contradiction semantics | required in 0.2B.2 | Patrí do CND a aplikačnej validácie |
| Classification hierarchy, system and external-source enforcement | required in 0.2B.2 | Rozlíšiť zdroj definície CLS od dôkazu zaradenia |
| Referential integrity service and error-category boundary | required in 0.2B.2 | Formát ID nie je existencia cieľa |
| Stored Decision and evidence-to-claim promotion | required in 0.2C | Observation môže existovať skôr, promotion nie |
| Generic/non-numeric Observation result | required in 0.2C | Potrebuje riadený typed result model |
| Observation correction/supersession | required in 0.2C | Persistence a audit policy |
| PROJECT/EXPERIMENT Observation scope | later | Až po governance identifikátorov a entít |
| Actor identity, attachments and evidence verification | later | Potrebujú samostatné identity a lifecycle pravidlá |
| Requirement/tolerance model | later | Nesmie sa vrátiť do MeasurementQuality |
| Accuracy, declared error, repeatability and reproducibility | optional research | Pred rozšírením treba stabilizovať metrologickú semantiku |

Existujúce backlog témy sa týmto reportom neduplikujú ani nemenia.

## 22. Blocking Defects

### KCI-0001

- **Severity:** Medium
- **Affected contracts:** všetky schémovo validované kontrakty a test harness
- **Description:** pri chýbajúcom `jsonschema` vykoná `setUp` každý test ako skipped; simulovaný beh skončil `OK (skipped=120)` a `successful=True`.
- **Impact:** automatizácia môže integračnú validáciu bez runtime dependency nesprávne vyhodnotiť ako úspešnú, hoci governance ju označuje za blokovanú.
- **Recommended action:** pridať failujúci suite-level dependency preflight alebo samostatný povinný runner krok s nenulovým exit statusom. Zachovať jasnú inštalačnú správu.
- **Blocks 0.2B.2:** Yes

### KCI-0002

- **Severity:** Medium
- **Affected contracts:** SourceLink, Classification, PropertyRecord, Observation a validačná vrstva
- **Description:** `sourceReferenceId` pattern sa kontroluje štandardnou schémou cez centrálny SRC `$ref` a zároveň ručne cez regex v `_validate_source_link_ids`. Jeden chybný formát preto vracia `schema_validation.pattern` aj `reference_integrity.invalid_source_reference_id`.
- **Impact:** duplikovaný formát môže časom driftovať a `reference_integrity` sa zamieňa s formátovou validáciou namiesto existencie cieľa.
- **Recommended action:** ponechať formát výlučne JSON Schema a vyhradiť reference-integrity vrstvu pre existenciu, stav a kompatibilitu referencie. Pridať regresný test kategórie.
- **Blocks 0.2B.2:** Yes

### KCI-0004

- **Severity:** Medium
- **Affected contracts:** project sequencing and documentation
- **Description:** BACKLOG stále uvádza začatie 0.2B.1, návrh siedmich schém a rozhodnutie o spustení testov ako otvorené, hoci implementácia a 120-testová sada existujú.
- **Impact:** vstup do 0.2B.2 nemá jednoznačný operatívny backlog a môže opakovať dokončenú prácu.
- **Recommended action:** v samostatnom closure kroku presunúť dokončené položky a zapísať iba reálne katalógové a integračné pokračovania.
- **Blocks 0.2B.2:** Yes

Nie je evidovaný žiadny Critical ani High blocker a žiadny blocker nevyžaduje architektonický redizajn.

## 23. Non-blocking Findings

### KCI-0003

- **Severity:** Medium
- **Affected contracts:** Condition, future Condition Type Catalog
- **Description:** `Condition.referenceId` je statický union ID rodín. Jeho opis hovorí o existujúcich centrálne podporovaných identifikátoroch, ale union po neskorších míľnikoch neobsahuje aktívne `OBS`, `PRP` ani `CLS`.
- **Impact:** union môže pri každom novom prefixe driftovať; samotné pridanie všetkých ID by zároveň povolilo sémanticky nevhodné target types.
- **Recommended action:** počas návrhu CND katalógu definovať povolené target family per condition type a upraviť opis alebo validačnú hranicu. Nepridávať ID automaticky bez semantiky.
- **Blocks 0.2B.2:** No

### KCI-0005

- **Severity:** Low
- **Affected contracts:** validation documentation
- **Description:** `scripts/README.md` obsahuje zastarané tvrdenie, že runtime nemá `jsonschema` a validácia používa iba štandardnú knižnicu, v rozpore s ďalším textom a pyproject.
- **Impact:** používateľ môže zvoliť nesprávny setup alebo nesprávne interpretovať schopnosti validátora.
- **Recommended action:** odstrániť historickú vetu v closure dokumentačnej oprave.
- **Blocks 0.2B.2:** No

### KCI-0006

- **Severity:** Low
- **Affected contracts:** Quantity, ValueRange, MeasurementQuality, Condition, PropertyRecord, Observation tests
- **Description:** všeobecné invalid-fixture testy pri väčšine kontraktov overujú iba `result.ok == false`; Classification má presnejšie mapovanie dôvodu. Kritické semantic fixtures majú samostatné presné assertions.
- **Impact:** niektoré nekritické fixtures môžu zostať zelené po zmene skutočného dôvodu zlyhania.
- **Recommended action:** postupne zaviesť očakávaný error code/path manifest alebo parametrizované prípady pre každý fixture bez zmeny unittest frameworku.
- **Blocks 0.2B.2:** No

### KCI-0007

- **Severity:** Low
- **Affected contracts:** Observation and common metadata
- **Description:** Observation `notes` cez common metadata povoľuje prázdny string, kým notes v ostatných Knowledge Core Value Objectoch používajú `minLength: 1`.
- **Impact:** vzniká malá serializačná nekonzistencia a potenciálne bezvýznamná hodnota.
- **Recommended action:** pri najbližšej verziovanej metadata revízii prijať jednotnú empty-string policy; nemeníť kontrakt potichu.
- **Blocks 0.2B.2:** No

### KCI-0008

- **Severity:** Low
- **Affected contracts:** ValueRange and nested consumers
- **Description:** prítomnosť `lowerInclusive`/`upperInclusive` bez príslušnej hranice kontroluje `dependentRequired` aj aplikačný validátor, takže jeden problém vytvára schema aj application error.
- **Impact:** report je hlučnejší a zodpovednostná hranica je menej presná; správanie je však zdokumentované a konzistentné pri vnorení.
- **Recommended action:** v samostatnej verziovanej oprave ponechať toto pravidlo v JSON Schema a odstrániť redundantnú aplikačnú kontrolu alebo explicitne zdôvodniť potrebu dvoch kategórií.
- **Blocks 0.2B.2:** No

Celkom bolo zaznamenaných osem findings: 0 Critical, 0 High, 4 Medium a 4 Low.

## 24. Required Fixes Before 0.2B.2

Pred začatím katalógovej implementácie treba vykonať malý corrective/closure krok bez zmeny Accepted architektúry:

1. zabezpečiť nenulový výsledok integračných testov, ak `jsonschema` chýba,
2. odstrániť manuálnu formátovú duplicitu SourceLink ID z reference-integrity vrstvy a zachovať správne kategórie,
3. zosúladiť BACKLOG s dokončeným 0.2B.1 a reálnymi úlohami 0.2B.2.

KCI-0003 sa musí rozhodnúť v návrhu Condition Type Catalog, nie pred samotným otvorením corrective kroku. Low findings možno riešiť priebežne s príslušnou verziovanou zmenou.

## 25. Recommended 0.2B.2 Order

1. `0.2B.1-close.1` - finite validation and documentation corrections KCI-0001, KCI-0002, KCI-0004.
2. Unit Catalog contract and structural records.
3. Condition Type Catalog contract, value-form and reference-target policy.
4. Property Catalog contract, unit/dimension/valueType/condition compatibility.
5. Classification Catalog contract, system, hierarchy, lifecycle and source-origin semantics.
6. Catalog-aware and reference-integrity validation composed into PropertyRecord and Observation contexts.
7. Integration fixtures and tests proving catalog existence, state and compatibility failures without introducing real engineering knowledge.

## 26. Readiness Verdict

Phase 0.2B.1 Knowledge Core je architektonicky konzistentné, acyklické, skladateľné a významové invarianty sa pri vnorení zachovávajú. Identity sú centralizované, evidence/claim hranica ostáva čistá a katalógové závislosti sú explicitné.

Tri finite podmienky KCI-0001, KCI-0002 a KCI-0004 boli uzavreté v míľniku 0.2B.1-close.1 bez nového RFC, ADR alebo zmeny objektového modelu.

Konečný strojovo čitateľný verdict je uvedený ako posledný riadok dokumentu.

## 27. Corrective Closure

| Finding | Corrective action | Verification evidence | Final state |
| --- | --- | --- | --- |
| KCI-0001 | Suite-level dependency preflight nahradil per-test skip. Chýbajúci `jsonschema` aj tranzitívny `referencing` vyvolajú jasnú chybu s inštalačným postupom. | Riadené subprocess simulácie oboch chýbajúcich závislostí končia nenulovým návratovým kódom; normálny beh končí 122 úspešnými testami. | CLOSED |
| KCI-0002 | Odstránená ručná regex kontrola `sourceReferenceId` z aplikačnej vrstvy. Formát kontroluje centrálna JSON Schema. | Chybný vnorený SRC identifikátor vracia iba `schema_validation.pattern` s presnou cestou. Platný, ale nevyriešený SRC formát nevytvára falošnú `reference_integrity` chybu. | CLOSED |
| KCI-0004 | BACKLOG presunul dokončené úlohy 0.2B.1 a uvádza iba reálne katalógové a integračné pokračovania. | BACKLOG, ROADMAP a stav siedmich Knowledge Core schém sú navzájom konzistentné. | CLOSED |

V aktuálnej vrstve ešte neexistuje resolver autoritatívnych SourceReference záznamov. Korekcia KCI-0002 preto neodstraňuje žiadnu reálnu kontrolu existencie: tá sa v 0.2B.2 musí zaviesť v kategórii `reference_integrity`, oddelene od schémového formátu ID.

Neblokujúci finding KCI-0005 je takisto uzavretý odstránením zastaraného tvrdenia zo `scripts/README.md`. KCI-0003, KCI-0006, KCI-0007 a KCI-0008 zostávajú neblokujúce a ich odporúčané hranice sa nemenia.

Všetky blokujúce findings sú uzavreté. Phase 0.2B.1 je `COMPLETE`; Phase 0.2B.2 je nasledujúca fáza a nebola začatá.

## 28. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-09-09 | 0.1 | 0 | Codex | Initial integration review of all seven Phase 0.2B.1 Knowledge Core contracts; contract, identifier, dependency, validation, traceability, fixture, test, documentation and catalog-readiness audit. |
| 2026-09-09 | 0.1 | 1 | Codex | Corrective closure of blocking findings KCI-0001, KCI-0002 and KCI-0004; validation bootstrap, error-category boundary and backlog alignment verified. |

READY FOR 0.2B.2
