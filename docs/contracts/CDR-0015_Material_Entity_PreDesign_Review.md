# CDR-0015 Material Entity Pre-design Review

Project: EOS – Engineering Operating System  
Contract Review ID: CDR-0015  
Contract: Material  
Review type: Pre-design  
Phase: 0.2C.1-prep  
Version: 0.1  
Revision: 0  
Status: Review  
Document basis: Accepted EOS architecture + completed Phase 0.2B

## 1. Purpose

Definovať najmenší bezpečný kontrakt entity `Material` pred implementáciou prvej Knowledge Entity v Phase 0.2C. Review má zachovať prijaté hranice identity, aggregate ownership, claim, evidence, katalógovej validácie a zdrojovej dohľadateľnosti bez zavedenia reálnych materiálových znalostí.

## 2. Scope

Review rieši význam `Material`, identitu `MAT-xxxx`, vlastníctvo `PropertyRecord` a `Classification`, väzbu na `Observation`, lifecycle, provenance, názov, designation, normy, chemické zloženie, materiálový stav, hranicu voči `StockMaterial` a budúcu validačnú kompozíciu.

Mimo rozsahu sú JSON Schema, fixtures, validátor, katalógové dáta, reálne materiály, `StockMaterial`, `Supplier`, `ManufacturingProcess`, `Machine`, `CuttingTool`, persistence, API, UI a zmena Accepted RFC alebo ADR.

## 3. Reviewed Artifacts

Preskúmané boli:

- `AGENTS.md`, EOS-003, EOS-006, EOS-007, EOS-009 a EOS-010;
- Accepted RFC-0001, RFC-0002 a RFC-0003;
- Accepted ADR-0015 a ADR-0016;
- CDR-0005 až CDR-0008 a CDR-0010 až CDR-0014;
- schémy PropertyRecord, Classification, Observation, Property Catalog Entry, Classification Catalog Entry, common metadata, identifiers, SourceLink a schema index;
- aktuálne plánovacie a validačné README dokumenty;
- implementovaný `CatalogRegistry`, `ValidationContext`, `reference_integrity` a `catalog_validation`.

Pre-flight dňa 2026-10-04 potvrdil vetvu `feature/phase-0.2b-knowledge-contracts`, HEAD `200e428b64cd34308407fbd59d1226e5d7087848`, čistý pracovný strom, 214 úspešných testov, 20 schém, sedem Knowledge Core schém, štyri katalógové schémy, 17 ADR a štyri RFC. Neexistuje Material, StockMaterial ani iná 0.2C entity schéma a repozitár neobsahuje reálne produkčné katalógové alebo materiálové dáta.

## 4. Authoritative Findings

| Oblasť | Klasifikácia | Zistenie |
| --- | --- | --- |
| Doménový význam | AUTHORITATIVE | Material je materiálový znalostný objekt, nie fyzický kus, skladová forma ani dodávateľská položka. |
| Typ objektu | AUTHORITATIVE | Material je Knowledge Entity, Entity a Aggregate Root s vlastným lifecycle a auditnou históriou. |
| Identita | AUTHORITATIVE | Stabilné `MAT-xxxx` identifikuje Material entity; názov ani designation nie sú identita. |
| Vlastnosti | AUTHORITATIVE | Material môže vlastniť embedded `PropertyRecord`; PropertyRecord je claim-like Value Object revidovaný cez rodiča. |
| Klasifikácie | AUTHORITATIVE | Material môže vlastniť embedded `Classification`; CLS identifikuje katalógový význam, nie vnorené použitie. |
| Observation | AUTHORITATIVE | First-class Observation je samostatný Aggregate Root a môže referencovať Material cez `subjectId`; Material ju nesmie vlastniť. |
| Zdroje | AUTHORITATIVE | Material je source-backed entity; root provenance, claim provenance, assignment provenance a evidence provenance majú odlišný význam. |
| Katalógy | AUTHORITATIVE | PRP, UNT, CND a CLS sa overujú existujúcim explicitným katalógovým contextom. |
| Designation | AUTHORITATIVE / DEFERRED | Accepted model pozná `Designation` ako vlastnený Value Object, ale jeho serializačný kontrakt nie je implementovaný a nie je povinnou súčasťou minimálneho Material profilu. |
| Material condition | OPEN / RESTRICTED FOR V1 | Accepted architektúra neurčuje univerzálne, či dodací stav alebo tepelné spracovanie mení MAT identitu. V1 preto nesmie takúto identitu serializovať ani predstierať. |
| Norm linkage | DEFERRED | Material môže konceptuálne referencovať NormReference, ale presné pole, kardinalita a runtime entity resolver nie sú uzavreté pre v1. |
| Chemické zloženie | DEFERRED | Neexistuje prijatý composition contract ani pravidlá pre element, zvyšok, rezíduá a specification-versus-observation. |
| Equivalence | DEFERRED | Ekvivalencia externých označení alebo materiálov sa nesmie odvodiť z názvu, designation ani podobných vlastností. |

Draft EOS-004 obsahuje starší širší návrh s povinným `designation` a `materialGroup`. Accepted RFC-0001 až RFC-0003 a aktuálna implementačná postupnosť sú pre tento review rozhodujúce; CDR-0015 nemení Draft EOS-004 ani z neho nepreberá neimplementované polia.

## 5. Material Domain Meaning

`Material` reprezentuje jeden stabilný EOS znalostný koncept materiálu. Môže niesť tvrdenia o technických vlastnostiach, riadené klasifikačné priradenia a provenance vlastnej definície.

Material nie je:

- fyzický kus, výrobná dávka, tavba alebo šarža;
- skladová tyč, plech, rúra alebo iná geometrická forma;
- supplier-specific produkt, ponuka, cena alebo dostupnosť;
- výrobný proces, heat-treatment operation alebo výsledok merania;
- norma, designation, katalógová položka alebo PropertyRecord.

Fyzický a komerčný kontext patrí budúcemu `StockMaterial`, inventory/procurement vrstvám alebo samostatným evidence objektom.

## 6. Object Type / Aggregate Boundary

Material je súčasne:

- Knowledge Entity v Engineering Knowledge Layer;
- Entity so stabilnou identitou a vlastným lifecycle;
- Aggregate Root pre svoje embedded claims a classifications.

Nie je Value Object, Reference Object ani Catalog Entry. Je samostatne uložený, revidovaný, source-backed a referencovateľný inými aggregate roots. Môže vlastniť Value Objects, ale nesmie vlastniť iný Aggregate Root.

## 7. MAT Identifier Semantics

`MAT-xxxx` identifikuje práve jednu stabilnú Material entity. Vlastné ID pole sa má volať `id`, v súlade so spoločnou entity konvenciou. Referencia z iného objektu sa môže volať `materialId`.

MAT neidentifikuje stock form, fyzický kus, batch, heat number, supplier offer, material condition, designation, Classification ani PropertyRecord. Prefix je už Active v EOS-003 a centralizovaný v identifiers schéme; nový prefix nie je potrebný.

## 8. Aggregate Ownership

| Objekt | Rozhodnutie pre v1 | Dôvod |
| --- | --- | --- |
| `PropertyRecord[]` | OWNED EMBEDDED VALUE | Claim-like Value Objects patria do transakcie a revízie Materialu. |
| `Classification[]` | OWNED EMBEDDED VALUE | Material vlastní konkrétne CLS assignments, nie katalógové položky. |
| root `SourceLink[]` | OWNED EMBEDDED VALUE | Súčasť common metadata a provenance definície Materialu. |
| root `Condition[]` | DEFERRED | RFC vlastníctvo povoľuje, ale root-level význam a vzťah k identity nie sú uzavreté; v1 používa Conditions iba v PropertyRecord. |
| `Observation[]` | SEPARATE AGGREGATE | Observation sa vyhľadáva podľa `subjectId`; nesmie sa vnárať. |
| `NormReference[]` | REFERENCED / DEFERRED FIELD | Samostatný Reference Object; v1 nepridáva neuzavreté pole. |
| `DocumentRecord[]` | SEPARATE AGGREGATE | Dokument nie je vlastnená časť Materialu. |
| Supplier údaje | REJECTED | Generic Material nie je supplier-specific. |
| `StockMaterial[]` | SEPARATE AGGREGATE | Budúci StockMaterial referencuje Material, nie naopak cez vlastnené pole. |
| `Designation[]` | DEFERRED | Accepted koncept bez hotového serializačného kontraktu. |

## 9. PropertyRecord Relationship

Odporúčané pole je `properties`, pole existujúcich PropertyRecord objektov. Je voliteľné a môže byť prázdne, aby vznik Material Draft nevyžadoval okamžité technické tvrdenia.

PropertyRecord vlastní Material. Zmena PropertyRecord je zmenou Material aggregate a musí sa auditovať cez jeho versioning. PropertyRecord si zachováva vlastné `verificationStatus` a `sourceLinks`; root `status` ich nenahrádza.

Rovnaké `propertyId` sa môže vyskytnúť viackrát. Legitímne dôvody sú rozdielne Conditions, zdroje, hodnoty, verification status alebo paralelné a konfliktné claims. JSON Schema nesmie zaviesť jednoduché `uniqueItems` alebo unikátnosť podľa PRP. Presná duplicate/conflict policy patrí neskoršej aplikačnej a Decision vrstve.

## 10. Classification Relationship

Odporúčané pole je `classifications`, voliteľné pole existujúcich Classification Value Objects. Môže byť prázdne a môže obsahovať viac CLS assignments.

Material vlastní assignments, nie Classification Catalog Entries. `Classification.sourceLinks` dokazujú konkrétne zaradenie Materialu; sourceLinks katalógovej položky dokazujú definíciu CLS významu. V1 nevynucuje CLS target applicability, hierarchiu, systém ani assignment multiplicity. Jednoduchý zákaz opakovania CLS sa nezavádza bez dohodnutej assignment policy.

## 11. Observation Relationship

Material nesmie obsahovať `observations` ani `observationIds`. Observation je samostatný Aggregate Root a môže mať `subjectId` vo formáte MAT. Pozorovania sa majú objavovať cez repository/query podľa subjektu, nie cez rastúci spätný zoznam v Materiale.

Jedna Observation môže podporovať budúce rozhodnutie o claims, ale nikdy sa automaticky nestáva PropertyRecord ani nemení Material aggregate.

## 12. Root Source Provenance

`sourceLinks` je povinné root pole zo spoločných entity metadát.

Root provenance podporuje identitu, definíciu, pomenovanie a hranicu konkrétneho Material záznamu. Nepreukazuje automaticky každú hodnotu PropertyRecord, správnosť Classification assignment ani obsah Observation.

Draft môže mať `sourceLinks: []`. Material v stave Review alebo Approved musí mať najmenej jeden relevantný root SourceLink, pretože aj tvrdenie, že konkrétny EOS záznam predstavuje určitý materiálový koncept, je overiteľné. Toto je application validation pravidlo; SourceLink štruktúra sa znovu používa bez duplikácie.

## 13. Lifecycle

Material používa spoločný entity `RecordStatus`: `Draft`, `Review`, `Approved`, `Deprecated`, `Archived`. Lifecycle vyjadruje zrelosť a použiteľnosť Material záznamu.

Lifecycle nevyjadruje heat treatment, delivery condition, fyzický stav, verification konkrétneho property claim ani pravdivosť Observation. Archived alebo Deprecated Material zostáva auditovateľný; fyzické mazanie schváleného záznamu nie je doménová operácia.

## 14. Name Model

`name` je REQUIRED NOW, neprázdny human-readable kanonický EOS label. Nie je identita, externé označenie ani schema-level unikátna hodnota. Zmena názvu bez zmeny významu môže byť revision; zmena názvu odhaľujúca zmenu identity alebo významu je recordVersion zmena alebo nový Material podľa governance posúdenia.

## 15. Designation Model

V1 nemá pole `designation`, `primaryDesignation`, `designations`, `externalDesignations`, `aliases`, `code` ani `standardDesignation`.

Accepted RFC pozná `Designation` ako budúci embedded Value Object, ale bezpečný kontrakt musí spájať hodnotu aspoň so systémom alebo autoritou, platnosťou a podľa pôvodu so zdrojmi. Jeden voľný string by vytváral falošnú jednoznačnosť a mohol by naznačiť neoverenú ekvivalenciu.

Designation je DEFERRED, nie zamietnutý navždy. Jeho zavedenie potrebuje samostatný pre-design alebo prijatý reusable contract.

## 16. Name vs Designation

`name` je interný čitateľný EOS label Material entity. Designation je externým alebo riadeným systémom pridelené označenie. Name sa nesmie interpretovať ako designation a designation sa nesmie použiť ako MAT identita.

V1 môže bezpečne fungovať iba s `name`; nesmie však tvrdiť štandardovú ekvivalenciu ani importovať reálne designation dáta.

## 17. Description

`description` je OPTIONAL NOW. Slúži na stručné vysvetlenie hranice Material konceptu. Nesmie nahrádzať PropertyRecord, Classification, Condition, designation, normovú väzbu ani source citation.

## 18. Standards / Norm Boundary

V1 používa root a claim-level SourceLink pre provenance. Nepridáva `normReferenceIds`, embedded NormReference ani voľný názov normy.

NormReference je samostatný Reference Object a Accepted architektúra povoľuje budúcu referenciu z Materialu. Presné pole, kardinalita, význam designation-system väzby a runtime entity resolver však nie sú v prvom profile potrebné. Zdroj dokazujúci Material definíciu, normatívny systém označenia a zdroj jednotlivého property claim sú rozdielne väzby a nesmú sa zlúčiť.

## 19. Chemical Composition Boundary

V1 nevytvára `chemicalComposition` ani špecializovaný MaterialComposition objekt. Voľný text alebo notes sa nesmú používať ako autoritatívne chemické zloženie.

Jednotlivé jednoduché numeric composition claims môžu byť v budúcnosti vyjadrené PropertyRecord iba vtedy, keď existujú riadené PRP, UNT a potrebné CND významy. Generic PropertyRecord sám nerieši element identity, basis, residuals, balance element, súčet, specification-versus-observation ani komplexné pravidlá zloženia. Reálne chemické zloženie je preto pre onboarding v1 deferred.

## 20. Material Condition / Delivery State

V1 nemá root pole `condition`, `materialCondition`, `deliveryState`, `temper` ani ekvivalent. Conditions sa môžu používať iba vnútri PropertyRecord na kvalifikovanie platnosti konkrétneho claim.

Počiatočný MAT profil je condition-neutral: stabilná identita neobsahuje serializovaný delivery alebo heat-treatment state. To neznamená tvrdenie, že stav nikdy nemení materiálový koncept; znamená to, že také prípady nie sú v1 modelovateľné ako reálne dáta.

## 21. Heat Treatment vs Identity

Accepted architektúra neurčuje univerzálne pravidlo, kedy heat treatment mení vlastnosti, StockMaterial stav, výrobný výsledok alebo samotnú Material identitu. CDR preto neprijíma univerzálnu odpoveď.

Bezpečné pravidlo v1 je:

1. heat-treatment process sa neukladá do Materialu;
2. condition-dependent property môže používať nested Conditions;
3. fyzický stav konkrétnej zásoby patrí budúcemu StockMaterial alebo výrobnému záznamu;
4. reálny koncept, ktorého identita je neoddeliteľná od condition, sa nesmie onboardovať, kým samostatné rozhodnutie neurčí identity boundary.

Toto obmedzenie zabraňuje tomu, aby jedno MAT súčasne znamenalo všetky stavy aj jeden presný stav.

## 22. Material Family / Classification

V1 nepridáva `materialType`, `materialFamily`, `materialGroup`, `category`, `class` ani ad-hoc enum. Riadené zaradenie sa vyjadruje cez `Classification` a CLS.

Classification Catalog v1 zatiaľ nemodeluje target applicability, systém, external code ani hierarchiu. Material validácia preto overí existenciu a lifecycle CLS, nie to, či je konkrétna kategória materiálovo vhodná.

## 23. Property Catalog Interaction

Každý vnorený PropertyRecord používa existujúcu validačnú kompozíciu:

1. PRP musí existovať v `CatalogRegistry` a byť správneho typu;
2. lifecycle musí povoľovať použitie;
3. value type musí patriť do `allowedValueTypes`;
4. výsledné UNT musí patriť do `allowedUnitIds`;
5. Conditions musia rešpektovať PRP CND allow-list;
6. každá Condition sa validuje proti CND a každá Quantity/ValueRange proti UNT.

Material nesmie túto logiku kopírovať ani zaviesť vlastný property compatibility engine.

## 24. Classification Catalog Interaction

Každá vnorená Classification znovu používa existujúcu kontrolu CLS existencie, typu a lifecycle. V1 nepridáva Material-specific applicability, hierarchy, system/code mapping, equivalence ani assignment multiplicity pravidlá, pretože ich Classification Catalog ešte neobsahuje.

## 25. StockMaterial Boundary

| Material vlastní alebo opisuje | StockMaterial vlastní alebo bude opisovať |
| --- | --- |
| stabilný engineering material concept | skladovú, dodávateľskú alebo používanú formu |
| source-backed všeobecné PropertyRecord claims | form-specific properties a rozmery |
| riadené Classification assignments | stock form, geometry a dimensions |
| provenance identity a definície | Supplier referenciu a supplier-specific designation |
| vlastný entity lifecycle a revízie | lot, batch alebo heat kontext, ak ho budúci návrh prijme |
| condition-neutral v1 hranicu | availability, commercial a procurement kontext |

StockMaterial bude Material iba referencovať cez `materialId`. Material nesmie absorbovať skladovú geometriu, dostupnosť alebo nákupné údaje preto, že sa používajú pri obrábaní.

## 26. Supplier Boundary

Material v1 neobsahuje `supplierId`, `supplierIds`, `manufacturer`, `producer` ani vendor designation. Generic Material nie je supplier-specific produkt. Dodávateľská identita, ponuka a komerčné označenie patria budúcemu StockMaterial, commercial record alebo first-class relationship, ak väzba neskôr potrebuje vlastný audit.

## 27. ManufacturingProcess Boundary

Material neobsahuje zoznam compatible/prohibited processes, heat-treatment recipes ani machinability rules. ManufacturingProcess je samostatný Aggregate Root. Budúca kompatibilita alebo odporúčanie môže byť relationship, capability, rule, PropertyRecord s presným významom alebo odvodený výsledok, ale nie voľné pole v Material v1.

## 28. Machine / CuttingTool Boundary

Material nevlastní machine compatibility, CuttingTool recommendations, feeds, speeds, machining time ani cost. Tieto významy patria budúcim capability, calculation, recommendation, quotation alebo manufacturing vrstvám.

## 29. Properties vs Requirements

Material PropertyRecord vyjadruje source-backed claim o Material koncepte. Nie je design requirement pre part, výrobná tolerancia, acceptance limit ani nameraná Observation.

Requirement/tolerance model zostáva deferred a nesmie sa nahradiť ValueRange alebo MeasurementQuality bez prijatého kontraktu. Observation zostáva evidence a PropertyRecord claim.

## 30. Root Verification Status

Material root nemá `verificationStatus`. Root `status` riadi lifecycle entity. Každý PropertyRecord má vlastný claim verification status a každý SourceLink vlastný stav overenia väzby. Pridanie root verification status by miešalo zrelosť entity s overením jednotlivých tvrdení.

## 31. Versioning / Revision Ownership

Material znovu používa common metadata:

- `id`, `schemaVersion`, `recordVersion`, `revision`, `status`;
- `createdAt`, `createdBy`, `updatedAt`, `updatedBy`;
- `sourceLinks`, `changeSummary`.

Zmena významu, property setu, Classification assignmentu alebo provenance ovplyvňujúcej interpretáciu zvyšuje `recordVersion`. Formálna oprava bez zmeny významu zvyšuje `revision`. `schemaVersion` sa mení pri verzii serializačného kontraktu, nie pri zmene jedného Material záznamu.

## 32. Property Claim History

Zmena embedded PropertyRecord mení Material aggregate. Starý claim sa nemá ticho prepisovať. Zachovanie starších Material verzií patrí persistence a audit vrstve; v1 JSON objekt nemusí obsahovať interné pole histórie.

Schválený conflict alebo nový zdroj má viesť k auditovanej Material verzii, nie k mutácii bez `changeSummary`.

## 33. Material Equivalence Boundary

V1 nemá `equivalentTo`, `sameAs`, aliases ani mapovanie externých grade/designation systémov. Podobný názov, vlastnosti alebo classification nepreukazujú ekvivalenciu. Ekvivalencia a near-equivalence potrebujú zdroje, scope, conditions, audit a pravdepodobne samostatné governance pravidlo alebo Relationship.

## 34. Replacement / Supersession

Voliteľné `replaces` a `replacedBy` sú povolené, pretože ich common entity metadata poznajú a RFC-0002 výslovne povoľuje replacement/supersession Materialu. V Material kontrakte musia byť zúžené na `MAT-xxxx`.

Neznamenajú ekvivalenciu. Existencia cieľa, self-reference, obojsmerná konzistencia a cykly potrebujú budúci entity resolver alebo persistence integrity; automatické nasledovanie náhrady je zakázané.

## 35. Duplicate Property Claims

Viac PropertyRecord s rovnakým `propertyId` je v1 povolených. Schema-level zákaz by zničil condition-specific, source-specific alebo paralelné claims. Katalóg zatiaľ nemodeluje multiplicitu ani uniqueness scope.

Úplne identické položky môžu byť v budúcnosti warning alebo governance finding, ale v1 ich neodmieta bez prijatého pravidla.

## 36. Conflicting Claims

Konfliktné PropertyRecord môžu koexistovať. Každý si zachová hodnotu, Conditions, sourceLinks a verificationStatus. EOS ich nesmie ticho zlúčiť, vybrať priemer ani prepísať „novším“ tvrdením.

Rozhodnutie o preferovanom alebo autoritatívnom claim patrí budúcemu Decision alebo explicitne schválenému governance mechanizmu.

## 37. Observation-to-Claim Promotion

Observation s `subjectId` MAT je evidence. Nevytvára ani nemení `Material.properties` automaticky. Promotion do PropertyRecord vyžaduje Decision alebo ekvivalentný schválený proces; samostatný stored Decision contract nie je podmienkou pre Material schema, ale automatická promotion je zakázaná.

## 38. Candidate Field Inventory

| Pole | Rozhodnutie | Odôvodnenie |
| --- | --- | --- |
| `id` | REQUIRED NOW | Stabilné MAT ID. |
| common entity metadata | REQUIRED NOW | Lifecycle, audit, versioning a root provenance. |
| `name` | REQUIRED NOW | Neprázdny EOS label. |
| `description` | OPTIONAL NOW | Stručná hranica konceptu. |
| `sourceLinks` | REQUIRED NOW | Súčasť common metadata; obsah lifecycle-aware. |
| `properties` | OPTIONAL NOW | Vlastnené PropertyRecord claims. |
| `classifications` | OPTIONAL NOW | Vlastnené Classification assignments. |
| `notes` | OPTIONAL NOW | Neautoritatívna poznámka. |
| `replaces`, `replacedBy` | OPTIONAL NOW | Priame MAT replacement odkazy, nie equivalence. |
| `designation`, `designations` | DEFER | Chýba reusable Designation contract a authority model. |
| `observations`, `observationIds` | REJECT | Observation je samostatný Aggregate Root; query podľa subjectu. |
| root `conditions` | DEFER | Neuzavretý root význam a identity boundary. |
| `materialType`, `materialFamily` | REJECT | Použiť Classification, nie ad-hoc enum. |
| `standards`, `normReferenceIds` | DEFER | Neuzavretá kardinalita a entity resolution. |
| `chemicalComposition` | DEFER | Chýba composition model. |
| `supplierIds`, `stockForms` | REJECT | Patria StockMaterial/commercial vrstve. |
| root `verificationStatus` | REJECT | Overenie je na claims a SourceLinks. |
| `equivalentTo`, `sameAs`, `aliases` | DEFER | Ekvivalencia nesmie byť implicitná. |

## 39. Candidate Models

### Candidate A – minimal identity entity

Common metadata, MAT `id`, `name`, root `sourceLinks`.

- Silná minimalita a bezpečný Draft.
- Neumožňuje niesť znalostné claims ani classifications a nenapĺňa cieľ prvej reusable Knowledge Entity.
- Vhodný ako minimum platného záznamu, nie ako celý kontrakt.

### Candidate B – knowledge-bearing Material

Candidate A + optional `description`, `properties`, `classifications`, `notes`, `replaces`, `replacedBy`.

- Zachováva evidence/claim hranicu a používa hotové core contracts.
- Je kompatibilný s budúcim StockMaterial cez MAT referenciu.
- Umožňuje paralelné a konfliktné claims bez predčasnej doménovej ontológie.
- Nevyžaduje nový resolver ani nový core contract.
- Odporúčaný v1 model.

### Candidate C – designation-aware Material

Candidate B + jeden voľný `designation`.

- Vyzerá prakticky, ale skrýva systém, autoritu, platnosť a multiplicitu.
- Vytvára vysoké riziko falošnej ekvivalencie a konflikt s budúcim Designation contractom.
- Neodporúča sa pre v1.

### Candidate D – state-aware standards Material

Candidate B + root Conditions, designations, norm references a chemistry.

- Mohol by pokryť širšiu doménu, ale potrebuje viac neexistujúcich kontraktov a identity rozhodnutí.
- Je predčasný a blokoval by prvú entity implementáciu.

## 40. Recommended Minimal Model

Odporúča sa Candidate B:

```json
{
  "id": "MAT-9001",
  "schemaVersion": "0.1.0",
  "recordVersion": "0.1.0",
  "revision": 0,
  "status": "Draft",
  "createdAt": "...",
  "createdBy": "...",
  "updatedAt": "...",
  "updatedBy": "...",
  "sourceLinks": [],
  "changeSummary": "...",
  "name": "Fictional material concept",
  "properties": [],
  "classifications": []
}
```

Príklad je výhradne fiktívny a nepredstavuje technické dáta. Povinné sú common metadata, MAT `id` a neprázdny `name`. Voliteľné sú `description`, `properties`, `classifications`, `notes`, `replaces` a `replacedBy`. Unknown fields musia byť odmietnuté.

## 41. Minimum Useful Material

Platný Material môže mať bez PropertyRecord a bez Classification iba common metadata, MAT `id`, neprázdny `name` a root `sourceLinks`. Draft môže mať prázdne sourceLinks. Review/Approved vyžaduje root provenance.

Toto minimum podporuje postupné authoring a vytvára auditovateľnú identitu bez falošného technického obsahu. Prázdny objekt alebo záznam bez name nie je Material. Properties ani classifications sa nesmú vynútiť iba na vytvorenie dojmu „užitočnosti“.

## 42. Reference Integrity

V1 potrebuje:

- schema kontrolu MAT formátu vlastného `id`;
- existenciu a typ PRP/CND/UNT/CLS cez existujúci CatalogRegistry pri context-aware validácii;
- budúcu MAT referenčnú integritu pre `replaces`/`replacedBy`, ktorá môže zostať deferred, kým neexistuje entity resolver.

Material nepotrebuje nový generic resolver na validáciu svojich embedded Knowledge Core objektov. Root SourceReference existencia a prípadné MAT replacement targets zostávajú explicitne neoverené existujúcim katalógovým contextom.

## 43. Context-aware Validation

Budúca implementácia má rozšíriť existujúcu validačnú kompozíciu:

```text
Material schema
  -> Material-local application invariants
  -> each properties[i] as PropertyRecord
  -> each classifications[i] as Classification
  -> existing reference_integrity/catalog_validation with ValidationContext
```

`validate_with_context(...)` má znovu použiť existujúce reusable helpery a zachovať presné cesty, napríklad `$.properties[1].quantity.unitId` alebo `$.classifications[0].classificationId`. Nemá vzniknúť druhý catalog validator. Contract-only validácia nesmie tvrdiť runtime existenciu katalógových cieľov.

## 44. Provenance Matrix

| Úroveň | Čo sourceLinks dokazujú | Čo nedokazujú |
| --- | --- | --- |
| Material root | identitu, definíciu, pomenovanie a hranicu MAT konceptu | každú property hodnotu, assignment alebo meranie |
| PropertyRecord | konkrétny technický claim a jeho hodnotu/interpretáciu | existenciu Material identity všeobecne |
| Classification | konkrétne priradenie Materialu ku CLS | autoritatívnu definíciu CLS položky |
| Classification Catalog Entry | definíciu a pôvod CLS významu | že konkrétny Material do kategórie patrí |
| Observation | pôvod a kontext konkrétneho evidence záznamu | automatické prijatie claim do Materialu |

Rovnaký SourceReference môže byť použitý na viacerých úrovniach iba cez samostatné SourceLinks s presným supported claim/field a interpretáciou.

## 45. Real Data Boundary

Tento review nevytvára žiadny reálny Material, designation, property, klasifikáciu, normovú väzbu ani chemické zloženie. Implementačný míľnik musí používať iba fiktívne vysoké testovacie ID a netechnické hodnoty.

Platná schéma ani zelený test nesmú byť interpretované ako schválenie konkrétneho materiálového údaja.

## 46. Future Real-data Requirements

Onboarding reálneho Material bude vyžadovať minimálne:

- autoritatívne SourceReference a presné root SourceLinks;
- prijatý Designation model alebo explicitné rozhodnutie, že daný zdrojový koncept designation nepotrebuje;
- rozhodnutie o grade versus condition identity pre daný typ materiálu;
- riadené PRP, UNT, CND a CLS entries;
- source-backed properties, Conditions a classifications;
- review ekvivalencie bez automatického mapovania;
- oddelenie specification claims od Observation evidence;
- governance schválenie a audit verzií.

## 47. Validation Responsibility

| Vrstva | Zodpovednosť |
| --- | --- |
| JSON Schema | uzavretý tvar, required, MAT pattern, typy, common metadata, embedded `$ref`, replacement MAT formát |
| EOS application validation | Review/Approved root source rule, lokálne invariants, rekurzívne semantic pravidlá |
| Nested Knowledge Core | PropertyRecord, Classification, Condition, ValueRange a MeasurementQuality pravidlá |
| `reference_integrity` | existencia a typ PRP/CND/UNT/CLS v explicitnom registry snapshote |
| `catalog_validation` | lifecycle a property/unit/condition/classification kompatibilita dostupná vo v1 katalógoch |
| Workflow/governance | schválenie, oprávnenia, promotion evidence, conflict resolution, replacement rozhodnutie |
| Persistence | uniqueness MAT, optimistic locking, historické verzie, referenčné a transakčné invarianty |
| Future Decision | prijatie/odmietnutie Observation alebo konfliktného claim |

## 48. Risks

| Priorita | Riziko | Mitigácia |
| --- | --- | --- |
| Critical | Material sa zmení na StockMaterial alebo fyzický lot. | Zakázať supplier, stock form, geometry, availability a batch polia. |
| Critical | Condition-dependent identity sa začne hádať z názvu. | V1 condition-neutral; reálne závislé koncepty neonboardovať. |
| High | Voľný designation vytvorí falošnú ekvivalenciu. | Designation v1 vynechať. |
| High | Observation sa vloží do Materialu alebo prepíše claim. | Query podľa subjectId; promotion iba cez Decision/governance. |
| High | Duplicitné PRP sa mechanicky zmažú. | Povoliť paralelné claims a zachovať provenance/conditions. |
| High | Konfliktné claims sa ticho zlúčia. | Zachovať ich samostatne; rozhodnutie odložiť. |
| High | Root verificationStatus duplikuje claim verification. | Root používa lifecycle; verification ostáva na claims/links. |
| Medium | Chemical composition sa sploští do textu. | Deferred composition; notes nie sú autoritatívne dáta. |
| Medium | Supplier údaje preniknú do generic Materialu. | Presunúť do StockMaterial/commercial vrstvy. |
| Medium | Classification sa preťaží designation alebo condition významom. | CLS používať iba pre riadené kategórie dostupné v katalógu. |
| Medium | Material sa stane kontajnerom machining recommendations. | Proces/tool/machine/cost údaje odmietnuť. |
| Medium | Contract-only výsledok sa vydá za catalog-aware validáciu. | Plné tvrdenie iba cez explicitný ValidationContext. |
| Low | Prázdne optional polia zvyšujú šum. | Ak sú povolené, nemajú niesť sémantiku; API môže prázdne polia vynechať. |

## 49. Deferred Concepts

- reusable `Designation` contract, systémy označení, aliasy a lokalizácia;
- grade/designation equivalence a near-equivalence;
- root MaterialCondition, delivery state, temper a heat-treatment identity policy;
- špecializovaný chemical composition model;
- structured NormReference väzba a entity resolver;
- CLS target applicability, hierarchy a system/external-code semantics;
- PRP required Conditions, multiplicita a claim uniqueness policy;
- generic entity resolver a MAT/SRC referenčná integrita;
- persistence, historical snapshots a replacement graph integrity;
- Decision contract a workflow conflict resolution;
- StockMaterial, Supplier a commercial/inventory model;
- reálna materiálová populácia a import.

## 50. Implementation Preconditions

Material implementácia môže začať iba pri zachovaní týchto podmienok:

1. Material zostane knowledge concept, nie fyzický alebo komerčný objekt.
2. `id` bude používať existujúce `MAT-xxxx` a Material bude Aggregate Root.
3. V1 bude condition-neutral a nebude onboardovať reálny koncept závislý od material condition.
4. Designation, root Conditions, structured norm linkage a chemistry zostanú mimo v1.
5. Povinné polia budú common metadata, MAT `id` a neprázdny `name`.
6. `properties` a `classifications` budú voliteľné owned collections existujúcich kontraktov.
7. Observation sa nebude vnárať ani ukladať ako back-reference array.
8. Root sourceLinks budú required; Draft môže byť prázdny, Review/Approved nie.
9. Root nebude mať `verificationStatus`.
10. Rovnaké PRP a konfliktné claims sa nebudú schema-level zakazovať ani automaticky riešiť.
11. Context-aware validácia znovu použije existujúce PRP/CND/UNT/CLS helpery bez duplicity.
12. `replaces`/`replacedBy` budú iba voliteľné MAT odkazy a nebudú znamenať equivalence.
13. Fixtures zostanú fiktívne a nevzniknú reálne Material dáta.
14. Accepted RFC a ADR sa nezmenia.

Ak sa má do prvého kontraktu pridať designation alebo condition-dependent identity, treba najprv samostatne uzavrieť príslušný contract/architecture problém. Nemožno ich doplniť ako neštruktúrovaný string.

## 51. Readiness Verdict

Material má autoritatívne určený význam, MAT identitu, aggregate boundary, ownership PropertyRecord a Classification, oddelenie Observation, root provenance a hranicu voči StockMaterial. Existujúce katalógy a validačný runtime postačujú pre vnorené Knowledge Core objekty bez generic entity resolvera.

Implementácia je bezpečná iba ako obmedzený condition-neutral profil bez designation, root MaterialCondition, structured norm linkage, špecializovanej chémie a reálnych materiálových dát. Tieto obmedzenia sú explicitné a nevyžadujú zmenu Accepted architektúry; ich porušenie by však vytvorilo nekompatibilné identity modely.

## 52. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-10-04 | 0.1 | 0 | Codex | Initial Material entity pre-design review defining the restricted v1 aggregate, ownership, provenance, catalog-validation reuse, StockMaterial boundary and deferred condition/designation semantics. |

READY WITH CONDITIONS
