# CHANGELOG

## 0.2B.2.3 - 2026-09-24

Status: Implemented / Review

### Added

- `schemas/catalogs/property-catalog-entry.schema.json` pre samostatný Knowledge Catalog Entry Aggregate Root s centrálnym PRP ID, common metadata, povinným významovým opisom, riadenými value types, presným UNT allow-listom, voliteľným CND allow-listom a provenance.
- Registrácia `propertyCatalogEntry` a `propertyCatalogEntries` v schema indexe.
- 11 platných a 44 neplatných fiktívnych fixtures a 16 unittest testov pre Property Catalog v1.

### Changed

- CDR-0011 zvýšený na Revision 1 a doplnený o skutočný implementačný, validačný a testovací výsledok.
- Existujúca validačná kompozícia aplikuje lifecycle/source pravidlo na Property Catalog Entry priamo aj cez schema index.
- Dokumentácia schém, testov, validátora a roadmap opisuje Knowledge Catalog rolu, PRP identitu a value-type/unit/condition policy.

### Deferred / Not Added

- Nevznikla catalog-aware validácia PropertyRecord alebo Observation, reference-integrity resolver, canonical unit, required Conditions, multiplicita, MeasurementQuality policy, classification väzba, alias, equivalence, quantity-kind, dimension ani conversion model.
- Nevznikla žiadna reálna PRP položka ani Classification Catalog.
- Celá Phase 0.2B.2 nie je dokončená. Nasleduje `Phase 0.2B.2.4-prep - Classification Catalog Pre-design Review`, ktorá nebola začatá.

## 0.2B.2.2 - 2026-09-24

Status: Implemented / Review

### Added

- `schemas/catalogs/condition-type-catalog-entry.schema.json` pre samostatný Knowledge Catalog Entry Aggregate Root s centrálnym CND ID, common metadata, riadenými hodnotovými formami, podmienenou reference-prefix policy a provenance.
- Registrácia `conditionTypeCatalogEntry` a `conditionTypeCatalogEntries` v schema indexe.
- 8 platných a 38 neplatných fiktívnych fixtures a 15 unittest testov pre Condition Type Catalog v1.

### Changed

- CDR-0010 zvýšený na Revision 1 a doplnený o skutočný implementačný, validačný a testovací výsledok.
- Existujúca validačná kompozícia aplikuje lifecycle/source pravidlo na Condition Type Catalog Entry priamo aj cez schema index.
- Dokumentácia schém, testov, validátora a roadmap opisuje Knowledge Catalog rolu, CND identitu, value-form/reference policy a hranicu voči Property Catalogu.

### Deferred / Not Added

- Nevznikla catalog-aware validácia Condition, reference-integrity resolver, evaluation-mode policy, unit restriction, quantity-kind, dimension, multiplicity, logický výraz ani rule engine.
- Nevznikla žiadna reálna CND položka, Property Catalog ani Classification Catalog.
- Celá Phase 0.2B.2 nie je dokončená. Nasleduje `Phase 0.2B.2.3-prep - Property Catalog Pre-design Review`, ktorá nebola začatá.

## 0.2B.2.1 - 2026-09-10

Status: Implemented / Review

### Added

- `schemas/catalogs/unit-catalog-entry.schema.json` pre samostatný Unit Catalog Entry Aggregate Root s centrálnym UNT ID, common metadata, name, symbol, provenance a voliteľnými replacement referenciami.
- Registrácia `unitCatalogEntry` a `unitCatalogEntries` v schema indexe.
- 8 platných a 31 neplatných fiktívnych fixtures a 15 unittest testov pre Unit Catalog v1.

### Changed

- CDR-0009 zvýšený na Revision 1 a doplnený o skutočný implementačný, validačný a testovací výsledok.
- Existujúca validačná kompozícia aplikuje lifecycle/source pravidlo na Unit Catalog Entry priamo aj cez schema index.
- Dokumentácia schém, testov, validátora a roadmap opisuje identitu, lifecycle, symbolovú neunikátnosť, provenance a replacement hranice.

### Deferred / Not Added

- Nevznikol quantity-kind, dimension, unit-system, alias, equivalence ani conversion model alebo engine.
- Nevznikla žiadna reálna jednotka ani autoritatívna Unit Catalog populácia.
- Celá Phase 0.2B.2 nie je dokončená. Nasleduje Phase 0.2B.2.2 - Condition Type Catalog, ktorá nebola začatá.

## 0.2B.1-close.1 - 2026-09-09

Status: Completed

### Changed

- Testovacia bootstrap kontrola teraz pri chýbajúcom `jsonschema` alebo `referencing` zlyhá s nenulovým návratovým kódom a jasným inštalačným postupom namiesto výsledku `OK` so všetkými testami preskočenými.
- Odstránená duplicitná ručná regex kontrola `sourceReferenceId`; formát kontroluje centrálna JSON Schema a kategória `reference_integrity` zostáva vyhradená pre skutočnú existenciu, stav a kompatibilitu referencie.
- `BACKLOG.md` je zosúladený s dokončenými siedmimi Knowledge Core kontraktmi a obsahuje konkrétne pokračovanie pre 0.2B.2.
- CDR-0008 Revision 1 uzatvára blokery KCI-0001, KCI-0002 a KCI-0004; opravuje sa aj zastaraný popis validačného runtime v dokumentácii.

### Validated

- Kompletných 122 unittest testov prešlo; simulácie chýbajúceho `jsonschema` aj `referencing` skončili nenulovo.
- Phase 0.2B.1 je `COMPLETE`. Nasleduje Phase 0.2B.2 - Knowledge Catalogs, ktorá nebola začatá.
- Schémy, katalógy, Accepted RFC a ADR sa v korektívnom uzatvorení nemenili.

## 0.2B.1.7 - 2026-09-08

Status: Implemented / Review

### Added

- `schemas/knowledge-core/observation.schema.json` pre first-class Property Measurement Observation Aggregate Root s jedným subjektom a jedným Quantity alebo ValueRange výsledkom.
- Centrálny OBS formát, Observation discovery v schema indexe, 10 platných a 45 neplatných fixtures.
- 15 unittest testov pre identitu, subject rodiny, GLOBAL/JOB scope, typed result, vnorené pravidlá, zdroje a indexovú kompozíciu.

### Changed

- CDR-0007 Revision 2 zaznamenáva implementačný výsledok; verdict zostáva `READY FOR IMPLEMENTATION` a Status Review.
- Validačná kompozícia rekurzívne používa existujúce ValueRange a MeasurementQuality pravidlá a existujúcu source lifecycle kontrolu.
- Dokumentácia schém, testov, validátora a roadmap opisuje úzky profil a deferred hranice.

### Deferred / Not Added

- Nevznikol PropertyRecord embedding, arbitrary payload, generic ObservationResult, nečíselný výsledok, PROJECT/EXPERIMENT binding, actor, attachment, evidence verification ani correction model.
- Referenčná existencia subject/JOB/PRP, katalógová kompatibilita, persistence immutability a Decision workflow zostávajú aplikačné alebo budúce pravidlá.
- Phase 0.2B.2 ani 0.2C nezačala; nevznikol nový RFC, ADR, katalóg, databáza, API ani UI.

## 0.2B.1.6 - 2026-09-08

Status: Implemented / Review

### Added

- `schemas/knowledge-core/property-record.schema.json` pre embedded claim-like Value Object s povinným `propertyId`, `valueType`, `verificationStatus`, `sourceLinks` a presne jednou vetvou `quantity` alebo `valueRange`.
- Centrálny PRP formát a discovery PropertyRecord v schema indexe.
- 10 platných a 40 neplatných fiktívnych fixtures a 13 unittest testov pre štruktúru, `$ref`, discriminator, odmietnuté polia, vnorené aplikačné pravidlá a regresie.

### Changed

- CDR-0006 Revision 1 zaznamenáva finálny implementačný výsledok; Status zostáva Review a verdikt `READY WITH CONDITIONS` je zachovaný.
- Validačná orchestrácia rekurzívne aplikuje existujúce ValueRange a MeasurementQuality pravidlá aj vo vnorených kontraktoch bez duplikácie ich implementácie.
- Dokumentácia schém, testov a validátora opisuje claim boundary, zdroje, verifikáciu a odložené katalógové kontroly.

### Deferred / Not Added

- Do 0.2B.2 zostáva existencia a stav PRP, povolený valueType, kompatibilita jednotiek a dimenzií, povinné podmienky, doménové rozsahy a property classification.
- Kontextová povinnosť neprázdnych `sourceLinks` a Decision workflow zostávajú odložené; samostatný kontrakt nepredstiera lifecycle rodiča.
- Nevznikol Property Catalog, Observation, Decision, reálne PRP položky, nové RFC, ADR ani governance dokumenty.
- Dokončený je iba rozsah 0.2B.1.6; Phase 0.2B.2 nezačala.

## 0.2B.1.5 - 2026-09-07

Status: Implemented / Review

### Added

- `schemas/knowledge-core/classification.schema.json` pre embedded reference Value Object s povinným `classificationId` a štrukturálne nepovinnými `sourceLinks` cez existujúci SourceLink `$ref`.
- Centrálny CLS formát a discovery v schema indexe.
- 4 platné a 26 neplatných fiktívnych fixtures; 12 nových unittest testov vrátane presných príčin a ciest chýb, multiplicity SourceLink a regresnej kontroly indexu.
- Konkrétna backlog úloha pre katalógové vynucovanie pôvodu a povinnosti sourceLinks v `0.2B.2`.

### Changed

- CDR-0005 Revision 1 dopĺňa finálny implementačný výsledok; Status zostáva Review.
- Dokumentácia schém a testov opisuje význam CLS, zdrojové pravidlá a limity validácie.
- Namiesto pre-design odporúčania neprázdneho sourceLinks sa zachováva existujúca EOS multiplicita: prázdne pole je štrukturálne platné a unikátnosť sa nevyžaduje. Ide o explicitné implementačné spresnenie podľa zadania, nie zrušenie zdrojovej povinnosti.

### Deferred / Not Added

- Povinnosť sourceLinks pre externé klasifikácie podľa RFC-0001 §4.6 zostáva platná; kontrola katalógového pôvodu, existencie, aktívneho stavu, kompatibility a hierarchie je odložená do `0.2B.2`.
- Validačný kód, závislosti a predchádzajúce Knowledge Core kontrakty sa nemenili.
- Nevznikol Classification Catalog, reálne CLS položky, nové RFC, ADR ani governance zmeny.
- Dokončený je iba implementačný rozsah `0.2B.1.5`; celý `0.2B.1` zostáva rozpracovaný a `0.2B.2` nezačala.

## 0.2B.1.4 - 2026-08-01

Status: Review

### Added

- `CDR-0004_Condition_Contract.md` ako contract review dokument pre štvrtý Knowledge Core Contract.
- `schemas/knowledge-core/condition.schema.json` pre value object `Condition`.
- Centrálny identifikátor `CND-xxxxxx` v `schemas/common/identifiers.schema.json`.
- Discovery záznam pre `Condition` v `schemas/index.schema.json`.
- Platné a neplatné fixture záznamy pre `Condition`.
- `unittest` pokrytie pre `CND` identifikátor, `evaluationMode`, presne jednu hodnotovú formu, vnorené `Quantity`/`ValueRange` `$ref`, notes-only rozhodnutie, zákaz metadata/source/verification polí a regresie `Quantity`/`ValueRange`/`MeasurementQuality`.

### Changed

- Dokumentácia schém, testov a skriptov opisuje počiatočný scope `Condition`, rozdiel medzi kontextovou podmienkou a výrobnou toleranciou, schema-only validáciu a odložené aplikačné pravidlá.

### Not Added

- Nevznikol Condition Type Catalog, Classification, PropertyRecord ani Observation kontrakt.
- Nevznikol tolerance schema, MeasurementMethod, Instrument, Unit Catalog ani Property Catalog.
- Nevznikli konkrétne strojárske hodnoty, reálne jednotky, konverzné faktory, kalkulačky, API, databázový server ani UI.
- Nevznikol nový ADR ani RFC.

## 0.2B.1.3 - 2026-08-01

Status: Review

### Added

- `CDR-0003_MeasurementQuality_Contract.md` ako contract review dokument pre tretí Knowledge Core Contract.
- `schemas/knowledge-core/measurement-quality.schema.json` pre value object `MeasurementQuality`.
- Discovery záznam pre `MeasurementQuality` v `schemas/index.schema.json`.
- Platné a neplatné fixture záznamy pre `MeasurementQuality`.
- `unittest` pokrytie pre vnorený `Quantity` `$ref`, notes-only rozhodnutie, `confidenceLevel`, aplikačné pravidlá pre neistotu a rozlíšenie, zákaz tolerancií a regresie `Quantity`/`ValueRange`.

### Changed

- EOS aplikačná validačná vrstva doplnená o pravidlá `MeasurementQuality`: `uncertainty.value >= 0` a `resolution.value > 0`.
- Dokumentácia schém, testov a skriptov opisuje počiatočný scope `MeasurementQuality`, rozdiel voči tolerancii, confidenceLevel reprezentáciu a odložené koncepty.

### Not Added

- Nevznikol tolerance, requirement, Condition, Classification, PropertyRecord ani Observation kontrakt.
- Nevznikol MeasurementMethod, Instrument, CalibrationRecord, Unit Catalog ani Property Catalog.
- Nevznikli konkrétne strojárske hodnoty, reálne jednotky, konverzné faktory, kalkulačky, API, databázový server ani UI.
- Nevznikol nový ADR ani RFC.

## 0.2B.1.3-prep - 2026-08-01

Status: Completed / Approved

### Changed

- RFC-0001 zvýšené na Revision 4 a cez zaznamenaný `Accepted -> Review -> Accepted` lifecycle opravená hranica `MeasurementQuality`.
- RFC-0003 zvýšené na Revision 3 a zosúladené so slovníkovým významom `MeasurementQuality`.
- Výrobná, konštrukčná, rozmerová, geometrická a akceptačná tolerancia odstránená z `MeasurementQuality`.
- `MeasurementQuality` ponechané pre metrologické charakteristiky ako neistota merania, rozlíšenie, deklarovaná chybová charakteristika meracieho systému, repeatability, reproducibility a confidence informácia.
- Budúci requirement/tolerance model explicitne odložený do backlogu.
- Implementácia `MeasurementQuality` zostáva ďalším kontraktom po tejto korekcii.

### Not Added

- Nevznikla žiadna JSON schéma.
- Nevznikol tolerance, requirement, MeasurementQuality, Condition, Classification, PropertyRecord ani Observation kontrakt.
- Nevznikol nový ADR ani RFC.

## 0.2B.1.2 - 2026-08-01

Status: Review

### Added

- `CDR-0002_ValueRange_Contract.md` ako contract review dokument pre druhý Knowledge Core Contract.
- `schemas/knowledge-core/value-range.schema.json` pre value object `ValueRange`.
- Discovery záznam pre `ValueRange` v `schemas/index.schema.json`.
- Platné a neplatné fixture záznamy pre `ValueRange`.
- `unittest` pokrytie pre štrukturálne pravidlá, aplikačné pravidlá, centrálny `UNT` `$ref`, schema index a regresiu `Quantity`.

### Changed

- EOS aplikačná validačná vrstva doplnená o pravidlá `ValueRange`: obrátené hranice a inkluzivita bez príslušnej hranice.
- Dokumentácia schém, testov a skriptov opisuje `ValueRange`, jeho vzťah ku `Quantity`, štrukturálnu a aplikačnú validáciu a sémantickú predvolenú inkluzivitu.

### Not Added

- Nevznikol Unit Catalog ani konkrétne jednotky.
- Nevznikli `MeasurementQuality`, `Condition`, `Classification`, `PropertyRecord` ani `Observation`.
- Nevznikli konkrétne strojárske hodnoty, konverzné faktory, kalkulačky, API, databázový server ani UI.
- Nevznikol nový ADR ani RFC.

## 0.2B.1.1 - 2026-08-01

Status: Review

### Added

- `CDR-0001_Quantity_Contract.md` ako prvý contract review dokument pre Knowledge Core Contract.
- `schemas/knowledge-core/quantity.schema.json` pre value object `Quantity`.
- Centrálny identifikátor `UNT-xxxxxx` v `schemas/common/identifiers.schema.json`.
- Discovery záznam pre `Quantity` v `schemas/index.schema.json`.
- Platné a neplatné fixture záznamy pre `Quantity`.
- `unittest` pokrytie pre validáciu `Quantity`, centrálny `UNT` `$ref`, viac chýb naraz, presné cesty k poliam a zákaz entity metadát vo value objecte.

### Changed

- Validačná vrstva genericky odmieta nefinite numerické hodnoty `NaN` a `Infinity`.
- Mapovanie `additionalProperties` chýb teraz ukazuje konkrétne neočakávané pole.
- Dokumentácia schém, testov a skriptov opisuje kontrakt `Quantity` a jeho limity.

### Not Added

- Nevznikol Unit Catalog ani konkrétne jednotky.
- Nevznikli `ValueRange`, `MeasurementQuality`, `Condition`, `PropertyRecord` ani `Observation`.
- Nevznikli konkrétne strojárske hodnoty, konverzné faktory, kalkulačky, API, databázový server ani UI.
- Nevznikol nový ADR ani RFC.

Všetky významné zmeny projektu EOS sa zaznamenávajú v tomto súbore.

## 0.2B.0 - 2026-08-01

Status: Completed / Approved

### Added

- Architecture Phase Complete záznam pre uzavretie architektonickej fázy.
- Architecture Freeze pravidlo: nové veľké architektonické dokumenty nevznikajú bez nového architektonického problému.

### Changed

- `EOS-003` doplnený o prefix governance pre `RFC`, `OBS`, `PRP`, `UNT`, `CLS`, `CND`, `DEC`, `REL` a `EVT`.
- `DEC-xxxxxx` označený ako `Candidate`.
- `REL-xxxxxx` a `EVT-xxxxxx` označené ako `Deferred`.
- RFC-0001, RFC-0002 a RFC-0003 prijaté ako `Accepted`.
- `EOS-009` aktualizovaný na closure stav po splnení governance podmienok.
- `EOS-010` aktualizovaný na Architecture Readiness Verdict `READY`.
- `ROADMAP.md` a `BACKLOG.md` nastavené na ďalší míľnik `Phase 0.2B.1 - Knowledge Core Contracts`.

### Not Added

- Nevznikli nové JSON schémy.
- Nevznikli nové ADR.
- Nevznikli nové RFC.
- Nebola začatá implementácia Knowledge Core Contracts.
- Nebol pridaný API, databázový server, calculation engine ani UI.

## 0.2A.2 - 2026-07-14

Status: Completed / Approved

### Added

- Minimalistický `pyproject.toml` s riadenou závislosťou `jsonschema>=4.18.0`.
- Jednotný validačný chybový model s kategóriami `json_syntax`, `schema_definition`, `schema_validation`, `application_validation` a `reference_integrity`.
- Testy pripravené pre `allOf`, `oneOf`, `if/then/else`, `uniqueItems`, `maximum`, format checkery a cross-file `$ref`.

### Changed

- ADR-0013 zmenené zo `Proposed` na `Accepted`.
- Štrukturálna JSON Schema validácia migrovaná na `jsonschema.validators.Draft202012Validator`.
- Interná validačná vrstva ponechaná pre EOS aplikačné pravidlá.
- EOS-006 a EOS-007 aktualizované po integrácii štandardného validátora.
- Dokumentácia doplnená o postup vytvorenia virtuálneho prostredia, inštalácie projektu a spustenia `unittest`.
- `pyproject.toml` doplnený o explicitné package discovery pre `scripts*`, aby editable inštalácia nezahŕňala dokumentačné a dátové priečinky ako Python packages.
- Regresne opravené mapovanie `required` chýb na konkrétne pole a explicitné format checkery pre `date`, `date-time` a `uri`.

### Not Added

- Nebol pridaný `pytest`.
- Nebola začatá fáza 0.2B.
- Neboli pridané nové technické entity ani strojárske dáta.

## 0.2A.1 - 2026-07-14

Status: Draft

### Added

- `EOS-007_Validation_Capability_Matrix.md`.
- `ADR-0013_Use_a_standards_compliant_JSON_Schema_validator.md` so statusom `Proposed`.
- Auditné testy pre lokálne `$ref`, nepodporované schema keywordy, viac chýb a presné cesty k poliam.

### Changed

- Validačná vrstva teraz fail-closed hlási nepodporované alebo neznáme JSON Schema kľúčové slová.
- Dokumentácia validácie jasne uvádza, že aktuálny validátor nie je plná implementácia JSON Schema Draft 2020-12.

### Not Added

- Nebola pridaná externá validačná závislosť.
- Nebola začatá fáza 0.2B.

## 0.2A.0 - 2026-07-13

Status: Draft

### Added

- Modulárne JSON Schema kontrakty pre spoločné metadáta, identifikátory, `SourceLink`, `SourceReference`, `NormReference` a `DocumentRecord`.
- Centrálny schema index `schemas/index.schema.json`.
- Kompatibilitný vstup `schemas/core_entities.schema.json`.
- Minimálna Python validačná vrstva v `scripts/validation/`.
- Netechnické testovacie fixtures a `unittest` testy.
- Governance dokument `EOS-006_Data_Validation_Standard.md`.
- ADR-0009 až ADR-0012.

### Not Added

- Neboli pridané materiálové, technologické, strojové, nástrojové, dodávateľské ani zákazkové entity.
- Neboli pridané kalkulačky, UI, databázový server ani konkrétne strojárske dáta.

## 0.1.1 - 2026-07-13

Status: Completed / Approved

### Changed

- Normalizovaný `EOS-000` do slovenčiny s plnou diakritikou bez zmeny významu.
- Zvýšená revízia governance dokumentov `EOS-001` až `EOS-005` na `Revision 1` a doplnená `Change History`.
- Oddelený governance pôvod dokumentu od technickej zdrojovej klasifikácie `N`, `L`, `P`, `V`.
- Rozlíšené interné technické štandardy `STD-xxx` a externé normatívne referencie `NRM-xxxx`.
- Potvrdený `SourceReference` ako samostatná autoritatívna entita.
- Zavedený koncept `SourceLink` pre väzbu technického tvrdenia na zdroj.
- Spresnené spoločné metadáta entít: `schemaVersion`, `recordVersion`, `revision`, `sourceLinks` a `changeSummary`.
- Spresnené pravidlo, že `sourceLinks` môže byť prázdne v stave `Draft`, ale pri `Review` alebo `Approved` musí pokrývať overiteľné technické, výrobné, dodávateľské alebo obchodné tvrdenia.
- Spresnené oddelenie verzie riadeného dokumentu od verzie registračného záznamu `DocumentRecord`.
- Doplnené hierarchické ID pre entity vlastnené zákazkou.

### Added

- `ADR-0005` až `ADR-0008`.

### Not Added

- Neboli pridané detailné technické schémy jednotlivých entít.
- Neboli pridané kalkulačky, UI, databázový server ani konkrétne strojárske dáta.

## 0.1.0 - 2026-07-13

### Added

- Založená základná štruktúra repozitára.
- Pridaný manifest `EOS-000`.
- Pridané governance dokumenty `EOS-001` až `EOS-005`.
- Pridané prvé architektonické rozhodnutia `ADR-0001` až `ADR-0004`.
- Pridané pravidlá práce v `AGENTS.md`.

### Not Added

- Neboli pridané kalkulačky.
- Nebolo pridané používateľské rozhranie.
- Neboli pridané konkrétne strojárske hodnoty.
