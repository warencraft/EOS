# CDR-0022: Uzavretie migrácie testov entít podľa ADR-0017

Project: EOS – Engineering Operating System
Contract Review ID: CDR-0022
Review type: Closure
Version: 0.1
Revision: 0
Status: Review
Document basis: Accepted ADR-0017 a lokálne vykonané regresné a porovnávacie kontroly

## Účel a rozsah

Rozhodnutie sa týka výhradne spoločnej testovacej infraštruktúry troch entít. Baseline: `2065a73fd0098a6bd97c97d5277d04082ec1d892` (main po PR #3, #4 a #5). Vetva: `closure/adr-0017-test-migration`. Pred vyradením: 299/299 úspešných. Zmeny sú lokálne na finálne review; nejde o tvrdenie o stave publikovaného main.

## Rozhodnutie a dôkazy

Zdrojom očakávaní sú explicitné ENTITY_PROFILES, tabuľky invalid-cases a špecifické významové testy, nie výstup schémy pod testom. Žiadny nový formát, generátor alebo runtime závislosť. V každej rodine skupina starých súborov presne zodpovedá vyradeným cestám v prílohe A.

| Rodina | Exact A | Explicitné riadky | Deferred | Generované a zložené mimo tabuľky | Negatívne spolu | Platné príklady |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Supplier | 131 | 15 | 97 | 30 | 142 | 12 |
| ManufacturingProcess | 148 | 12 | 125 | 31 | 168 | 11 |
| Material | 42 | 14 | 17 | 31 | 62 | 16 |
| Spolu | 321 | 41 | 239 | 92 | 372 | 39 |

**Ako sa dokázala náhrada:** ešte pred odstránením prešli staré súbory i nové vstupy validáciou. Po odstránení nezávislá kontrola znovu načítala presný obsah pôvodných fixtures z archívu HEAD, nie z generátora. Porovnala oba dekódované JSON vstupy a pre každý vstup aj početnosť všetkých očakávaných diagnostík (category, errorCode, path, recordId, referencedId, severity). Nešlo o porovnanie dvoch booleovských výsledkov ani o porovnanie poradia členov JSON objektu. Pri viacerých zhodných generovaných vstupoch príloha uvádza jednu preukázanú náhradu. Klasifikácia odstránených kandidátov: A=321, B=0, C=0, D=0. Kategória C nie je nulová pre *iné* aktíva: platné príklady, katalógový kontext a špecifické testy sa ponechávajú.

- Supplier: zachované hranice identity organizácie, CLS lifecycle, default/authoring, upozornenia, priama aj kontextová validácia a root/assignment provenance.
- ManufacturingProcess: samostatné pomenované zákazy procesných parametrov, operácií a capability; oddelená Observation; chýbajúce CLS bez závislých chýb, TEC recordId a presné vnorené cesty.
- Material: zdroj a platnosť vnoreného claim sa nezamieňajú so zdrojom rodiča. Pokryté sú duplicitné a konfliktné tvrdenia, replacement iba ako MAT referencia, PRP/UNT/CND/CLS, value type, jednotky a podmienky, potlačenie závislých chýb a indexové cesty. Nepoužiteľná náhrada chybnej MAT referencie ani vynechanie ďalšej chyby zloženého prípadu neprejdú.

## Vyradené a ponechané testy

Odstránených 23 metód: opakované kontroly uzavretosti/minima, iterácií fixtures, zdrojov a zákazu ďalších polí, procesná mapa porovnávaná so súbormi a tri dočasné porovnávacie metódy. Presné názvy sú v prílohe C. Spoločný runner teraz kontroluje aj úplnú diagnostiku zložených vstupov (prázdny objekt, poškodený SourceLink a neúplný PropertyRecord), platnosť východiskového záznamu, prítomnosť pôvodných platných príkladov podľa mena a výsledky 54 kombinácií root provenance (18 na entitu). Zákazy jednotlivých doménových polí zostávajú explicitné v tabuľkách. Osobitný Material test náhrad naďalej skúša oba smery na verejnom API; nepotrebuje už samostatné neplatné súbory.

Počet metód klesol z 299 na 276. Tri spoločné testovacie metódy vykonávajú jednotlivé subTest; **372 nie je počet unittest metód**. Ponechaných 58 metód zameraných na tieto tri entity (vrátane ich špecifických integračných kontrol) je v prílohe B. Celkovo ostalo všetkých 132 platných fixtures, jeden spoločný katalógový kontext a 350 záporných fixtures iných rodín; tri tabuľky entít sa nepočítajú ako ďalšie záporné JSON záznamy. Nebol odstránený žiadny iný súbor.

## Skúšky citlivosti

Každý zásah bol dočasný, iba v pamäti; požadovalo sa zlyhanie konkrétneho subTest, nie chyba spustenia. Po odobratí zásahu prešla čistá sada.

| # | Vnesená porucha | Pozorovaný signál |
| ---: | --- | --- |
| 1 | SUP profil bez povinného id | test_contract_and_fixtures: supplier |
| 2 | Povoľ contacts na Supplier | test_negative_cases: deferred-contacts |
| 3 | Povoľ parameters na ManufacturingProcess | test_negative_cases: deferred-parameters |
| 4 | Ignoruj neplatné replaces na Material | test_negative_cases: invalid-replaces-prefix |
| 5 | Zmeň vnorenú cestu PRP | test_unresolved_reference_has_no_dependent_diagnostics: PRP |
| 6 | Zmeň koreňový MAT recordId | rovnaký test: PRP |
| 7 | Zmeň referencedId pre PRP | rovnaký test: PRP |
| 8 | Zmeň referencedId pre UNT | rovnaký test: UNT |
| 9 | Zmeň referencedId pre CND | rovnaký test: CND |
| 10 | Zmeň referencedId pre CLS | rovnaký test: CLS |

## Finálna regresia

`.\.venv\Scripts\python.exe -m unittest discover -s tests -v`: 276 passed, 0 failures, 0 errors, 0 skipped (19,115 s). Python 3.12.14, jsonschema 4.26.0, referencing 0.37.0. Všetkých 23 schém prešlo Draft202012Validator.check_schema; každý z 215 výskytov $ref sa rozlíšil cez registry v kontexte vlastnej schémy. Testy neodkazujú na odstránené cesty. Kontrola diffu: bez zmeny schém, validátora alebo závislostí.

## Governance

1. PASS: bez neoverených technických hodnôt.
2. PASS: testovací dôkaz nie je norma ani technické odporúčanie.
3. PASS: ostali iba fiktívne testovacie dáta v rozsahu zmeny.
4. PASS: entity ID a názvy nezmenené; CDR-0022 bolo voľné po CDR-0021.
5. PASS: zmenené len testy a dokumentácia.
6. PASS: odstránené iba ekvivalentné vstupy; trvalé testy používajú spoločný profil a tabuľky.
7. PASS: slovenská dokumentácia, anglické identifikátory, UTF-8.
8. PASS: žiadna nová závislosť ani nástroj.
9. PASS: celá sada bez zlyhaní, chýb a preskočení.
10. N/A: nové ADR netreba; vykonáva sa existujúce Accepted ADR-0017.
11. PASS: aktuálne sekcie plánovania a changelogu odlišujú closure od implementácie Machine.
12. PASS: žiadna ďalšia fáza nezačala.

## Zvyšné obmedzenia a Machine

Iné rodiny fixtures neboli predmetom migrácie; veľkosť test_validation.py zostáva samostatnou otázkou údržby, nie blokérom Machine. Registry a fixtures nedokazujú platnosť reálnych strojárskych údajov. Stav podľa tohto lokálneho closure: ADR-0017 migration COMPLETE; infraštruktúrny blokér CLOSED. Machine zostáva READY FOR IMPLEMENTATION podľa CDR-0021, implementácia NOT STARTED. Tento záznam neaktivuje Machine a nie je povolením publikovať alebo zlúčiť zmeny.

## Príloha A: úplný inventár vyradených súborov

Všetky cesty sú pod `tests/fixtures/invalid/entities/`. Pravý stĺpec je vykonaný prípad v spoločnom runneri. Každý riadok: A (presná obsahová aj diagnostická ekvivalencia).

| Súbor na baseline | Rodina / náhradný prípad |
| --- | --- |
| `material-array-instead-of-object-invalid.json` | `material/array` |
| `material-chemical-composition-invalid.json` | `material/deferred-chemicalComposition` |
| `material-classifications-wrong-type-invalid.json` | `material/classifications-wrong-type` |
| `material-compatible-processes-invalid.json` | `material/deferred-compatibleProcesses` |
| `material-cutting-tool-ids-invalid.json` | `material/deferred-cuttingToolIds` |
| `material-delivery-condition-invalid.json` | `material/deferred-deliveryCondition` |
| `material-description-wrong-type-invalid.json` | `material/description-wrong-type` |
| `material-designation-invalid.json` | `material/deferred-designation` |
| `material-designations-invalid.json` | `material/deferred-designations` |
| `material-empty-name-invalid.json` | `material/name-empty` |
| `material-empty-object-invalid.json` | `material/empty-object` |
| `material-family-invalid.json` | `material/deferred-materialFamily` |
| `material-heat-treatment-invalid.json` | `material/deferred-heatTreatment` |
| `material-incomplete-padding-invalid.json` | `material/incomplete-padding` |
| `material-invalid-classification-invalid.json` | `material/invalid-classification` |
| `material-invalid-property-record-invalid.json` | `material/invalid-property-record` |
| `material-invalid-replaced-by-prefix-invalid.json` | `material/invalid-replaced-by-prefix` |
| `material-invalid-replaces-prefix-invalid.json` | `material/invalid-replaces-prefix` |
| `material-lowercase-prefix-invalid.json` | `material/lowercase-prefix` |
| `material-machine-ids-invalid.json` | `material/deferred-machineIds` |
| `material-malformed-id-invalid.json` | `material/malformed-id` |
| `material-malformed-source-link-invalid.json` | `material/malformed-source-link` |
| `material-material-condition-invalid.json` | `material/deferred-materialCondition` |
| `material-missing-id-invalid.json` | `material/missing-id` |
| `material-missing-name-invalid.json` | `material/missing-name` |
| `material-missing-source-links-invalid.json` | `material/missing-sourceLinks` |
| `material-name-wrong-type-invalid.json` | `material/name-wrong-type` |
| `material-norm-reference-ids-invalid.json` | `material/deferred-normReferenceIds` |
| `material-null-id-invalid.json` | `material/id-null` |
| `material-null-name-invalid.json` | `material/name-null` |
| `material-null-properties-invalid.json` | `material/null-properties` |
| `material-null-source-links-invalid.json` | `material/sourceLinks-null` |
| `material-observation-ids-invalid.json` | `material/deferred-observationIds` |
| `material-observations-invalid.json` | `material/deferred-observations` |
| `material-properties-wrong-type-invalid.json` | `material/properties-wrong-type` |
| `material-source-links-wrong-type-invalid.json` | `material/source-links-wrong-type` |
| `material-stock-forms-invalid.json` | `material/deferred-stockForms` |
| `material-supplier-id-invalid.json` | `material/deferred-supplierId` |
| `material-type-invalid.json` | `material/deferred-materialType` |
| `material-unknown-root-field-invalid.json` | `material/unknown-root-field` |
| `material-verification-status-invalid.json` | `material/deferred-verificationStatus` |
| `material-wrong-prefix-invalid.json` | `material/wrong-prefix` |
| `supplier-array-invalid.json` | `supplier/array` |
| `supplier-classifications-invalid-embedded-invalid.json` | `supplier/classifications-invalid-embedded` |
| `supplier-classifications-wrong-type-invalid.json` | `supplier/classifications-wrong-type` |
| `supplier-createdAt-invalid-date-invalid.json` | `supplier/createdAt-invalid-date` |
| `supplier-deferred-DUNS-invalid.json` | `supplier/deferred-DUNS` |
| `supplier-deferred-Incoterms-invalid.json` | `supplier/deferred-Incoterms` |
| `supplier-deferred-MOQ-invalid.json` | `supplier/deferred-MOQ` |
| `supplier-deferred-address-invalid.json` | `supplier/deferred-address` |
| `supplier-deferred-addresses-invalid.json` | `supplier/deferred-addresses` |
| `supplier-deferred-approvalStatus-invalid.json` | `supplier/deferred-approvalStatus` |
| `supplier-deferred-approvals-invalid.json` | `supplier/deferred-approvals` |
| `supplier-deferred-approved-invalid.json` | `supplier/deferred-approved` |
| `supplier-deferred-availableMaterials-invalid.json` | `supplier/deferred-availableMaterials` |
| `supplier-deferred-billingAddress-invalid.json` | `supplier/deferred-billingAddress` |
| `supplier-deferred-blockedSupplier-invalid.json` | `supplier/deferred-blockedSupplier` |
| `supplier-deferred-branches-invalid.json` | `supplier/deferred-branches` |
| `supplier-deferred-capabilities-invalid.json` | `supplier/deferred-capabilities` |
| `supplier-deferred-capabilityIds-invalid.json` | `supplier/deferred-capabilityIds` |
| `supplier-deferred-capacity-invalid.json` | `supplier/deferred-capacity` |
| `supplier-deferred-certificateNumbers-invalid.json` | `supplier/deferred-certificateNumbers` |
| `supplier-deferred-certifications-invalid.json` | `supplier/deferred-certifications` |
| `supplier-deferred-city-invalid.json` | `supplier/deferred-city` |
| `supplier-deferred-companyNumber-invalid.json` | `supplier/deferred-companyNumber` |
| `supplier-deferred-contactEmail-invalid.json` | `supplier/deferred-contactEmail` |
| `supplier-deferred-contactName-invalid.json` | `supplier/deferred-contactName` |
| `supplier-deferred-contactPerson-invalid.json` | `supplier/deferred-contactPerson` |
| `supplier-deferred-contactPhone-invalid.json` | `supplier/deferred-contactPhone` |
| `supplier-deferred-contacts-invalid.json` | `supplier/deferred-contacts` |
| `supplier-deferred-country-invalid.json` | `supplier/deferred-country` |
| `supplier-deferred-currency-invalid.json` | `supplier/deferred-currency` |
| `supplier-deferred-cuttingToolIds-invalid.json` | `supplier/deferred-cuttingToolIds` |
| `supplier-deferred-deliveryScore-invalid.json` | `supplier/deferred-deliveryScore` |
| `supplier-deferred-deliveryTerms-invalid.json` | `supplier/deferred-deliveryTerms` |
| `supplier-deferred-discount-invalid.json` | `supplier/deferred-discount` |
| `supplier-deferred-email-invalid.json` | `supplier/deferred-email` |
| `supplier-deferred-externalId-invalid.json` | `supplier/deferred-externalId` |
| `supplier-deferred-externalIdentifiers-invalid.json` | `supplier/deferred-externalIdentifiers` |
| `supplier-deferred-headquarters-invalid.json` | `supplier/deferred-headquarters` |
| `supplier-deferred-hourlyRate-invalid.json` | `supplier/deferred-hourlyRate` |
| `supplier-deferred-inventoryItems-invalid.json` | `supplier/deferred-inventoryItems` |
| `supplier-deferred-isApproved-invalid.json` | `supplier/deferred-isApproved` |
| `supplier-deferred-leadTime-invalid.json` | `supplier/deferred-leadTime` |
| `supplier-deferred-legalName-invalid.json` | `supplier/deferred-legalName` |
| `supplier-deferred-locationIds-invalid.json` | `supplier/deferred-locationIds` |
| `supplier-deferred-locations-invalid.json` | `supplier/deferred-locations` |
| `supplier-deferred-machineIds-invalid.json` | `supplier/deferred-machineIds` |
| `supplier-deferred-machines-invalid.json` | `supplier/deferred-machines` |
| `supplier-deferred-manufacturingProcesses-invalid.json` | `supplier/deferred-manufacturingProcesses` |
| `supplier-deferred-markup-invalid.json` | `supplier/deferred-markup` |
| `supplier-deferred-materialIds-invalid.json` | `supplier/deferred-materialIds` |
| `supplier-deferred-materialsSupported-invalid.json` | `supplier/deferred-materialsSupported` |
| `supplier-deferred-maxDiameter-invalid.json` | `supplier/deferred-maxDiameter` |
| `supplier-deferred-maxSize-invalid.json` | `supplier/deferred-maxSize` |
| `supplier-deferred-mergedInto-invalid.json` | `supplier/deferred-mergedInto` |
| `supplier-deferred-observationIds-invalid.json` | `supplier/deferred-observationIds` |
| `supplier-deferred-observations-invalid.json` | `supplier/deferred-observations` |
| `supplier-deferred-parentSupplierId-invalid.json` | `supplier/deferred-parentSupplierId` |
| `supplier-deferred-paymentTerms-invalid.json` | `supplier/deferred-paymentTerms` |
| `supplier-deferred-performanceHistory-invalid.json` | `supplier/deferred-performanceHistory` |
| `supplier-deferred-persons-invalid.json` | `supplier/deferred-persons` |
| `supplier-deferred-phone-invalid.json` | `supplier/deferred-phone` |
| `supplier-deferred-plants-invalid.json` | `supplier/deferred-plants` |
| `supplier-deferred-postalCode-invalid.json` | `supplier/deferred-postalCode` |
| `supplier-deferred-preferredSupplier-invalid.json` | `supplier/deferred-preferredSupplier` |
| `supplier-deferred-price-invalid.json` | `supplier/deferred-price` |
| `supplier-deferred-priceList-invalid.json` | `supplier/deferred-priceList` |
| `supplier-deferred-pricePerKg-invalid.json` | `supplier/deferred-pricePerKg` |
| `supplier-deferred-processIds-invalid.json` | `supplier/deferred-processIds` |
| `supplier-deferred-properties-invalid.json` | `supplier/deferred-properties` |
| `supplier-deferred-qualificationStatus-invalid.json` | `supplier/deferred-qualificationStatus` |
| `supplier-deferred-qualityScore-invalid.json` | `supplier/deferred-qualityScore` |
| `supplier-deferred-rating-invalid.json` | `supplier/deferred-rating` |
| `supplier-deferred-registeredAddress-invalid.json` | `supplier/deferred-registeredAddress` |
| `supplier-deferred-registrationNumber-invalid.json` | `supplier/deferred-registrationNumber` |
| `supplier-deferred-reliability-invalid.json` | `supplier/deferred-reliability` |
| `supplier-deferred-replacedBy-invalid.json` | `supplier/deferred-replacedBy` |
| `supplier-deferred-replaces-invalid.json` | `supplier/deferred-replaces` |
| `supplier-deferred-score-invalid.json` | `supplier/deferred-score` |
| `supplier-deferred-serviceProcessIds-invalid.json` | `supplier/deferred-serviceProcessIds` |
| `supplier-deferred-shippingAddress-invalid.json` | `supplier/deferred-shippingAddress` |
| `supplier-deferred-shippingCost-invalid.json` | `supplier/deferred-shippingCost` |
| `supplier-deferred-siteIds-invalid.json` | `supplier/deferred-siteIds` |
| `supplier-deferred-sites-invalid.json` | `supplier/deferred-sites` |
| `supplier-deferred-standardsHeld-invalid.json` | `supplier/deferred-standardsHeld` |
| `supplier-deferred-stockMaterialIds-invalid.json` | `supplier/deferred-stockMaterialIds` |
| `supplier-deferred-stockedMaterials-invalid.json` | `supplier/deferred-stockedMaterials` |
| `supplier-deferred-street-invalid.json` | `supplier/deferred-street` |
| `supplier-deferred-successorId-invalid.json` | `supplier/deferred-successorId` |
| `supplier-deferred-supplierCode-invalid.json` | `supplier/deferred-supplierCode` |
| `supplier-deferred-supplierType-invalid.json` | `supplier/deferred-supplierType` |
| `supplier-deferred-supportedProcesses-invalid.json` | `supplier/deferred-supportedProcesses` |
| `supplier-deferred-taxId-invalid.json` | `supplier/deferred-taxId` |
| `supplier-deferred-tolerances-invalid.json` | `supplier/deferred-tolerances` |
| `supplier-deferred-tools-invalid.json` | `supplier/deferred-tools` |
| `supplier-deferred-tradingName-invalid.json` | `supplier/deferred-tradingName` |
| `supplier-deferred-unknownField-invalid.json` | `supplier/deferred-unknownField` |
| `supplier-deferred-vatNumber-invalid.json` | `supplier/deferred-vatNumber` |
| `supplier-deferred-vendorCode-invalid.json` | `supplier/deferred-vendorCode` |
| `supplier-deferred-verificationStatus-invalid.json` | `supplier/deferred-verificationStatus` |
| `supplier-deferred-warehouses-invalid.json` | `supplier/deferred-warehouses` |
| `supplier-deferred-website-invalid.json` | `supplier/deferred-website` |
| `supplier-description-empty-invalid.json` | `supplier/description-empty` |
| `supplier-description-wrong-type-invalid.json` | `supplier/description-wrong-type` |
| `supplier-empty-object-invalid.json` | `supplier/empty-object` |
| `supplier-id-long-padding-invalid.json` | `supplier/id-long-padding` |
| `supplier-id-lowercase-invalid.json` | `supplier/id-lowercase` |
| `supplier-id-malformed-invalid.json` | `supplier/id-malformed` |
| `supplier-id-null-invalid.json` | `supplier/id-null` |
| `supplier-id-short-padding-invalid.json` | `supplier/id-short-padding` |
| `supplier-id-wrong-prefix-invalid.json` | `supplier/id-wrong-prefix` |
| `supplier-missing-changeSummary-invalid.json` | `supplier/missing-changeSummary` |
| `supplier-missing-createdAt-invalid.json` | `supplier/missing-createdAt` |
| `supplier-missing-createdBy-invalid.json` | `supplier/missing-createdBy` |
| `supplier-missing-id-invalid.json` | `supplier/missing-id` |
| `supplier-missing-name-invalid.json` | `supplier/missing-name` |
| `supplier-missing-recordVersion-invalid.json` | `supplier/missing-recordVersion` |
| `supplier-missing-revision-invalid.json` | `supplier/missing-revision` |
| `supplier-missing-schemaVersion-invalid.json` | `supplier/missing-schemaVersion` |
| `supplier-missing-sourceLinks-invalid.json` | `supplier/missing-sourceLinks` |
| `supplier-missing-status-invalid.json` | `supplier/missing-status` |
| `supplier-missing-updatedAt-invalid.json` | `supplier/missing-updatedAt` |
| `supplier-missing-updatedBy-invalid.json` | `supplier/missing-updatedBy` |
| `supplier-name-empty-invalid.json` | `supplier/name-empty` |
| `supplier-name-null-invalid.json` | `supplier/name-null` |
| `supplier-name-wrong-type-invalid.json` | `supplier/name-wrong-type` |
| `supplier-notes-wrong-type-invalid.json` | `supplier/notes-wrong-type` |
| `supplier-revision-negative-invalid.json` | `supplier/revision-negative` |
| `supplier-sourceLinks-malformed-invalid.json` | `supplier/malformed-source-link` |
| `supplier-sourceLinks-null-invalid.json` | `supplier/sourceLinks-null` |
| `supplier-sourceLinks-wrong-type-invalid.json` | `supplier/sourceLinks-wrong-type` |
| `supplier-status-business-value-invalid.json` | `supplier/status-business-value` |
| `manufacturing-process-array-root-invalid.json` | `manufacturing-process/array` |
| `manufacturing-process-classifications-wrong-type-invalid.json` | `manufacturing-process/classifications-wrong-type` |
| `manufacturing-process-deferred-Ra-invalid.json` | `manufacturing-process/deferred-Ra` |
| `manufacturing-process-deferred-abrasive-invalid.json` | `manufacturing-process/deferred-abrasive` |
| `manufacturing-process-deferred-accuracy-invalid.json` | `manufacturing-process/deferred-accuracy` |
| `manufacturing-process-deferred-achievableRoughness-invalid.json` | `manufacturing-process/deferred-achievableRoughness` |
| `manufacturing-process-deferred-achievableTolerance-invalid.json` | `manufacturing-process/deferred-achievableTolerance` |
| `manufacturing-process-deferred-aliases-invalid.json` | `manufacturing-process/deferred-aliases` |
| `manufacturing-process-deferred-alternativeNames-invalid.json` | `manufacturing-process/deferred-alternativeNames` |
| `manufacturing-process-deferred-alternativeTo-invalid.json` | `manufacturing-process/deferred-alternativeTo` |
| `manufacturing-process-deferred-approvedForProduction-invalid.json` | `manufacturing-process/deferred-approvedForProduction` |
| `manufacturing-process-deferred-approvedProcess-invalid.json` | `manufacturing-process/deferred-approvedProcess` |
| `manufacturing-process-deferred-atmosphere-invalid.json` | `manufacturing-process/deferred-atmosphere` |
| `manufacturing-process-deferred-broaderThan-invalid.json` | `manufacturing-process/deferred-broaderThan` |
| `manufacturing-process-deferred-camCode-invalid.json` | `manufacturing-process/deferred-camCode` |
| `manufacturing-process-deferred-capabilities-invalid.json` | `manufacturing-process/deferred-capabilities` |
| `manufacturing-process-deferred-capability-invalid.json` | `manufacturing-process/deferred-capability` |
| `manufacturing-process-deferred-capabilityLimits-invalid.json` | `manufacturing-process/deferred-capabilityLimits` |
| `manufacturing-process-deferred-capacity-invalid.json` | `manufacturing-process/deferred-capacity` |
| `manufacturing-process-deferred-children-invalid.json` | `manufacturing-process/deferred-children` |
| `manufacturing-process-deferred-conditions-invalid.json` | `manufacturing-process/deferred-conditions` |
| `manufacturing-process-deferred-consumables-invalid.json` | `manufacturing-process/deferred-consumables` |
| `manufacturing-process-deferred-coolant-invalid.json` | `manufacturing-process/deferred-coolant` |
| `manufacturing-process-deferred-cost-invalid.json` | `manufacturing-process/deferred-cost` |
| `manufacturing-process-deferred-costPerHour-invalid.json` | `manufacturing-process/deferred-costPerHour` |
| `manufacturing-process-deferred-costPerKg-invalid.json` | `manufacturing-process/deferred-costPerKg` |
| `manufacturing-process-deferred-currency-invalid.json` | `manufacturing-process/deferred-currency` |
| `manufacturing-process-deferred-cuttingSpeed-invalid.json` | `manufacturing-process/deferred-cuttingSpeed` |
| `manufacturing-process-deferred-cuttingToolIds-invalid.json` | `manufacturing-process/deferred-cuttingToolIds` |
| `manufacturing-process-deferred-cycleTime-invalid.json` | `manufacturing-process/deferred-cycleTime` |
| `manufacturing-process-deferred-depthOfCut-invalid.json` | `manufacturing-process/deferred-depthOfCut` |
| `manufacturing-process-deferred-designation-invalid.json` | `manufacturing-process/deferred-designation` |
| `manufacturing-process-deferred-documentIds-invalid.json` | `manufacturing-process/deferred-documentIds` |
| `manufacturing-process-deferred-effects-invalid.json` | `manufacturing-process/deferred-effects` |
| `manufacturing-process-deferred-electricity-invalid.json` | `manufacturing-process/deferred-electricity` |
| `manufacturing-process-deferred-energy-invalid.json` | `manufacturing-process/deferred-energy` |
| `manufacturing-process-deferred-equivalentTo-invalid.json` | `manufacturing-process/deferred-equivalentTo` |
| `manufacturing-process-deferred-erpCode-invalid.json` | `manufacturing-process/deferred-erpCode` |
| `manufacturing-process-deferred-externalCode-invalid.json` | `manufacturing-process/deferred-externalCode` |
| `manufacturing-process-deferred-externalIdentifiers-invalid.json` | `manufacturing-process/deferred-externalIdentifiers` |
| `manufacturing-process-deferred-feedRate-invalid.json` | `manufacturing-process/deferred-feedRate` |
| `manufacturing-process-deferred-gas-invalid.json` | `manufacturing-process/deferred-gas` |
| `manufacturing-process-deferred-hierarchyPath-invalid.json` | `manufacturing-process/deferred-hierarchyPath` |
| `manufacturing-process-deferred-hourlyRate-invalid.json` | `manufacturing-process/deferred-hourlyRate` |
| `manufacturing-process-deferred-inputState-invalid.json` | `manufacturing-process/deferred-inputState` |
| `manufacturing-process-deferred-inputStock-invalid.json` | `manufacturing-process/deferred-inputStock` |
| `manufacturing-process-deferred-inputTypes-invalid.json` | `manufacturing-process/deferred-inputTypes` |
| `manufacturing-process-deferred-inputs-invalid.json` | `manufacturing-process/deferred-inputs` |
| `manufacturing-process-deferred-inspectorQualification-invalid.json` | `manufacturing-process/deferred-inspectorQualification` |
| `manufacturing-process-deferred-instructions-invalid.json` | `manufacturing-process/deferred-instructions` |
| `manufacturing-process-deferred-level-invalid.json` | `manufacturing-process/deferred-level` |
| `manufacturing-process-deferred-machineIds-invalid.json` | `manufacturing-process/deferred-machineIds` |
| `manufacturing-process-deferred-machineTypes-invalid.json` | `manufacturing-process/deferred-machineTypes` |
| `manufacturing-process-deferred-machines-invalid.json` | `manufacturing-process/deferred-machines` |
| `manufacturing-process-deferred-materialConditionIn-invalid.json` | `manufacturing-process/deferred-materialConditionIn` |
| `manufacturing-process-deferred-materialConditionOut-invalid.json` | `manufacturing-process/deferred-materialConditionOut` |
| `manufacturing-process-deferred-materialIds-invalid.json` | `manufacturing-process/deferred-materialIds` |
| `manufacturing-process-deferred-materials-invalid.json` | `manufacturing-process/deferred-materials` |
| `manufacturing-process-deferred-maxDiameter-invalid.json` | `manufacturing-process/deferred-maxDiameter` |
| `manufacturing-process-deferred-maxLength-invalid.json` | `manufacturing-process/deferred-maxLength` |
| `manufacturing-process-deferred-measurementQuality-invalid.json` | `manufacturing-process/deferred-measurementQuality` |
| `manufacturing-process-deferred-minTolerance-invalid.json` | `manufacturing-process/deferred-minTolerance` |
| `manufacturing-process-deferred-narrowerThan-invalid.json` | `manufacturing-process/deferred-narrowerThan` |
| `manufacturing-process-deferred-normIds-invalid.json` | `manufacturing-process/deferred-normIds` |
| `manufacturing-process-deferred-observationIds-invalid.json` | `manufacturing-process/deferred-observationIds` |
| `manufacturing-process-deferred-observations-invalid.json` | `manufacturing-process/deferred-observations` |
| `manufacturing-process-deferred-operatorQualification-invalid.json` | `manufacturing-process/deferred-operatorQualification` |
| `manufacturing-process-deferred-outputState-invalid.json` | `manufacturing-process/deferred-outputState` |
| `manufacturing-process-deferred-outputTypes-invalid.json` | `manufacturing-process/deferred-outputTypes` |
| `manufacturing-process-deferred-outputs-invalid.json` | `manufacturing-process/deferred-outputs` |
| `manufacturing-process-deferred-parameterDefinitions-invalid.json` | `manufacturing-process/deferred-parameterDefinitions` |
| `manufacturing-process-deferred-parameterValues-invalid.json` | `manufacturing-process/deferred-parameterValues` |
| `manufacturing-process-deferred-parameters-invalid.json` | `manufacturing-process/deferred-parameters` |
| `manufacturing-process-deferred-parentIds-invalid.json` | `manufacturing-process/deferred-parentIds` |
| `manufacturing-process-deferred-parentProcessId-invalid.json` | `manufacturing-process/deferred-parentProcessId` |
| `manufacturing-process-deferred-personnelRequirements-invalid.json` | `manufacturing-process/deferred-personnelRequirements` |
| `manufacturing-process-deferred-price-invalid.json` | `manufacturing-process/deferred-price` |
| `manufacturing-process-deferred-processCode-invalid.json` | `manufacturing-process/deferred-processCode` |
| `manufacturing-process-deferred-processCost-invalid.json` | `manufacturing-process/deferred-processCost` |
| `manufacturing-process-deferred-processFamily-invalid.json` | `manufacturing-process/deferred-processFamily` |
| `manufacturing-process-deferred-processParameters-invalid.json` | `manufacturing-process/deferred-processParameters` |
| `manufacturing-process-deferred-processType-invalid.json` | `manufacturing-process/deferred-processType` |
| `manufacturing-process-deferred-processingTime-invalid.json` | `manufacturing-process/deferred-processingTime` |
| `manufacturing-process-deferred-properties-invalid.json` | `manufacturing-process/deferred-properties` |
| `manufacturing-process-deferred-qualificationStatus-invalid.json` | `manufacturing-process/deferred-qualificationStatus` |
| `manufacturing-process-deferred-qualified-invalid.json` | `manufacturing-process/deferred-qualified` |
| `manufacturing-process-deferred-qualityGrade-invalid.json` | `manufacturing-process/deferred-qualityGrade` |
| `manufacturing-process-deferred-recipe-invalid.json` | `manufacturing-process/deferred-recipe` |
| `manufacturing-process-deferred-recommendedTools-invalid.json` | `manufacturing-process/deferred-recommendedTools` |
| `manufacturing-process-deferred-replacedBy-invalid.json` | `manufacturing-process/deferred-replacedBy` |
| `manufacturing-process-deferred-replaces-invalid.json` | `manufacturing-process/deferred-replaces` |
| `manufacturing-process-deferred-requiredMachines-invalid.json` | `manufacturing-process/deferred-requiredMachines` |
| `manufacturing-process-deferred-roughness-invalid.json` | `manufacturing-process/deferred-roughness` |
| `manufacturing-process-deferred-serviceProviders-invalid.json` | `manufacturing-process/deferred-serviceProviders` |
| `manufacturing-process-deferred-settings-invalid.json` | `manufacturing-process/deferred-settings` |
| `manufacturing-process-deferred-setupCost-invalid.json` | `manufacturing-process/deferred-setupCost` |
| `manufacturing-process-deferred-setupTime-invalid.json` | `manufacturing-process/deferred-setupTime` |
| `manufacturing-process-deferred-shortName-invalid.json` | `manufacturing-process/deferred-shortName` |
| `manufacturing-process-deferred-specialProcessApproval-invalid.json` | `manufacturing-process/deferred-specialProcessApproval` |
| `manufacturing-process-deferred-spindleSpeed-invalid.json` | `manufacturing-process/deferred-spindleSpeed` |
| `manufacturing-process-deferred-standardIds-invalid.json` | `manufacturing-process/deferred-standardIds` |
| `manufacturing-process-deferred-standards-invalid.json` | `manufacturing-process/deferred-standards` |
| `manufacturing-process-deferred-stockForms-invalid.json` | `manufacturing-process/deferred-stockForms` |
| `manufacturing-process-deferred-stockMaterialIds-invalid.json` | `manufacturing-process/deferred-stockMaterialIds` |
| `manufacturing-process-deferred-substituteProcessIds-invalid.json` | `manufacturing-process/deferred-substituteProcessIds` |
| `manufacturing-process-deferred-supplierIds-invalid.json` | `manufacturing-process/deferred-supplierIds` |
| `manufacturing-process-deferred-suppliers-invalid.json` | `manufacturing-process/deferred-suppliers` |
| `manufacturing-process-deferred-supportedMaterialIds-invalid.json` | `manufacturing-process/deferred-supportedMaterialIds` |
| `manufacturing-process-deferred-supportedMaterials-invalid.json` | `manufacturing-process/deferred-supportedMaterials` |
| `manufacturing-process-deferred-surfaceFinish-invalid.json` | `manufacturing-process/deferred-surfaceFinish` |
| `manufacturing-process-deferred-synonyms-invalid.json` | `manufacturing-process/deferred-synonyms` |
| `manufacturing-process-deferred-timePerPart-invalid.json` | `manufacturing-process/deferred-timePerPart` |
| `manufacturing-process-deferred-tolerance-invalid.json` | `manufacturing-process/deferred-tolerance` |
| `manufacturing-process-deferred-toolIds-invalid.json` | `manufacturing-process/deferred-toolIds` |
| `manufacturing-process-deferred-tools-invalid.json` | `manufacturing-process/deferred-tools` |
| `manufacturing-process-deferred-transformedProperties-invalid.json` | `manufacturing-process/deferred-transformedProperties` |
| `manufacturing-process-deferred-treatmentTemperature-invalid.json` | `manufacturing-process/deferred-treatmentTemperature` |
| `manufacturing-process-deferred-treatmentTime-invalid.json` | `manufacturing-process/deferred-treatmentTime` |
| `manufacturing-process-deferred-unknownField-invalid.json` | `manufacturing-process/deferred-unknownField` |
| `manufacturing-process-deferred-validatedProcess-invalid.json` | `manufacturing-process/deferred-validatedProcess` |
| `manufacturing-process-deferred-validationStatus-invalid.json` | `manufacturing-process/deferred-validationStatus` |
| `manufacturing-process-deferred-verificationStatus-invalid.json` | `manufacturing-process/deferred-verificationStatus` |
| `manufacturing-process-deferred-welderQualification-invalid.json` | `manufacturing-process/deferred-welderQualification` |
| `manufacturing-process-deferred-weldingCurrent-invalid.json` | `manufacturing-process/deferred-weldingCurrent` |
| `manufacturing-process-deferred-weldingVoltage-invalid.json` | `manufacturing-process/deferred-weldingVoltage` |
| `manufacturing-process-deferred-workInstructions-invalid.json` | `manufacturing-process/deferred-workInstructions` |
| `manufacturing-process-deferred-wpsIds-invalid.json` | `manufacturing-process/deferred-wpsIds` |
| `manufacturing-process-description-wrong-type-invalid.json` | `manufacturing-process/description-wrong-type` |
| `manufacturing-process-empty-description-invalid.json` | `manufacturing-process/empty-description` |
| `manufacturing-process-empty-name-invalid.json` | `manufacturing-process/name-empty` |
| `manufacturing-process-empty-object-invalid.json` | `manufacturing-process/empty-object` |
| `manufacturing-process-invalid-classification-invalid.json` | `manufacturing-process/invalid-classification` |
| `manufacturing-process-lowercase-tec-invalid.json` | `manufacturing-process/lowercase-tec` |
| `manufacturing-process-malformed-source-link-invalid.json` | `manufacturing-process/malformed-source-link` |
| `manufacturing-process-malformed-tec-invalid.json` | `manufacturing-process/malformed-tec` |
| `manufacturing-process-missing-description-invalid.json` | `manufacturing-process/missing-description` |
| `manufacturing-process-missing-id-invalid.json` | `manufacturing-process/missing-id` |
| `manufacturing-process-missing-name-invalid.json` | `manufacturing-process/missing-name` |
| `manufacturing-process-missing-sourceLinks-invalid.json` | `manufacturing-process/missing-sourceLinks` |
| `manufacturing-process-name-wrong-type-invalid.json` | `manufacturing-process/name-wrong-type` |
| `manufacturing-process-notes-wrong-type-invalid.json` | `manufacturing-process/notes-wrong-type` |
| `manufacturing-process-null-description-invalid.json` | `manufacturing-process/description-null` |
| `manufacturing-process-null-id-invalid.json` | `manufacturing-process/id-null` |
| `manufacturing-process-null-name-invalid.json` | `manufacturing-process/name-null` |
| `manufacturing-process-null-sourceLinks-invalid.json` | `manufacturing-process/sourceLinks-null` |
| `manufacturing-process-sourceLinks-wrong-type-invalid.json` | `manufacturing-process/sourceLinks-wrong-type` |
| `manufacturing-process-wrong-prefix-invalid.json` | `manufacturing-process/wrong-prefix` |
| `manufacturing-process-wrong-tec-padding-invalid.json` | `manufacturing-process/wrong-tec-padding` |

## Príloha B: presný zoznam ponechaných aktív entít

### Platné fixtures (39)

- `tests/fixtures/valid/entities/material-conflicting-claims-valid.json`
- `tests/fixtures/valid/entities/material-description-valid.json`
- `tests/fixtures/valid/entities/material-empty-classifications-valid.json`
- `tests/fixtures/valid/entities/material-empty-properties-valid.json`
- `tests/fixtures/valid/entities/material-empty-source-links-valid.json`
- `tests/fixtures/valid/entities/material-minimal-draft-valid.json`
- `tests/fixtures/valid/entities/material-multiple-classifications-valid.json`
- `tests/fixtures/valid/entities/material-multiple-properties-valid.json`
- `tests/fixtures/valid/entities/material-notes-valid.json`
- `tests/fixtures/valid/entities/material-one-classification-valid.json`
- `tests/fixtures/valid/entities/material-one-property-valid.json`
- `tests/fixtures/valid/entities/material-populated-source-links-valid.json`
- `tests/fixtures/valid/entities/material-properties-classifications-valid.json`
- `tests/fixtures/valid/entities/material-replaced-by-valid.json`
- `tests/fixtures/valid/entities/material-replaces-valid.json`
- `tests/fixtures/valid/entities/material-same-property-multiple-valid.json`
- `tests/fixtures/valid/entities/supplier-approved-with-source-valid.json`
- `tests/fixtures/valid/entities/supplier-description-valid.json`
- `tests/fixtures/valid/entities/supplier-empty-classifications-valid.json`
- `tests/fixtures/valid/entities/supplier-empty-source-links-valid.json`
- `tests/fixtures/valid/entities/supplier-full-profile-valid.json`
- `tests/fixtures/valid/entities/supplier-minimal-draft-valid.json`
- `tests/fixtures/valid/entities/supplier-multiple-classifications-valid.json`
- `tests/fixtures/valid/entities/supplier-notes-valid.json`
- `tests/fixtures/valid/entities/supplier-one-classification-valid.json`
- `tests/fixtures/valid/entities/supplier-populated-source-links-valid.json`
- `tests/fixtures/valid/entities/supplier-review-with-source-valid.json`
- `tests/fixtures/valid/entities/supplier-without-classifications-valid.json`
- `tests/fixtures/valid/entities/manufacturing-process-approved-valid.json`
- `tests/fixtures/valid/entities/manufacturing-process-description-valid.json`
- `tests/fixtures/valid/entities/manufacturing-process-empty-classifications-valid.json`
- `tests/fixtures/valid/entities/manufacturing-process-empty-source-links-valid.json`
- `tests/fixtures/valid/entities/manufacturing-process-full-profile-valid.json`
- `tests/fixtures/valid/entities/manufacturing-process-minimal-draft-valid.json`
- `tests/fixtures/valid/entities/manufacturing-process-multiple-classifications-valid.json`
- `tests/fixtures/valid/entities/manufacturing-process-notes-valid.json`
- `tests/fixtures/valid/entities/manufacturing-process-one-classification-valid.json`
- `tests/fixtures/valid/entities/manufacturing-process-populated-source-links-valid.json`
- `tests/fixtures/valid/entities/manufacturing-process-review-valid.json`

Katalógový kontext: `tests/fixtures/catalog-context/fictional-catalog-context.json`.

### `tests/test_catalog_validation.py` (10)

- `test_material_preserves_nested_application_error_path`
- `test_material_replacement_reference_is_not_entity_resolved`
- `test_material_reuses_valid_property_and_classification_context`
- `test_material_surfaces_classification_reference_and_lifecycle`
- `test_material_surfaces_forbidden_and_disallowed_conditions`
- `test_material_surfaces_missing_condition_and_value_form_mismatch`
- `test_material_surfaces_missing_nested_unit`
- `test_material_surfaces_missing_property_reference`
- `test_material_surfaces_property_value_type_and_unit_policy`
- `test_schema_index_preserves_material_catalog_error_path`

### `tests/test_manufacturing_process_validation.py` (19)

- `test_assignment_sources_do_not_replace_root_sources`
- `test_common_metadata_refs_and_required_fields`
- `test_context_cls_lifecycle_default_and_authoring`
- `test_context_cls_type_check_is_reused`
- `test_context_missing_cls_keeps_nested_path_and_root_id`
- `test_context_requires_explicit_context_consistently`
- `test_context_valid_cls_and_multiple_assignments`
- `test_contract_only_needs_no_catalog_registry`
- `test_description_and_common_notes_semantics`
- `test_index_definition_resolves_without_entity_collection`
- `test_lifecycle_uses_record_status_not_business_status`
- `test_multiple_classifications_and_assignment_ref`
- `test_name_is_label_without_uniqueness_or_normalization`
- `test_nested_schema_errors_preserve_exact_paths`
- `test_observation_accepts_tec_subject_without_ownership`
- `test_process_root_source_rule_runs_once_with_explicit_flag`
- `test_required_description_and_inspection_label`
- `test_source_links_reuses_source_link_contract`
- `test_tec_reuses_exact_central_definition`

### `tests/test_material_migration.py` (3)

- `test_cls_lifecycle_matrix_on_material`
- `test_root_and_claim_sources_remain_independent`
- `test_unresolved_reference_has_no_dependent_diagnostics`

### `tests/test_supplier_validation.py` (18)

- `test_assignment_sources_do_not_replace_root_sources`
- `test_common_metadata_refs_and_required_fields`
- `test_context_cls_lifecycle_default_and_authoring`
- `test_context_cls_type_check_is_reused`
- `test_context_missing_cls_keeps_nested_path_and_root_id`
- `test_context_requires_explicit_context_consistently`
- `test_context_valid_cls_and_multiple_assignments`
- `test_contract_only_needs_no_catalog_registry`
- `test_description_and_common_notes_semantics`
- `test_index_definition_resolves_without_entity_collection`
- `test_lifecycle_uses_record_status_not_business_status`
- `test_multiple_classifications_and_assignment_ref`
- `test_name_is_label_without_uniqueness_or_normalization`
- `test_nested_schema_errors_preserve_exact_paths`
- `test_observation_accepts_sup_subject_without_ownership`
- `test_source_links_reuses_source_link_contract`
- `test_sup_reuses_exact_central_definition`
- `test_supplier_root_source_rule_runs_once_with_explicit_flag`

### `tests/test_validation.py` (8)

- `test_material_preserves_duplicate_and_conflicting_claims`
- `test_material_rejects_root_conditions_but_allows_nested_condition`
- `test_material_replacement_links_are_structural_mat_references`
- `test_material_reuses_central_mat_and_common_metadata`
- `test_material_reuses_property_record_classification_and_source_link`
- `test_material_root_source_rule_runs_once_with_explicit_flag`
- `test_material_source_lifecycle_rule_is_composed`
- `test_schema_index_resolves_material`

## Príloha C: odstránené metódy podľa modulu

### `tests/test_entity_profiles.py` (2)

- `test_manufacturing_process_legacy_equivalence`
- `test_supplier_pilot_equivalence`

### `tests/test_manufacturing_process_validation.py` (8)

- `test_every_deferred_fixture_fails_as_unknown_field`
- `test_invalid_fixture_expected_reason_and_path`
- `test_invalid_fixtures`
- `test_minimum_needs_no_optional_or_deferred_fields`
- `test_review_approved_require_root_provenance`
- `test_schema_definition_and_closed_shape`
- `test_source_links_required_with_exact_path`
- `test_valid_fixtures`

### `tests/test_material_migration.py` (1)

- `test_legacy_input_and_diagnostic_equivalence`

### `tests/test_supplier_validation.py` (7)

- `test_every_deferred_fixture_fails_as_unknown_field`
- `test_invalid_fixtures`
- `test_minimum_needs_no_optional_or_deferred_fields`
- `test_review_approved_require_root_provenance`
- `test_schema_definition_and_closed_shape`
- `test_source_links_required_with_exact_path`
- `test_valid_fixtures`

### `tests/test_validation.py` (5)

- `test_invalid_material_fixtures_fail`
- `test_material_minimum_keeps_knowledge_fields_optional`
- `test_material_rejects_deferred_and_foreign_root_fields`
- `test_material_schema_definition_is_valid`
- `test_valid_material_fixtures_pass`

## Change History

| Dátum | Revízia | Zmena |
| --- | ---: | --- |
| 2026-11-06 | 0 | Lokálne closure: dôkazy, inventár, citlivosť a verdikt pred finálnym review. |

ADR-0017 MIGRATION COMPLETE – MACHINE BLOCKER CLOSED
