# EOS-004 - Základný dátový model

**Project:** EOS - Engineering Operating System  
**Document ID:** EOS-004  
**Version:** 0.1  
**Revision:** 1  
**Status:** Draft  
**Author:** Chief Engineering Knowledge Architect + Codex  
**Last update:** 2026-07-13  
**Document basis:** Internal governance decision  

---

## 1. Účel

Tento dokument definuje počiatočné entity EOS bez konkrétnych technických hodnôt. Ide o dátový kontrakt a nie o databázu hotových znalostí.

## 2. Spoločné metadáta entít

Každá hlavná dátová entita má mať minimálne tieto polia:

- `id`,
- `schemaVersion`,
- `recordVersion`,
- `revision`,
- `status`,
- `createdAt`,
- `createdBy`,
- `updatedAt`,
- `updatedBy`,
- `sourceLinks`,
- `changeSummary`.

Odporúčané doplnkové polia:

- `name`,
- `description`,
- `notes`,
- `replaces`,
- `replacedBy`.

### 2.1 Pravidlo pre `sourceLinks`

Pole `sourceLinks` zostáva súčasťou spoločných metadát entít.

V stave `Draft` môže byť `sourceLinks` prázdne, ak ide o pracovný návrh bez schválenej zdrojovej väzby.

V stave `Review` alebo `Approved` musí `sourceLinks` obsahovať zdroj vždy, keď záznam obsahuje overiteľné technické, výrobné, dodávateľské alebo obchodné tvrdenia.

JSON Schema môže overiť existenciu poľa a základný tvar položiek. Časť pravidla závislá od významu obsahu, napríklad rozpoznanie overiteľného tvrdenia, bude kontrolovať aplikačná validačná vrstva.

## 3. Rozdiel medzi schemaVersion, recordVersion a revision

`schemaVersion` označuje verziu dátového kontraktu, podľa ktorého je záznam štruktúrovaný.

`recordVersion` označuje významovú verziu konkrétneho záznamu. Zvyšuje sa pri zmene významu, rozhodnutia alebo obsahu, ktorý môže ovplyvniť použitie záznamu.

`revision` označuje menšiu opravu v rámci rovnakej `recordVersion`, napríklad opravu textu, doplnenie poznámky alebo spresnenie bez zmeny významu.

Príklad princípu:

- zmena schémy poľa zvyšuje `schemaVersion`,
- zmena významu záznamu zvyšuje `recordVersion`,
- jazyková alebo formálna oprava zvyšuje `revision`.

## 4. SourceReference ako autoritatívna entita

`SourceReference` je samostatná autoritatívna entita. Nejde iba o textovú poznámku pri inom zázname.

Účelom `SourceReference` je evidovať pôvod informácie tak, aby sa rovnaký zdroj dal použiť pri viacerých tvrdeniach, záznamoch alebo dokumentoch.

`SourceReference` sa od konkrétneho použitia zdroja oddeľuje cez väzbu `SourceLink`.

## 5. SourceLink

`SourceLink` je väzba medzi konkrétnym tvrdením alebo poľom a autoritatívnou entitou `SourceReference`.

Hlavné polia:

- `sourceReferenceId`,
- `sourceClass`,
- `supportedClaim`,
- `supportedField`,
- `usageType`,
- `sourceLocation`,
- `interpretationNote`,
- `verificationStatus`.

Význam polí:

- `sourceReferenceId` odkazuje na `SourceReference`, napríklad `SRC-000001`.
- `sourceClass` používa triedy `N`, `L`, `P` alebo `V`.
- `supportedClaim` opisuje tvrdenie, ktoré zdroj podporuje.
- `supportedField` označuje pole záznamu, ktorého sa zdroj týka.
- `usageType` rozlišuje citáciu, interpretáciu, praktickú skúsenosť, overenie alebo obmedzenie.
- `sourceLocation` uvádza lokalizáciu v zdroji, napríklad kapitolu, stranu, článok, výkres alebo internú poznámku.
- `interpretationNote` vysvetľuje, ako bol zdroj použitý.
- `verificationStatus` určuje, či je väzba návrh, skontrolovaná, schválená alebo sporná.

## 6. Entity

### 6.1 `SourceReference`

Účel: popísať pôvod informácie ako samostatný autoritatívny záznam.

ID formát: `SRC-xxxxxx`.

Hlavné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `sourceClass`, `title`, `referenceType`, `citation`, `date`, `createdAt`, `createdBy`, `updatedAt`, `updatedBy`, `changeSummary`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `sourceClass`, `title`, `referenceType`.

Väzby: môže byť použitá cez `SourceLink` v každej entite.

Spôsob zdrojovej klasifikácie: priamo cez `sourceClass`.

Spôsob revízie: cez `recordVersion`, `revision` a `changeSummary`.

Nesmie obsahovať: neoverenú interpretáciu vydávanú za fakt. Interpretácia patrí do `SourceLink`.

### 6.2 `Material`

Účel: reprezentovať materiál ako znalostný objekt.

ID formát: `MAT-xxxx`.

Hlavné polia: `id`, `name`, `designation`, `materialGroup`, `sourceLinks`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `name`, `designation`, `sourceLinks`.

Nepovinné polia: `aliases`, `notes`, `relatedNormReferences`.

Väzby: `StockMaterial`, `Job`, `NormReference`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: nezdrojované vlastnosti alebo odporúčania bez klasifikácie.

### 6.3 `StockMaterial`

Účel: popísať dostupnú alebo používanú formu polotovaru.

ID formát: `POL-xxxx`.

Hlavné polia: `id`, `materialId`, `stockType`, `designation`, `supplierIds`, `sourceLinks`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `materialId`, `stockType`.

Väzby: `Material`, `Supplier`, `Job`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: cenu alebo dostupnosť bez dátumu a zdroja.

### 6.4 `ManufacturingProcess`

Účel: definovať výrobný proces ako typ činnosti.

ID formát: `TEC-xxxx`.

Hlavné polia: `id`, `name`, `processGroup`, `description`, `capabilityNotes`, `sourceLinks`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `name`, `processGroup`.

Väzby: `JobOperation`, `Machine`, `Risk`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: garantované časy bez odkazu na overený záznam.

### 6.5 `Machine`

Účel: reprezentovať výrobné zariadenie.

ID formát: `MAC-xxxx`.

Hlavné polia: `id`, `name`, `machineType`, `capabilityReferences`, `status`, `sourceLinks`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `name`, `machineType`.

Väzby: `ManufacturingProcess`, `JobOperation`, `TimeRecord`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: neoverené parametre stroja.

### 6.6 `CuttingTool`

Účel: reprezentovať nástroj alebo nástrojovú zostavu.

ID formát: `TOOL-xxxx`.

Hlavné polia: `id`, `name`, `toolType`, `manufacturerReference`, `sourceLinks`, `notes`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `name`, `toolType`.

Väzby: `JobOperation`, `ManufacturingProcess`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: odporúčané rezné podmienky bez zdroja a kontextu.

### 6.7 `Supplier`

Účel: evidovať dodávateľa materiálu, polotovaru, nástroja alebo služby.

ID formát: `SUP-xxxx`.

Hlavné polia: `id`, `name`, `supplierType`, `contactReference`, `sourceLinks`, `notes`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `name`, `supplierType`.

Väzby: `StockMaterial`, `CuttingTool`, `Job`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`, ak záznam obsahuje technické alebo dodávateľsky overiteľné tvrdenia.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: citlivé obchodné údaje bez pravidiel prístupu.

### 6.8 `Job`

Účel: reprezentovať reálnu alebo pripravovanú zákazku.

ID formát: `JOB-yyyy-xxxx`.

Hlavné polia: `id`, `title`, `customerReference`, `drawingReferences`, `status`, `operations`, `sourceLinks`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `title`.

Väzby: `Material`, `StockMaterial`, `JobOperation`, `Risk`, `QuotationNote`, `TimeRecord`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: neoddelené interné poznámky, ktoré patria do rizík alebo lessons learned.

### 6.9 `JobOperation`

Účel: popísať jednu výrobnú alebo kontrolnú operáciu zákazky.

ID formát: `JOB-yyyy-xxxx-OP-xxx`.

Hlavné polia: `id`, `jobId`, `processId`, `machineId`, `sequence`, `description`, `sourceLinks`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `jobId`, `processId`, `sequence`.

Väzby: `Job`, `ManufacturingProcess`, `Machine`, `CuttingTool`, `TimeRecord`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: finálne časy bez oddelenia plánovaného a skutočného času.

### 6.10 `TimeRecord`

Účel: evidovať plánovaný alebo skutočný čas naviazaný na operáciu.

ID formát: `JOB-yyyy-xxxx-OP-xxx-TM-xxx`.

Hlavné polia: `id`, `jobOperationId`, `timeType`, `value`, `unit`, `sourceLinks`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `jobOperationId`, `timeType`, `sourceLinks`.

Väzby: `JobOperation`, `Machine`, `Job`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: automatický odhad bez označenia spôsobu vzniku.

### 6.11 `Risk`

Účel: zaznamenať technické, výrobné alebo cenové riziko.

ID formát: `JOB-yyyy-xxxx-RSK-xxx`.

Hlavné polia: `id`, `riskType`, `description`, `severity`, `mitigation`, `status`, `sourceLinks`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `riskType`, `description`.

Väzby: `Job`, `Material`, `ManufacturingProcess`, `QuotationNote`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: neoznačené domnienky vydávané za fakt.

### 6.12 `QuotationNote`

Účel: pripraviť poznámku alebo upozornenie do cenovej ponuky.

ID formát: `JOB-yyyy-xxxx-QN-xxx`.

Hlavné polia: `id`, `jobId`, `text`, `reason`, `sourceLinks`, `status`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `text`, `reason`, `sourceLinks`.

Väzby: `Job`, `Risk`, `NormReference`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: právne alebo technické záväzky bez schválenia.

### 6.13 `NormReference`

Účel: evidovať odkaz na externú normu, štandard alebo záväzný technický predpis.

ID formát: `NRM-xxxx`.

Hlavné polia: `id`, `standardCode`, `title`, `scope`, `sourceLinks`.

Povinné polia: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `standardCode`, `sourceLinks`.

Väzby: `Material`, `ManufacturingProcess`, `DocumentRecord`, `QuotationNote`.

Spôsob zdrojovej klasifikácie: cez `sourceLinks`, typicky s triedou `N`.

Spôsob revízie: cez spoločné metadáta.

Nesmie obsahovať: plné znenie normy, ak na to nie je oprávnenie.

### 6.14 `DocumentRecord`

Účel: evidovať riadený dokument EOS.

ID formát: používa ID dokumentu, ktorý eviduje.

Hlavné polia: `id`, `title`, `filePath`, `documentVersion`, `documentRevision`, `documentStatus`, `schemaVersion`, `recordVersion`, `revision`, `status`.

Povinné polia: `id`, `title`, `filePath`, `documentVersion`, `documentRevision`, `documentStatus`, `schemaVersion`, `recordVersion`, `revision`, `status`.

`documentVersion`, `documentRevision` a `documentStatus` opisujú riadený dokument.

`schemaVersion`, `recordVersion`, `revision` a `status` opisujú registračný dátový záznam `DocumentRecord`.

Tieto dve vrstvy verziovania sa nesmú miešať. Preferované riešenie je samostatná schéma `DocumentRecord`, ktorá tento rozdiel vyjadrí explicitne. Táto schéma sa v úlohe 0.1.1 ešte nevytvára.

Väzby: `SourceReference`, `NormReference`, `ADR`.

Spôsob zdrojovej klasifikácie: nepoužíva sa na governance pôvod dokumentu; technické tvrdenia v dokumente sa klasifikujú cez `SourceLink`.

Spôsob revízie: podľa pravidiel dokumentu a `EOS-003`.

Nesmie obsahovať: technické hodnoty, ktoré patria do dátových entít.

## 7. Revízie entít

Každá zmena významu záznamu musí zvýšiť `recordVersion` alebo `revision` podľa `EOS-003`.

Pôvodný význam musí zostať dohľadateľný cez históriu zmien, `changeSummary` alebo archív.

## 8. Súvisiace dokumenty

- `EOS-001_System_Architecture.md`
- `EOS-003_Identification_and_Versioning.md`
- `ADR-0002_Use_JSON_compatible_schemas_as_initial_data_contract.md`
- `ADR-0005_Separate_internal_EOS_standards_from_external_normative_references.md`
- `ADR-0006_Treat_source_references_as_first_class_entities.md`
- `ADR-0007_Separate_schema_version_from_record_version_and_revision.md`
- `ADR-0008_Use_hierarchical_identifiers_for_job_owned_entities.md`

## 9. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-07-13 | 0.1 | 0 | Chief Engineering Knowledge Architect + Codex | Initial draft |
| 2026-07-13 | 0.1 | 1 | Codex | Governance Alignment 0.1.1: doplnenie spoločných metadát, potvrdenie `SourceReference`, zavedenie `SourceLink`, zavedenie `NormReference` pre externé normatívne referencie a spresnenie verziovania dátových záznamov |
