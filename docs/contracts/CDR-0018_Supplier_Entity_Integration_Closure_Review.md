# CDR-0018 Supplier Entity Integration Closure Review

Project: EOS – Engineering Operating System
Contract Review ID: CDR-0018
Review: Supplier Entity Integration Closure
Review type: Closure
Phase: 0.2C.2-close
Version: 0.1
Revision: 1
Status: Review
Document basis: Accepted EOS architecture + CDR-0017 + Supplier v1 implementation
Author: Codex
Review date: 2026-10-14

Aktuálny stav Revision 1: SEC-0001/0002/0003 CLOSED; Phase 0.2C.2 COMPLETE. Corrective dôkazy a opakované kritériá sú v §62. Sekcie 1–60 a pôvodný riadok histórie zachovávajú Review Revision 0 vrátane vtedajších otvorených findings a verdictu; nejde o aktuálne otvorené úlohy.

## 1. Purpose

Posúdiť zachovanie SI-0001, aggregate hraníc a spoločnej validácie Supplier v1 a rozhodnúť o formálnom uzavretí Phase 0.2C.2. Review neposudzuje kvalifikáciu reálnych dodávateľov ani nenavrhuje ďalšiu entitu.

## 2. Scope

Prvý review pass nemení implementáciu, schémy, testy, fixtures, závislosti ani historické dokumenty. Jediným novým repozitárovým súborom je tento CDR. ManufacturingProcess sa nenavrhuje ani neimplementuje. Rozlišujeme serializačný kontrakt, aplikačné pravidlá, katalógovú validáciu a ľudské overenie identity.

## 3. Reviewed Artifacts

Vstup: `feature/phase-0.2c-knowledge-entities`, tracking `origin/feature/phase-0.2c-knowledge-entities`, HEAD `adbc8c762bfac4e4e90d1df12eef5534b3d2eb70` (`Implement Supplier entity v1`). `git status`, `git branch --show-current`, `git branch -vv` a `git log --oneline -15` potvrdili čistý strom a zhodu HEAD s lokálnym origin tracking ref. To samo nepredstavuje nové načítanie vzdialeného servera.

CDR-0017 existuje v Revision 2 s verdictom `READY FOR SUPPLIER CLOSURE REVIEW`; SI-0001 je CLOSED. Entity adresár obsahuje iba Material a Supplier. ManufacturingProcess, StockMaterial, generic entity resolver ani reálne Supplier záznamy neboli zavedené.

Preverené zdroje:

- `AGENTS.md`; governance EOS-000 a EOS-003/006/007/009/010; relevantný starší Draft EOS-004 pri vyhľadávaní single-role modelu.
- Accepted RFC-0001 (PropertyRecord, Classification, evidence), RFC-0002 (Entity, Aggregate Root, Supplier §4.6, Classification, §16), RFC-0003 (identity, Knowledge Entity, G-0049, aggregate boundaries).
- ADR-0010/0012 (closed contracts, central identity), Accepted ADR-0013/0015/0016 (štandardný validátor, Knowledge Layer, Observation).
- CDR-0017 najmä §44–48, §60–61; Material precedent CDR-0015 §50–52 a CDR-0016 vrátane corrective closure §54.
- Obe `schemas/entities/` schémy, všetkých sedem `schemas/knowledge-core/` a štyri `schemas/catalogs/` schémy; common identifiers, metadata, lifecycle a skutočný `schemas/common/source-link.schema.json`; schema index.
- `scripts/validation/__init__.py`, `catalog_context.py`, `validator.py`, `schema_loader.py`; runtime diff `736820b..adbc8c7`.
- `tests/test_validation.py`, `tests/test_catalog_validation.py`, celý `tests/test_supplier_validation.py`, entity fixtures a `tests/fixtures/catalog-context/fictional-catalog-context.json`.
- Aktuálne aj relevantné historické časti schemas/scripts/tests README, CHANGELOG, ROADMAP a celý BACKLOG.

Baseline: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` — **260 tests, 31.208 s, OK; 0 failures, 0 errors, 0 skipped**. Jednorazové read-only probes nemenili testovú sadu ani fixtures.

## 4. Supplier Domain Review

**PASS.** Identity-focused Knowledge Entity pre právne samostatnú organizáciu v dodávateľskej roli. Schéma nemá site, vendor account, offer, capability, certification, contact ani procurement polia. Nezistil sa semantic leakage. Validátor neanalyzuje význam voľného textu; zákaz používať notes ako skrytý obchodný model je autorské pravidlo, nie implementovaná NLP kontrola.

## 5. SUP Identity Review

**PASS.** `SUP-xxxx`, presne štyri číslice, `^SUP-[0-9]{4}$`. Supplier odkazuje výlučne na `https://eos.local/schemas/common/identifiers.schema.json#/$defs/SUP`; lokálny regex nemá. EOS-003, RFC-0002 §16, G-0049 a CDR-0017 §60 sú konzistentné. Malformed, padding, lowercase, wrong-prefix a null fixtures zlyhávajú na `$.id` zo správneho dôvodu.

## 6. SI-0001 Preservation

**PASS.** Jeden SUP = jedna právne samostatná organizácia. Ďalšia prevádzka, rola, vendor účet či ponuka sama nemení SUP. Premenovanie pri zachovaní právnej kontinuity zachováva identitu. Iný právny subjekt potrebuje odlišnú identitu. Sole traders zostávajú mimo v1. Schéma neimplementuje právnu deduplikáciu ani nepotvrdzuje skutočnú právnu identitu; CDR-0017 to ani nevyžaduje.

## 7. Object Type / Aggregate Root

**PASS.** Vlastné `id`, `revision`, lifecycle, audit metadata a root provenance. Supplier nie je Catalog Entry, Value Object ani owned child. Vlastní iba hodnoty Classification assignments, nevnára cudzie Aggregate Roots.

## 8. Common Metadata

**PASS.** `schemaVersion`, `recordVersion`, `revision`, `status`, `createdAt`, `createdBy`, `updatedAt`, `updatedBy`, `sourceLinks`, `changeSummary` a optional `notes` používajú property-level common refs rovnako ako Material. Bez Supplier-local metadata constraints alebo lifecycle enumu. Identita používa central SUP ref.

## 9. Lifecycle Boundary

**PASS.** Draft/Review/Approved/Deprecated/Archived sú stavy EOS záznamu, nie kvalifikácia, preferred/blocked vendor ani právna aktivita spoločnosti. Root lifecycle test pokrýva všetkých päť stavov; Qualified, ActiveVendor a Accepted sú odmietnuté. Business approval fields sú neznáme polia.

## 10. Root Provenance

**PASS pre význam a platnosť; diagnostická duplicita SEC-0002.** Required `sourceLinks` reuse-nuje common SourceLink. Draft môže byť prázdny; Review/Approved vyžaduje neprázdne zdroje aplikačne. SRC formát nedokazuje existenciu zdroja alebo jeho pravdivosť.

| Provenance | Čo podporuje | Čo nenahrádza |
| --- | --- | --- |
| Supplier.root sourceLinks | Identitu, existenciu a definíciu organizácie | Qualification, capability, certification, site attributes, ceny a terms |
| Classification.sourceLinks | Konkrétne zaradenie rodiča | Root identity evidence či detailnú výrobnú schopnosť |
| Classification Catalog Entry.sourceLinks | Definíciu významu CLS | Dôkaz priradenia CLS Supplierovi |
| Observation.sourceLinks | Zaznamenaný dôkaz v kontexte | Automatické schválenie Supplier alebo claim |
| Budúca qualification/capability/certification provenance | Scoped a časovo vymedzené tvrdenie | Univerzálnu organizačnú schopnosť |
| Budúca offer provenance | Predmet, množstvo, čas a obchodný kontext ponuky | Trvalý atribút Supplier identity |

Assignment zdroje nenahrádzajú root zdroje; test to explicitne dokazuje. V1 neoveruje sémantiku `supportedField` ani obsah zdrojového dokumentu.

## 11. Minimum Supplier

**PASS.** Required: `id`, `schemaVersion`, `recordVersion`, `revision`, `status`, `createdAt`, `createdBy`, `updatedAt`, `updatedBy`, `sourceLinks`, `changeSummary`, `name`. Optional iba `description`, `classifications`, `notes`. Minimálny Draft prejde bez ďalších polí a bez registry v contract-only režime. Inkrementálny zápis je možný.

## 12. Name

**PASS.** Required string, `minLength: 1`; label, nie identita, unique kľúč alebo registračné číslo. Test povoľuje rovnaký názov pri inom SUP a potvrdzuje absenciu normalizácie/mutácie vstupu. `minLength` nie je zákaz whitespace-only názvu; takú normalizáciu kontrakt nesľubuje.

## 13. Description / Notes

**PASS.** Description je optional neprázdny string; notes je optional common string a môže byť prázdny. Dokumentácia ani fixtures nezavádzajú strojový protokol vo voľnom texte alebo náhradu odložených modelov.

## 14. Classification Ownership

**PASS.** Optional 0..N embedded Classification values cez existujúci `$ref`. Supplier vlastní priradenia, nie CLS katalógové položky. Assignment nemá globálne ID ani vlastný record lifecycle.

## 15. Multi-role Organization

**PASS.** Bez single-role enumu, `supplierType`, `isManufacturer`, `isDistributor`, `isServiceProvider`. Multiple fixture má dve odlišné CLS. Contract-only aj authoring context prejdú; default správne odmietne druhú Draft CLS, čo je lifecycle pravidlo, nie zákaz viacerých rolí.

Search našiel `supplierType` v staršom Draft EOS-004 a zamietacej fixture. Počiatočný Draft nie je autoritou pre v1 oproti Accepted RFC a explicitnému CDR-0017. Nebol použitý na implementáciu ani potichu upravený.

## 16. Classification Catalog Integration

**PASS.** Supplier deleguje existujúcemu CLS resolveru: existencia/typ sú `reference_integrity`, lifecycle je `catalog_validation`. Bez Supplier applicability alebo kópie katalógových pravidiel. Doplňujúci probe vykonal všetkých 10 kombinácií piatich CLS stavov a dvoch policies: default prijme Approved/Deprecated, authoring navyše Draft/Review, Archived odmietnu obe. Deprecated je warning s `ok=True` a presnou vnorenou cestou, root SUP a referenced CLS. Trvalá Supplier sada túto celú maticu nepokrýva — SEC-0003.

## 17. PropertyRecord Exclusion

**PASS.** `properties` nie je povolené. `supplier-deferred-properties-invalid.json` vyvolá výhradne `schema_validation.additionalProperties` na `$.properties`; po odstránení poľa prejde. Supplier runtime nevolá PropertyRecord consumer. Nevznikol business key/value kontajner.

## 18. Observation Boundary

**PASS.** `observations` aj `observationIds` sú odmietnuté s explicitnými fixtures. Observation ostáva samostatný Aggregate Root; nezmenený `subjectId` kontrakt prijíma central SUP. Regresný test nepredstiera existenciu referencovaného Supplier ani novú Observation sémantiku.

## 19. Site / Location Boundary

**PASS.** Bez sites/siteIds, locations/locationIds, branches, plants, warehouses a headquarters. Organization-level identita je zachovaná; uvedené polia majú rejection fixtures.

## 20. Address Boundary

**PASS.** Bez address/addresses, street, city, postalCode, country, billingAddress, shippingAddress a registeredAddress. Closed shape a fixtures ich odmietajú; address architecture zostáva deferred.

## 21. Contact / Person Boundary

**PASS.** Bez contacts, contactPerson, contactName, email, phone, contactEmail, contactPhone a persons. Žiadny model osobných údajov ani reálne kontakty.

## 22. External Identifier Boundary

**PASS.** Bez externalId/externalIdentifiers, vendorCode/supplierCode, registrationNumber/companyNumber, taxId/vatNumber a ERP mappings. Scheme-aware identity mappings sú deferred; externé číslo neurčuje SUP identitu.

## 23. Qualification Boundary

**PASS.** Approved/isApproved, approvalStatus, qualificationStatus, preferredSupplier a blockedSupplier sú odmietnuté. Record Approved neznamená approved supplier.

## 24. Certification Boundary

**PASS.** Bez certifications, certificateNumbers, approvals a standardsHeld. Budúci model vyžaduje subjekt, scope, čas a provenance; root identity zdroj ich nenahrádza.

## 25. Capability Boundary

**PASS.** Bez capabilities/capabilityIds, processIds/supportedProcesses, materialsSupported, maxSize, capacity či tolerančných capability polí. Classification kategória nepreukazuje detailnú výrobnú schopnosť. Aj nezahrnuté varianty názvov odmieta closed shape.

## 26. Material Boundary

**PASS.** Supplier nemá materialIds; Material nemá supplierIds a jeho schéma je nezmenená. Žiadne bidirectional convenience arrays ani vlastníctvo cudzieho aggregate.

## 27. StockMaterial Boundary

**PASS.** Bez stockMaterialIds, stockedMaterials, inventory a availableMaterials modelu. StockMaterial schema neexistuje. Supply/inventory vzťah nie je Supplier identity.

## 28. ManufacturingProcess Boundary

**PASS.** Bez procesných zoznamov a service capability modelu. ManufacturingProcess schema ani pre-design nevznikli. Posudzuje sa len pripravenosť na budúci samostatný míľnik.

## 29. Machine / CuttingTool Boundary

**PASS.** Bez machineIds/machines, cuttingToolIds/tools alebo embedding. Uzavretá schéma ich odmieta, fixtures pokrývajú tieto skupiny.

## 30. Commercial Data Boundary

**PASS.** Bez offers, prices, priceList, paymentTerms, currency, Incoterms, MOQ, deliveryTerms, discount, markup, shippingCost a vendor account modelu. Commercial/relationship layer zostáva deferred.

## 31. Lead Time Boundary

**PASS.** Root leadTime výslovne odmietnutý. Budúca hodnota závisí od predmetu, procesu, množstva, času a ponuky; nie je trvalou identitou organizácie.

## 32. Rating / Performance Boundary

**PASS.** Bez rating, qualityScore, deliveryScore, reliability alebo performanceHistory. Aj reliabilityScore odmieta closed shape. Hodnotenie potrebuje budúcu metódu, evidence a čas.

## 33. Replacement / Corporate Relationship Boundary

**PASS.** Replaces/replacedBy, mergedInto, parentSupplierId a successorId sú odmietnuté. Supplier nekopíruje Material replacement fields. Rename, acquisition, kontinuita a duplicate correction zostávajú odlíšené doménové scenáre, nie automatické graph operácie.

## 34. Future Organization Abstraction

**PASS; známe MEDIUM design riziko nezhoršené.** Oddelenie organization identity od sites, rolí a účtov umožňuje budúce explicitné mappings bez zmeny významu SUP. Organization kontrakt ani automatická migrácia nevznikli. Zachovanie SUP a historických odkazov zostáva podmienkou návrhu; nejde o nový SEC finding.

## 35. Generic Entity Resolver

**PASS.** Nevznikol. CatalogRegistry rieši iba UNT/CND/PRP/CLS, nie SUP/MAT/SRC. Supplier nemá nové entity-to-entity väzby, ktoré by ho vyžadovali.

## 36. Validator Dispatch

**PASS.** Explicitný `SUPPLIER_SCHEMA_ID` riadi embedded map, spoločnú root source vetvu a catalog traversal. Žiadna heuristika podľa field presence. CLS algoritmus je zdieľaný. Schema gate pred catalog fázou chráni `enumerate(classifications)` pred nesprávnym typom. Žiadny Supplier business hack.

## 37. Material vs Supplier Entity Pattern

| Mechanizmus | Material | Supplier | Výsledok |
| --- | --- | --- | --- |
| Identity | Central MAT | Central SUP | Rovnaký spôsob, odlišný význam |
| Metadata/lifecycle | Common refs | Common refs | Zdieľané |
| Root provenance | Spoločný helper | Ten istý helper | Správna platnosť; SEC-0002 pri explicitnom flagu |
| PropertyRecord | Optional owned claims | Zakázaný | Generic runtime nevyžaduje claims |
| Classification | Optional assignments | Optional assignments | Rovnaký CLS resolver |
| Replacement | Štrukturálne MAT odkazy | Deferred | Bez kopírovania sémantiky |
| Index | $defs.material + materials | Iba $defs.supplier | Explicitné v1 rozhodnutie |
| Observation | Samostatný aggregate | Samostatný aggregate | Bez embedding/reverse IDs |

**PASS.** Znovupoužiteľné sú mechanizmy, nie univerzálny entity field list. Ownership sa rozhoduje osobitne.

## 38. Error Paths

**PASS pre kategórie a adresovanie.** Overené `$.id`, `$.sourceLinks`, `$.classifications[0].classificationId`, index 1 aj `$.classifications[0].sourceLinks[0].sourceReferenceId`. Schema, application, reference integrity a catalog chyby zostávajú oddelené. Kontextové chyby zachovávajú root SUP a referenced CLS; nie sú zabalené do generic Supplier failure. Multiplicita identickej source chyby je výnimka SEC-0002.

## 39. Error Suppression

**PASS.** Missing `CLS-999999` vyvolá práve jednu `reference_integrity.reference_not_found` na správnom indexe, bez lifecycle kaskády. Type mismatch tiež zastaví závislé kontroly. Schema chyby zastavia catalog fázu. Root application chyba však nepotlačí nezávislé missing CLS chyby. SEC-0002 nie je chybou CLS dependency suppression.

## 40. Root Provenance Tests

Pokryté required sourceLinks s presnou cestou, Draft empty, Review/Approved empty/populated, assignment/root oddelenie a malformed SourceLink. Default API vyžaduje zdroj bez opt-in. Kombinácia automatického pravidla s explicitným True nie je v trvalých entity testoch; jednorazový probe reprodukoval SEC-0002.

## 41. Fixture Quality

**PASS.** 12 valid a 131 invalid Supplier fixtures, z toho 97 deferred-field prípadov. Valid prípady: minimum, empty/populated zdroje, optional texty, 0/1/viac CLS, full profile, Review/Approved so zdrojom. Názov je fiktívna organizácia Alfa; SUP-9001/SRC-980001/CLS-980001/2 sú testovacie ID. Scan nenašiel URL, emaily ani reálne kontaktné/daňové identifikátory.

Všetkých 131 invalid súborov bolo vyhodnotených. Pri 97 deferred fixtures trvalý test vyžaduje jedinú additionalProperties chybu na danom poli a platnosť po odstránení. Zvyšných 34 má dôvody zodpovedajúce názvom: missing, ID, type, minLength, format, revision, lifecycle alebo malformed SourceLink. Empty object zámerne vyvolá 12 required chýb; prázdny SourceLink viac vnorených required/anyOf chýb. False-positive fixture spôsobený nezávislým chybným poľom sa nezistil.

## 42. Test Coverage

**PASS pre schválené invarianty, s Low SEC-0003.** 24 nových metód nad baseline 236. Pokrývajú central identity/common refs, minimum, optional texty, multiplicitu, provenance, deferred fields, Observation SUP regresiu, index, explicitný context, missing/type mismatch CLS a nested paths.

`test_context_cls_lifecycle_default_and_authoring` iteruje len Approved a Draft. Jeho Deprecated assertion sa nespustí. Root Supplier lifecycle test nie je náhradou nested CLS testu. Review/Deprecated/Archived na Supplier ceste preto closure overil jednorazovo; trvalé testy zostali nezmenené.

## 43. Regression Review

**PASS.** 260 passed / 0 failures / 0 errors / 0 skipped. `test_validation.py`: 194, `test_catalog_validation.py`: 42, `test_supplier_validation.py`: 24. Pôvodných 236 prešlo bez úprav; Supplier commit prvé dva testové súbory nezmenil. Prešli Knowledge Core, všetky štyri katalógy, CatalogRegistry, ValidationContext, Material aj jeho context validácia. Review nepridal unittest.

## 44. Schema Review

**PASS.** Draft 2020-12; canonical ID `https://eos.local/schemas/entities/supplier.schema.json`; title `EOS Supplier`; doménový description; object; additionalProperties false; central SUP, common metadata, SourceLink a Classification refs. Presne 12 required a 3 optional fields. Všetkých 22 schém prešlo Draft202012Validator.check_schema aj schema keyword kontrolou.

## 45. Schema Index

**PASS.** `$defs.supplier` existuje raz, Material ostáva registrovaný. Všetkých 201 `$ref` sa vyriešilo. Supplier index test má pozitívny aj negatívny prípad cez JSON Schema ref wrapper.

Chýbajúca `suppliers` kolekcia je výslovné obmedzenie implementačného zadania, zaznamenané v CDR-0017 §61.2. `$defs` je discovery/structural entry, nie nové EOS aplikačné API s fragmentovým schema ID. Plná validácia používa canonical Supplier schema ID. Material collection je nezmenená.

## 46. Entity Directory

**PASS.** Presne `material.schema.json` a `supplier.schema.json` v `schemas/entities/`. Knowledge Core Observation sa do tejto adresárovej metriky nezapočítava. Konvencia nezavádza framework alebo persistence.

## 47. Identifier Consistency

**PASS.** MAT/SUP central štvormiestne formáty nezmenené. Search našiel päťmiestne `SUP-09001` iba v zámernej long-padding invalid fixture; ostatné malformed hodnoty sú tiež negatívne testy. Runtime nemá lokálny SUP regex. Regex v teste je assertion, nie druhý produkčný validátor. Draft EOS-004 supplierType nie je alternatívny formát ani prijatý v1 field.

## 48. Documentation Consistency

**CONDITIONAL — SEC-0001.** CDR-0017 Rev. 2, aktuálne README, CHANGELOG a horná ROADMAP sekcia sú zhodné: Supplier implementovaný, SI-0001 CLOSED, closure pending, odložené domény neimplementované. CDR-0017 staršie OPEN/NOT READY výroky sú explicitne história Rev. 0/1.

BACKLOG:3–5 však stále uvádza Supplier pre-design ako nasledujúci a nezačatý; v completed zozname Supplier chýba. ROADMAP:9 označuje nezmenený BACKLOG za historický, ale samotný BACKLOG nemá také označenie ani odkaz na aktuálny transition. To zmierňuje nejasnosť pri spoločnom čítaní, neodstraňuje rozpor samostatného planning dokumentu. Rovnaká trieda chyby blokovala Material transition ako MEC-0001.

Staršie schema opisy future catalog a `__init__` Phase 0.2A text sú historické stopy, nie nová Supplier sémantika; aktuálne README/runtime jasne rozlišujú vrstvy. Tests README deklaráciu Deprecated warning pokrytia treba pri SEC-0003 podložiť vykonateľným Supplier prípadom. Historické dokumenty sa nemenili.

## 49. Real Data Boundary

**PASS.** Supplier JSON dáta sú izolované vo fixtures s fiktívnym názvom a testovacím účelom. Bez reálnych company IDs, kontaktov, produkčného katalógu alebo onboarding závislosti.

## 50. Complexity Sanity

Dve explicitné entity vetvy sú primerané. Root source aj CLS pravidlá majú spoločný helper. SchemaRegistry cache-uje schémy podľa cesty; Supplier nepridáva opakované diskové načítavanie, deep-copy vrstvu alebo registry. Contract a catalog traversal majú samostatné registrácie, ktorých súlad treba pri rozšírení sledovať. To ešte nie je dôvod na framework/refactoring. Konkrétny diagnostický dlh je SEC-0002; zásadný generický pattern defekt sa nezistil.

## 51. Failure / Safety

**PASS.** Malformed SUP, unknown/deferred fields a neplatný child zlyhajú. Bez explicitného contextu sa vracia `catalog_validation.context_required`; contract-only nesľubuje CLS existenciu. Missing CLS zlyhá uzavreto. Validný root neprekryje chybný child. Validátor nesľubuje právnu pravdu, applicability alebo SRC existenciu.

## 52. Source / Lifecycle Composition

Material/Supplier používajú spoločnú `_validate_contract_rules` vetvu a jeden `_validate_source_links_rule(..., has_verifiable_claims=True)`. SEC-0002 vzniká následným druhým volaním z `_validate_application_rules`, ak caller explicitne odovzdá True. Default False: jedna chyba; True: dve identické chyby. Platnosť, cesta a kategória zostávajú správne. Potrebná je cielená kompozičná oprava, nie nový framework.

## 53. Future Entity Pattern

**Technicky použiteľný s evidovaným malým dlhom.** Reuse central ID/common metadata/schema ID, provenance helperov, owned-value traversal, exact paths a test organization je bezpečný. Field list, PropertyRecord ownership, replacement a kolekcie sa nesmú kopírovať bez doménového rozhodnutia. Pred násobením na ďalších päť entít sledovať dvojitú registráciu traversal a opraviť duplicitnú source diagnostiku samostatne. Žiadna nová entita sa nenavrhuje.

## 54. Completion Criteria

| # | Kritérium | Výsledok | Dôkaz |
| --- | --- | --- | --- |
| 1 | Supplier domain semantics preserved | PASS | §4, closed organization profile |
| 2 | SI-0001 boundary preserved | PASS | §6, CDR-0017 §60 |
| 3 | Knowledge Entity / Entity / Aggregate Root | PASS | §7 |
| 4 | SUP centralized | PASS | §5, §47 |
| 5 | Common metadata reused | PASS | §8, property refs |
| 6 | Root provenance semantics correct | PASS | §10 |
| 7 | Lifecycle not overloaded | PASS | §9 |
| 8 | Incremental minimum Supplier | PASS | §11, minimal Draft |
| 9 | Name semantics correct | PASS | §12 |
| 10 | Description/notes non-structural | PASS | §13 |
| 11 | Multi-role supported | PASS | §15, distinct CLS probe |
| 12 | Classification ownership/integration | PASS | §14–16 |
| 13 | PropertyRecord absent | PASS | §17, precise rejection |
| 14 | Observation separate | PASS | §18 |
| 15 | Site/location boundary | PASS | §19 |
| 16 | Address boundary | PASS | §20 |
| 17 | Contact/person boundary | PASS | §21 |
| 18 | External identifier boundary | PASS | §22 |
| 19 | Qualification boundary | PASS | §23 |
| 20 | Certification boundary | PASS | §24 |
| 21 | Capability boundary | PASS | §25 |
| 22 | Material/StockMaterial boundaries | PASS | §26–27 |
| 23 | Process/Machine/Tool boundaries | PASS | §28–29 |
| 24 | Commercial data excluded | PASS | §30 |
| 25 | Price/lead-time excluded | PASS | §30–31 |
| 26 | Rating/performance excluded | PASS | §32 |
| 27 | Corporate/replacement deferred | PASS | §33 |
| 28 | Organization risk not worsened | PASS | §34 |
| 29 | Generic resolver absent | PASS | §35 |
| 30 | Context-aware validation correct | PASS | §16, §36, 10 lifecycle probes |
| 31 | Paths/categories preserved | PASS | §38–39; multiplicita osobitne SEC-0002 |
| 32 | Fixtures isolated/fictional | PASS | §41, §49 |
| 33 | Previous 236 regressions pass | PASS | §43 |
| 34 | Supplier tests pass | PASS | 24/24; coverage limit SEC-0003 |
| 35 | Accepted architecture unchanged | PASS | Git diff |

**35 PASS, 0 FAIL, 0 CONDITIONAL.** Implementačné kritériá neobsahujú synchronizáciu planning dokumentov. SEC-0001 preto samostatne blokuje formálne COMPLETE/transition, rovnako ako pri Material. Low diagnostický/coverage dlh nemení správnosť uvedených invariantov.

## 55. Deferred Work

Kategórie sú plánovanie, nie požiadavka implementovať všetky rozšírenia pred minimálnym identity onboardingom.

| Téma | Kategória | Hranica |
| --- | --- | --- |
| Identity/source verification a duplicate policy | prerequisite for real Supplier data | Platný JSON nie je overená identita |
| Site/location | later Supplier extension | Pred site-scoped údajmi |
| Address | later Supplier extension | Bez ad-hoc štruktúr |
| Contacts/persons | later governance capability | Identity, roly, platnosť, prístup |
| External/legal IDs | research/design question | Scheme, scope, provenance |
| Qualification | later Supplier extension | Oddelená od RecordStatus |
| Certifications | later Supplier extension | Subjekt, scope, čas |
| Capability | research/design question | Kategória nie je dôkaz schopnosti |
| Material/StockMaterial supply | relationship/commercial layer | Nie root arrays |
| Service/process capability relationship | relationship/commercial layer | Explicitný context |
| Commercial offer/procurement | relationship/commercial layer | Nie identity |
| Prices/lead times/payment terms | relationship/commercial layer | Predmet, množstvo, čas, account |
| Assessment/performance | later Supplier extension | Metóda, evidence, čas |
| Corporate/succession | research/design question | Kontinuita nie je record replacement |
| Generic resolver, ak bude potrebný | entity/runtime infrastructure | Podľa schválených väzieb |
| Organization abstraction | research/design question | MEDIUM; zachovať SUP/históriu |
| Real Supplier onboarding | prerequisite for real Supplier data | Samostatný riadený míľnik |
| Source diagnostika a coverage | entity/runtime infrastructure | SEC-0002/0003, samostatná úzka úloha |

## 56. Next Entity Readiness

Supplier je architektonicky stabilný druhý entity pattern. Identity, ownership ani generic validation nevyžadujú redesign. Formálny prechod na Phase 0.2C.3 zatiaľ nepovoliť pre SEC-0001.

Najbližšie odporúčanie: `Phase 0.2C.2-close.1 — Supplier Closure Documentation Alignment`. Po uzavretí SEC-0001 a overení baseline môže nasledovať `Phase 0.2C.3-prep — ManufacturingProcess Entity Pre-design Review`. Low SEC-0002/0003 tento pre-design neblokujú; zostávajú viditeľné samostatné úlohy.

## 57. Blocking Findings

### SEC-0001 — BACKLOG odporuje aktuálnemu Supplier transition stavu

- Severity: **Medium**.
- Affected artifacts: `BACKLOG.md:3–5` a completed list; `ROADMAP.md:5–9`; CDR-0017 §61.
- Description: Samostatný aktívne pomenovaný BACKLOG prezentuje Supplier pre-design ako nezačatý a nasledujúci, hoci v1 je implementovaný.
- Evidence: Heading `Nasledujúce: Phase 0.2C.2-prep` a veta `Supplier pre-design zatiaľ nezačal`; oproti tomu ROADMAP IMPLEMENTED a CDR-0017 Rev. 2. ROADMAP označuje BACKLOG za historický, ale BACKLOG nemá vlastné upozornenie/aktuálny transition odkaz.
- Impact: Pri samostatnom použití planning dokumentu hrozí opakovanie ukončeného míľnika. Nesplnená explicitná documentation-consistency požiadavka; rovnaký precedens MEC-0001.
- Recommended action: Samostatne aktualizovať aktuálny BACKLOG, zachovať deferred témy a zosúladiť transition s ROADMAP/CHANGELOG a closure. Historické snapshots neprepisovať potichu.
- Blocks Phase 0.2C.3: **Yes**, formálny transition blocker, nie schema defect.

## 58. Non-blocking Findings

### SEC-0002 — Explicitný caller flag zdvojuje source chybu

- Severity: **Low**.
- Affected artifacts: `scripts/validation/validator.py:469–471`, `525–531`, `1038–1057`; Supplier aj Material entry point.
- Description: Automatický entity source helper sa pri caller `has_verifiable_claims=True` vykoná znova v application rules.
- Evidence: Načítať `supplier-minimal-draft-valid.json`, zmeniť iba status na Review/Approved a volať `validate(record, 'https://eos.local/schemas/entities/supplier.schema.json', has_verifiable_claims=True)`. Vrátia sa dve identické `application_validation.source_links_required`, category `application_validation`, path `$.sourceLinks`, recordId `SUP-9001`. Default False vráti jednu. Rovnaký Material probe vráti dve; Draft ostáva platný.
- Impact: Duplicitné hlásenia/error count pri podporovanom API argumente. Nezmení sa ok=False, kategória, cesta ani odmietnutie dát. Problém existoval pri Material a Supplier ho zdedil.
- Recommended action: Cielená samostatná kompozičná oprava jedného vykonania účinného source pravidla; regresie default/explicit flag pre entity a súvisiace katalógy. Zachovať automatickú provenance povinnosť, nezavádzať framework.
- Blocks Phase 0.2C.3: **No**; diagnostický dlh, nie chybný doménový vzor.

### SEC-0003 — Supplier lifecycle test nevykoná Deprecated vetvu

- Severity: **Low**.
- Affected artifacts: `tests/test_supplier_validation.py:220–231`, catalog-context fixture `classificationEntries`, `tests/README.md:9`.
- Description: Nested Supplier lifecycle test iteruje iba Approved/Draft; Review/Deprecated/Archived nie sú jeho vstupy. Deprecated assertion je nedosiahnutý.
- Evidence: Fixture má iba `CLS-980001: Approved`, `CLS-980002: Draft`. Root Supplier test piatich stavov je iná kontrola. Closure jednorazovo overil všetkých päť CLS stavov s oboma policies na Supplier a všetkých 10 prípadov prešlo vrátane warningu a nested paths.
- Impact: Trvalá regresná ochrana je užšia než naznačuje názov testu a README; runtime defect sa nepreukázal. Spoločné lifecycle testy a closure probes potvrdzujú správne správanie.
- Recommended action: Samostatný test-only krok s piatimi fiktívnymi status variantmi, oboma policies, warningom, root recordId/referencedId a cestou; nie iba assertion policy helpera.
- Blocks Phase 0.2C.3: **No**.

Celkom **3 SEC findings: 0 Critical, 0 High, 1 Medium, 2 Low; 1 blocking, 2 non-blocking**. Známe Organization riziko a explicitný dispatch nie sú bez nového dôkazu ďalšími findings.

## 59. Required Actions

Pred ďalším entity míľnikom uzavrieť SEC-0001 samostatným documentation-only corrective krokom a zaznamenať overenie v ďalšej revízii closure. Zachovať Supplier pre-design/SI-0001/implementáciu aj deferred hranice. SEC-0002/0003 odporúčame riešiť samostatnou úzkou runtime/test úlohou; nie sú povolením meniť kód v tomto review.

| Metrika | Výsledok |
| --- | --- |
| Unittest | 260 passed, 0 failures, 0 errors, 0 skipped |
| Pre-Supplier / Supplier-added | 236 / 24 tests |
| Schemas / Knowledge Core / catalogs / entities | 22 / 7 / 4 / 2 |
| Total valid / invalid fixtures | 121 / 523 JSON súborov pod valid/invalid |
| Supplier valid / invalid | 12 / 131 |
| Material valid / invalid | 16 / 42, nezmenené |
| Catalog-context | 1 samostatný JSON mimo valid/invalid počtov |
| ADR / RFC documents | 17 vrátane template / 4 vrátane cross-review (3 Accepted RFC) |
| JSON parsing | PASS, 667 tracked JSON súborov |
| Draft202012Validator.check_schema / keyword audit | PASS, 22 schém |
| $ref resolution | PASS, 201 referencií |
| UTF-8 baseline | PASS, 744 tracked textových súborov; nový CDR kontrolovaný samostatne |
| Python compile | PASS, 9 tracked Python súborov |
| Python / jsonschema / referencing | 3.12.14 / 4.26.0 / 0.37.0 |
| Dependencies | Nezmenené |

Diff `736820b..adbc8c7` potvrdil nezmenené Material/common/KC/catalog schemas, pôvodné testy, catalog-context runtime, pyproject, RFC/ADR a governance. Review zachováva implementáciu/fixtures na adbc8c7 a pridáva iba tento CDR. Bez reálnych dát, ďalších entít, persistence, API, UI, merge, tag alebo release.

## 60. Closure Verdict

Supplier spĺňa 35 implementačných kritérií, zachováva SI-0001 a druhý entity pattern bez PropertyRecord; celá regresia prešla. Bez Critical/High blockeru, aggregate ownership úniku alebo materiálneho generic-framework defektu.

Phase 0.2C.2 zatiaľ nemožno označiť COMPLETE pre konečný dokumentačný transition blocker SEC-0001. Najbližšie nasleduje Supplier Closure Documentation Alignment, až potom ManufacturingProcess pre-design. Low SEC-0002/0003 ostávajú evidované ako neblokujúce. Phase 0.2C.3 sa nezačína.

## 61. Change History

| Date | Version | Revision | Author | Change |
| --- | --- | --- | --- | --- |
| 2026-10-14 | 0.1 | 0 | Codex | Prvý Supplier closure review na adbc8c7; 35 PASS, 260 úspešných testov, jeden dokumentačný transition blocker a dva neblokujúce runtime/test findings. Bez zmeny implementácie. |
| 2026-10-14 | 0.1 | 1 | Codex | Phase 0.2C.2-close.1: reprodukované a uzavreté SEC-0001/0002/0003, minimálna source composition oprava, trvalé regresie, 263 úspešných testov a 35 PASS bez zmeny doménových kontraktov. |

## 62. Corrective Closure Outcome

### 62.1 Baseline and scope

Vstup: čistá vetva `feature/phase-0.2c-knowledge-entities`, tracking origin rovnakej vetvy, HEAD `dd23d5455007533927299b80d1a0bff166229337`; lokálny tracking ref zhodný s HEAD. Supplier implementačný commit adbc8c7 je predkom. CDR-0018 Rev. 0 mal historický verdict READY WITH CONDITIONS. Baseline vykonaný pred editáciou: 260 tests, 29.664 s, OK; 0 failures/errors/skipped.

Rozsah: odstrániť tri doložené findings, zachovať automatic provenance, API, schemas a architecture freeze. Žiadny nový framework, post-hoc deduplication, entity resolver alebo ManufacturingProcess návrh. Authority z predchádzajúceho review zostáva nezmenená: CDR-0017 Rev. 2, CDR-0016 corrective precedent, EOS-003/006/007 a relevantné Accepted RFC/ADR.

### 62.2 SEC-0001 — CLOSED

Previous status: Medium, blocking. Pred opravou BACKLOG samostatne uvádzal Supplier pre-design ako nasledujúci a nezačatý. BACKLOG teraz uvádza completed pre-design, SI-0001 CLOSED, v1 aj corrective closure; všetky pôvodné otvorené/deferred témy zostali a Supplier deferred scope z §55 je explicitne doplnený. Aktuálne ROADMAP/CHANGELOG sekcie zhodne uvádzajú Phase 0.2C.2 COMPLETE a nasledujúci, zatiaľ nezačatý ManufacturingProcess pre-design. Historické milestone texty sú zachované a označené ako história.

Final status: CLOSED na základe obsahového porovnania samostatných planning dokumentov, nie iba zelených testov.

### 62.3 SEC-0002 — CLOSED

Previous status: Low, non-blocking. Reprodukcia pred editáciou validatora použila platné `material-minimal-draft-valid.json` a `supplier-minimal-draft-valid.json`; zmenil sa iba status na Review/Approved, sourceLinks ostal prázdny. Presná diagnostická tuple bola `(application_validation, application_validation.source_links_required, $.sourceLinks, MAT-9001)` alebo rovnaká s `SUP-9001`.

| Entita | Status | Default/False pred opravou | Explicit True pred opravou | Po oprave omitted/False/True |
| --- | --- | --- | --- | --- |
| Material | Review | 1 identická tuple | 2 identické tuples | 1 / 1 / 1 |
| Material | Approved | 1 | 2 | 1 / 1 / 1 |
| Supplier | Review | 1 | 2 | 1 / 1 / 1 |
| Supplier | Approved | 1 | 2 | 1 / 1 / 1 |

Root cause: `_validate_application_rules` najprv volá `_validate_contract_rules`, kde Material/Supplier automaticky volajú `_validate_source_links_rule(True)`. Následne explicitný caller flag aktivoval druhé volanie toho istého helpera na tom istom root/path. Štyri katalógové kontrakty mali rovnakú kompozíciu; Observation už malo výnimku.

Oprava je jeden composition guard: caller-driven helper sa nevolá pre sedem kontraktov, ktorých automatic traversal už túto root povinnosť pokrýva (Observation, štyri katalógy, Material, Supplier). Automatické contract rules, rekurzia, source policy ani error equality sa nemenia. Žiadne globálne skrývanie alebo deduplikácia výsledkov. SourceReference a ostatní opt-in consumers aj CLI argument ostávajú funkčné. Vyhľadanie všetkých `has_verifiable_claims` použití preverilo file/context entry point forwarding, CLI a existujúce SourceReference/Classification testy.

Permanent evidence: nové `test_material_root_source_rule_runs_once_with_explicit_flag`, `test_supplier_root_source_rule_runs_once_with_explicit_flag` a `test_source_flag_preserves_catalog_observation_and_opt_in_consumers`. Prvé dve skúšajú každý Draft/Review/Approved × empty/populated × omitted/False/True prípad s presným celým zoznamom category/code/path/recordId a ok výsledkom. Draft empty aj populated zdroje ostávajú platné. Tretí test chráni všetky štyri katalógy, Observation a SourceReference opt-in s rovnakými presnými assertions.

Pred opravou nové entity metódy zlyhali presne v štyroch Review/Approved explicit-True subtestoch. Po oprave všetky cielené prípady aj plná sada prešli. Final status: CLOSED; automatická provenance nie je podmienená caller flagom.

### 62.4 SEC-0003 — CLOSED

Previous status: Low, non-blocking. Pôvodný permanent test iteroval iba Approved `CLS-980001` a Draft `CLS-980002`; Deprecated assertion sa nemohol vykonať. Skontrolovaná skutočná CatalogLifecyclePolicy DEFAULT/AUTHORING zodpovedá nasledujúcej matici, bez rozporu so zadaním.

| CLS stav | default | authoring |
| --- | --- | --- |
| Draft | error | OK |
| Review | error | OK |
| Approved | OK | OK |
| Deprecated | OK + warning | OK + warning |
| Archived | error | error |

Existujúca `test_context_cls_lifecycle_default_and_authoring` teraz vytvára nezávislé test-local kópie platnej fiktívnej CLS pre všetkých päť stavov. Každý variant najprv overí katalógovým kontraktom a vloží do nového immutable registry. Skutočná Supplier context-aware cesta vykoná obe policies, spolu 10 kombinácií; pôvodná shared fixture sa nemení a testy nezávisia od poradia.

Pri odmietnutí presne assertuje `catalog_validation.catalog_status_not_allowed`, category `catalog_validation`, severity error; pri Deprecated presne `catalog_validation.deprecated_reference`, rovnakú category, severity warning, ok=True a práve jeden warning. V oboch prípadoch path `$.classifications[0].classificationId`, recordId `SUP-9001`, referencedId `CLS-980001`; ostatné povolené stavy majú prázdny zoznam diagnostiky. Expected acceptance používa existujúcu policy po jej vecnom overení, nie nový Supplier enum.

Final status: CLOSED; všetky stavy, obe policies, warning aj nested identifikátory sú trvalými vykonávanými assertions.

### 62.5 Completion criteria recheck

Všetkých 35 kritérií z §54 bolo opakovane porovnaných s nezmenenými doménovými schémami, zúženým runtime diffom a úspešnou regresiou. Nasledujúca tabuľka je aktuálny výsledok Revision 1.

| # | Kritérium | Výsledok | Opakovaný dôkaz |
| --- | --- | --- | --- |
| 1 | Supplier domain semantics preserved | PASS | Nezmenený kontrakt a regresie; §4, closed organization profile |
| 2 | SI-0001 boundary preserved | PASS | Nezmenený kontrakt a regresie; §6, CDR-0017 §60 |
| 3 | Knowledge Entity / Entity / Aggregate Root | PASS | Nezmenený kontrakt a regresie; §7 |
| 4 | SUP centralized | PASS | Nezmenený kontrakt a regresie; §5, §47 |
| 5 | Common metadata reused | PASS | Nezmenený kontrakt a regresie; §8, property refs |
| 6 | Root provenance semantics correct | PASS | §62.3–62.4, presné source/CLS regresie |
| 7 | Lifecycle not overloaded | PASS | Nezmenený kontrakt a regresie; §9 |
| 8 | Incremental minimum Supplier | PASS | Nezmenený kontrakt a regresie; §11, minimal Draft |
| 9 | Name semantics correct | PASS | Nezmenený kontrakt a regresie; §12 |
| 10 | Description/notes non-structural | PASS | Nezmenený kontrakt a regresie; §13 |
| 11 | Multi-role supported | PASS | Nezmenený kontrakt a regresie; §15, distinct CLS probe |
| 12 | Classification ownership/integration | PASS | Nezmenený kontrakt a regresie; §14–16 |
| 13 | PropertyRecord absent | PASS | Nezmenený kontrakt a regresie; §17, precise rejection |
| 14 | Observation separate | PASS | Nezmenený kontrakt a regresie; §18 |
| 15 | Site/location boundary | PASS | Nezmenený kontrakt a regresie; §19 |
| 16 | Address boundary | PASS | Nezmenený kontrakt a regresie; §20 |
| 17 | Contact/person boundary | PASS | Nezmenený kontrakt a regresie; §21 |
| 18 | External identifier boundary | PASS | Nezmenený kontrakt a regresie; §22 |
| 19 | Qualification boundary | PASS | Nezmenený kontrakt a regresie; §23 |
| 20 | Certification boundary | PASS | Nezmenený kontrakt a regresie; §24 |
| 21 | Capability boundary | PASS | Nezmenený kontrakt a regresie; §25 |
| 22 | Material/StockMaterial boundaries | PASS | Nezmenený kontrakt a regresie; §26–27 |
| 23 | Process/Machine/Tool boundaries | PASS | Nezmenený kontrakt a regresie; §28–29 |
| 24 | Commercial data excluded | PASS | Nezmenený kontrakt a regresie; §30 |
| 25 | Price/lead-time excluded | PASS | Nezmenený kontrakt a regresie; §30–31 |
| 26 | Rating/performance excluded | PASS | Nezmenený kontrakt a regresie; §32 |
| 27 | Corporate/replacement deferred | PASS | Nezmenený kontrakt a regresie; §33 |
| 28 | Organization risk not worsened | PASS | Nezmenený kontrakt a regresie; §34 |
| 29 | Generic resolver absent | PASS | Nezmenený kontrakt a regresie; §35 |
| 30 | Context-aware validation correct | PASS | §62.3–62.4, presné source/CLS regresie |
| 31 | Paths/categories preserved | PASS | §62.3–62.4, presné source/CLS regresie |
| 32 | Fixtures isolated/fictional | PASS | Nezmenený kontrakt a regresie; §41, §49 |
| 33 | Previous 236 regressions pass | PASS | Pôvodných 236 aj kompletných 260 pred opravou zachovaných v sade |
| 34 | Supplier tests pass | PASS | 25/25 Supplier metód; všetkých 10 CLS kombinácií |
| 35 | Accepted architecture unchanged | PASS | Nezmenený kontrakt a regresie; Git diff |

Súčet: **35 PASS, 0 FAIL, 0 CONDITIONAL**. SEC-0001 už neblokuje formálny transition. Otvorené SEC findings: 0; blockers: 0; nové blokujúce zistenie sa neobjavilo. Pôvodné findings v §57–58 zostávajú historickým dôkazom.

### 62.6 Validation and scope evidence

- Plná sada: 263 tests, 30.485 s, OK; 263 passed, 0 failures, 0 errors, 0 skipped. Baseline 260 zachovaná; 3 nové metódy, jedna existujúca rozšírená. Rozdelenie 196 general, 42 catalog, 25 Supplier.
- JSON parsing PASS: 667 JSON súborov. Draft202012Validator.check_schema aj schema keyword audit PASS: 22 schém; 201 refs vyriešených, index regresie zelené.
- UTF-8 PASS: 745 tracked textových súborov; Python compile PASS: 9 Python súborov. Python 3.12.14, jsonschema 4.26.0, referencing 0.37.0.
- Schémy bez zmeny: 22 total, 7 Knowledge Core, 4 catalogs, 2 entities (Material/Supplier). ADR 17 vrátane template; RFC 4 dokumenty vrátane cross-review.
- Fixtures bez zmeny: 121 valid/523 invalid; Supplier 12/131; Material 16/42. Shared catalog-context fixture nezmenená. Nevznikli reálne dáta.
- Doménové Material/Supplier a všetky ostatné schémy, common identifiers, catalog_context policy, governance, Accepted RFC/ADR a dependency súbory nezmenené. Zmena runtime je iba composition guard; žiadny nový resolver/framework a žiadne ManufacturingProcess artifacts.
- Intended files: BACKLOG.md, ROADMAP.md, CHANGELOG.md, tento CDR, scripts/validation/validator.py, tests/test_validation.py, tests/test_supplier_validation.py, tests/README.md. Historické CDR-0017 a CDR-0016 zostali nezmenené.

### 62.7 Final disposition

SEC-0001 CLOSED, SEC-0002 CLOSED, SEC-0003 CLOSED na základe konkrétnej korekcie a dôkazov. Phase 0.2C.2 Supplier je COMPLETE. Nasledujúci povolený míľnik je `Phase 0.2C.3-prep — ManufacturingProcess Entity Pre-design Review`; tento corrective krok ho nezačal. Žiadny merge, tag alebo release.

PHASE 0.2C.2 COMPLETE – READY FOR 0.2C.3
