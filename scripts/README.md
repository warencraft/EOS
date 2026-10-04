# scripts

## Míľnik 0.2C.1 - Material Entity v1

Validátor registruje `https://eos.local/schemas/entities/material.schema.json` ako prvú Knowledge Entity schému. Existing contract composition rekurzívne aplikuje vnorené ValueRange a MeasurementQuality pravidlá na `properties[]`; root lifecycle/source helper povoľuje prázdne zdroje v Draft a vyžaduje ich v Review/Approved.

Context-aware cesta deleguje každý `properties[index]` existujúcej PropertyRecord/PRP/CND/UNT validácii a každý `classifications[index]` existujúcej Classification/CLS validácii. Kategórie `reference_integrity`, `catalog_validation` a `application_validation` sa nemenia a cesty zostávajú Material-prefixed.

Nevznikol Material-local compatibility engine ani generic entity resolver. `replaces` a `replacedBy` sa kontrolujú iba štrukturálne ako centrálne MAT identifikátory; existencia cieľa, cykly a obojsmerná konzistencia zostávajú budúcej persistence/entity vrstve.

## Míľnik 0.2B.2.5 - Catalog-aware / Reference-integrity Integration

`scripts/validation/catalog_context.py` zavádza immutable in-memory `CatalogRegistry` so samostatnými read-only mapami pre UNT, CND, PRP a CLS. Registry nepristupuje k súborom ani databáze a očakáva, že vstupné položky už prešli vlastným katalógovým kontraktom. Duplicate stable ID a registrácia položky pod nesprávnou katalógovou rodinou zlyhajú fail-closed.

`ValidationContext` nesie registry snapshot a explicitnú `CatalogLifecyclePolicy`. Default policy povoľuje Approved, povoľuje Deprecated s warningom a odmieta Draft, Review a Archived. Authoring policy navyše povoľuje Draft a Review; Archived zostáva odmietnutý.

Pôvodné `validate(...)` a `validate_json_file(...)` zostávajú contract-only. Plná katalógová kontrola používa výhradne explicitné:

```python
validator.validate_with_context(instance, schema_id, context)
validator.validate_json_file_with_context(path, schema_id, context)
```

Bez contextu tieto entry pointy vrátia `catalog_validation.context_required`; kontroly sa ticho nepreskočia. `ValidationResult.executedLayers` rozlišuje vykonané vrstvy a `ValidationError.referencedId` nesie cieľové ID. Warning na Deprecated položku je dostupný cez `ValidationResult.warnings` a sám nespôsobí neplatný výsledok.

`reference_integrity` overuje existenciu a katalógový typ UNT/CND/PRP/CLS. `catalog_validation` overuje lifecycle, Property value type, result unit allow-list, Condition allow-list, CND value form a reference prefix. PropertyRecord a Observation používajú spoločnú property compatibility implementáciu; samostatné aj vnorené Conditions používajú spoločnú CND implementáciu. MeasurementQuality jednotky podliehajú UNT existencii, nie Property unit allow-listu.

Condition `referenceId` sa v tejto fáze kontroluje iba podľa povoleného prefixu. Entity, SourceReference a všeobecná existencia takéhoto cieľa zostávajú odložené do 0.2C. Implementácia neobsahuje loader, persistence, konverzie, dimenzionálnu inferenciu ani reálne katalógové dáta.

## Míľnik 0.2B.2.4 - Classification Catalog v1

Validátor registruje Classification Catalog Entry ako samostatný kontrakt a ako položku `classificationCatalogEntries` v schema indexe. Existujúca kompozičná mapa aplikuje rovnaké lifecycle/source pravidlo na priamu aj indexom vnorenú položku: Draft môže mať prázdne `sourceLinks`, kým Review alebo Approved bez definition provenance vracia `application_validation.source_links_required` s presnou cestou.

JSON Schema kontroluje CLS, common metadata, lifecycle, povinný name a description, SourceLink, replacement CLS odkazy a zákaz neznámych alebo deferred polí. Validátor nekontroluje existenciu alebo použiteľnosť CLS cieľov, kompatibilitu embedded Classification s rodičom, classification systems, external codes, hierarchy, aliases, equivalence ani assignment multiplicity. Nevznikla nová validačná vetva; pridaná bola iba registrácia do existujúcej kompozície.

## Míľnik 0.2B.2.3 - Property Catalog v1

Validátor registruje Property Catalog Entry ako samostatný kontrakt a ako položku `propertyCatalogEntries` v schema indexe. Existujúca kompozičná mapa aplikuje rovnaké lifecycle/source pravidlo na priamu aj indexom vnorenú položku: Draft môže mať prázdne `sourceLinks`, kým Review alebo Approved bez provenance vracia `application_validation.source_links_required` s presnou cestou.

JSON Schema kontroluje PRP, common metadata, lifecycle, povinný name a description, neprázdne unique `allowedValueTypes`, presný UNT allow-list, voliteľný CND allow-list, SourceLink, replacement PRP odkazy a zákaz neznámych alebo deferred polí.

Validátor zatiaľ nekontroluje existenciu PRP/UNT/CND záznamov ani kompatibilitu PropertyRecord alebo Observation s value-type, unit alebo condition allow-listom. Nevykonáva dimension inference, conversion, required Conditions ani MeasurementQuality policy. Nevznikla nová validačná vetva; pridaná bola iba registrácia do existujúcej kompozície.

## Míľnik 0.2B.2.2 - Condition Type Catalog v1

Validátor registruje Condition Type Catalog Entry ako samostatný kontrakt a ako položku `conditionTypeCatalogEntries` v schema indexe. Existujúca kompozičná mapa aplikuje rovnaké lifecycle/source pravidlo na priamu aj indexom vnorenú položku: Draft môže mať prázdne `sourceLinks`, kým Review alebo Approved bez provenance vracia `application_validation.source_links_required` s presnou cestou.

JSON Schema kontroluje CND, common metadata, lifecycle, name, neprázdne unikátne `allowedValueForms`, podmienenú uzavretú `allowedReferencePrefixes` policy, SourceLink, replacement CND odkazy a zákaz neznámych alebo deferred polí.

Validátor zatiaľ nekontroluje existenciu `Condition.conditionTypeId`, kompatibilitu konkrétnej hodnotovej formy s CND položkou, existenciu alebo typ `referenceId` cieľa, evaluation mode, jednotky, multiplicitu, duplicity ani logické kombinácie. Tieto pravidlá zostávajú budúcej catalog-aware/reference-integrity integrácii; existujúca Condition schéma sa nezmenila.

## Míľnik 0.2B.2.1 - Unit Catalog v1

Validátor registruje Unit Catalog Entry ako samostatný kontrakt a ako položku `unitCatalogEntries` v schema indexe. Existujúca kompozičná mapa aplikuje rovnaké lifecycle/source pravidlo na priamy záznam aj na záznam vnorený cez index: Draft môže mať prázdne `sourceLinks`, kým Review alebo Approved bez zdroja vracia `application_validation.source_links_required` s presnou cestou.

JSON Schema kontroluje UNT formát, common metadata, lifecycle enum, povinný name a symbol, SourceLink, replacement UNT referencie a zákaz neznámych alebo deferred polí. Validátor nekontroluje existenciu UNT cieľov, symbolovú unikátnosť, semantic equivalence, quantity kind, dimension, conversion ani replacement cykly.

## Míľnik 0.2B.1.7 - Observation Contract

Existujúca kompozičná mapa validátora registruje Observation ako rodiča Quantity, ValueRange, MeasurementQuality a poľa Conditions. Rovnaké pravidlá sa tým aplikujú na top-level Observation aj na Observation vnorenú cez schema index, bez kopírovania významovej logiky.

JSON Schema kontroluje entity metadata, OBS a subject ID formáty, GLOBAL/JOB scope podmienky, timestamp, PRP, result discriminator, vnorené kontrakty a uzavretý zoznam polí. EOS aplikačná vrstva kontroluje existujúce ValueRange a MeasurementQuality invarianty a neprázdne zdroje pre Review/Approved Observation. Source pravidlo znovu používa existujúci error model a pri vnorení zachováva úplnú cestu.

Validátor nekontroluje existenciu subjektu, JOB alebo PRP, katalógovú kompatibilitu, nemennosť uloženého záznamu, korekcie ani Decision workflow. Tieto kontroly nemožno vydávať za vykonané iba na základe platného formátu ID alebo úspešnej schémy.

## Míľnik 0.2B.1.6 - PropertyRecord Contract

EOS aplikačná validácia používa explicitnú mapu kompozície Knowledge Core kontraktov. Existujúce pravidlá ValueRange a MeasurementQuality sa tým spúšťajú aj pri vnorení v PropertyRecord a zachovávajú úplnú cestu chyby. Condition je zapojený do rovnakej orchestrácie, takže jeho prípadné budúce významové pravidlá sa budú aplikovať bez kopírovania do PropertyRecord.

JSON Schema naďalej kontroluje discriminator, presne jednu hodnotovú vetvu, vnorené `$ref`, VerificationStatus, SourceLink a zákaz neznámych polí. Aplikačná vrstva kontroluje iba existujúce významové invarianty. Nekontroluje PRP existenciu, kompatibilitu jednotiek, povolenú hodnotovú formu podľa katalógu ani Decision workflow.

Samostatná PropertyRecord validácia nemá lifecycle rodiča. `sourceLinks: []` preto môže byť štrukturálne platné a validátor nepredstiera kontextovú evidence kontrolu. Rodičovská integračná vrstva musí neskôr odovzdať explicitný kontext.

## Míľnik 0.2B.1.4 - Condition Contract

Pre `Condition` zostáva validácia v tomto míľniku schema-only:

- JSON Schema kontroluje objekt, povinné `conditionTypeId`, centrálny `CND-xxxxxx` formát, `evaluationMode`, presne jednu hodnotovú formu, vnorené `$ref` na `Quantity` a `ValueRange`, neprázdne textové a referenčné hodnoty a zákaz neznámych polí.
- EOS aplikačná validačná vrstva sa nemení, pretože existencia Condition Type Catalog položky, kompatibilita hodnotovej formy, dimenzionálna kompatibilita a skutočné vyhodnotenie podmienky sú odložené.

Validačná vrstva nevytvára Condition Type Catalog, nevykonáva unit conversion, nehodnotí splnenie podmienky a nemodeluje manufacturing tolerance.

## Míľnik 0.2B.1.3 - MeasurementQuality Contract

Pre `MeasurementQuality` zostáva validácia rozdelená na dve vrstvy:

- JSON Schema kontroluje objekt, známe polia, notes-only pravidlo, vnorené `Quantity` cez `$ref`, `confidenceLevel` v rozsahu 0 až 1 a zákaz neznámych polí.
- EOS aplikačná validácia kontroluje významové pravidlá `uncertainty.value >= 0` a `resolution.value > 0`.

Validačná vrstva nevykonáva prevody jednotiek, nekontroluje existenciu Unit Catalog položky, nemodeluje tolerancie a nevytvára MeasurementMethod ani Instrument kontrakt.

## Míľnik 0.2B.1.2 - ValueRange Contract

Pre `ValueRange` zostáva validácia rozdelená na dve vrstvy:

- JSON Schema kontroluje štruktúru, typy, `unitId`, aspoň jednu hranicu, väzbu inkluzivity na hranicu a neznáme polia.
- EOS aplikačná validácia kontroluje významové pravidlá `minValue <= maxValue`, `lowerInclusive` bez `minValue` a `upperInclusive` bez `maxValue`.

Validačná vrstva nevykonáva prevody jednotiek, nekontroluje existenciu Unit Catalog položky a nezavádza konkrétne jednotky ani technické hodnoty.

## Míľnik 0.2B.1.1 - Quantity Contract

Validačná vrstva ostáva rozdelená na štandardnú JSON Schema validáciu cez `jsonschema` a EOS aplikačné pravidlá.

Pre `Quantity` sa štrukturálne kontrolujú povinné polia, typ `number`, centrálny `UNT-xxxxxx` identifikátor a `additionalProperties: false`.

Aplikačná vrstva genericky odmieta nekonečné a nečíselné numerické hodnoty ako `NaN` a `Infinity`, aby value objecty používali iba konečné numerické hodnoty.

Tento priečinok je určený pre budúce pomocné skripty.

Skripty musia byť účelové, testovateľné a nesmú obsahovať hardcoded strojárske hodnoty.

## validation

`scripts/validation/` obsahuje štandardnú JSON Schema Draft 2020-12 validáciu cez `jsonschema` a oddelenú EOS aplikačnú validačnú vrstvu. Balík `jsonschema` je priamou projektovou závislosťou; jeho tranzitívna závislosť `referencing` poskytuje štandardný register pre lokálne a cross-file `$ref`.

Validácia rozlišuje:

- syntaktickú kontrolu JSON záznamov proti podporovanej podmnožine JSON Schema,
- aplikačné pravidlá EOS, napríklad významové pravidlo pre `sourceLinks`.

Od fázy 0.2A.2 používa štrukturálna validácia knižnicu `jsonschema` a `Draft202012Validator`.

Interná EOS vrstva zostáva zodpovedná za aplikačné pravidlá, napríklad `sourceLinks`, hierarchické ID a rozlíšenie `schemaVersion` vs `documentVersion`.

Ak chýba `jsonschema` alebo `referencing`, validačný nástroj zobrazí názov chýbajúcej závislosti a inštalačný postup. Kompletná testovacia sada zlyhá s nenulovým návratovým kódom; integračná validácia sa nesmie vykázať ako úspešná ani hromadne preskočená.

## Lokálne spustenie

V koreňovom priečinku projektu:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m unittest discover -s tests -p "test_*.py" -v
```

Ak príkaz `py` nie je dostupný, použi cestu k dostupnému Pythonu 3.11 alebo novšiemu.
