# schemas

## Míľnik 0.2C.1 - Material Entity v1

Prvá first-class Knowledge Entity schéma je `entities/material.schema.json`. Priečinok `entities/` je konvencia pre samostatné entity kontrakty; tento míľnik nevytvára generic entity framework ani collection/container schému.

Material je condition-neutral Entity a Aggregate Root:

- schema id: `https://eos.local/schemas/entities/material.schema.json`,
- discovery: `index.schema.json#/$defs/material`, indexová kolekcia `materials`,
- stabilné `id` používa výhradne centrálny `common/identifiers.schema.json#/$defs/MAT` vo formáte `MAT-xxxx`,
- povinné sú common entity metadata, `sourceLinks` a neprázdny `name`,
- voliteľné sú `description`, `properties`, `classifications`, `notes`, `replaces` a `replacedBy`.

`properties` obsahuje rodičom vlastnené PropertyRecord claims a `classifications` rodičom vlastnené Classification assignments. Opakované PRP aj konfliktné claims sú povolené. Conditions sú prípustné iba vo vnútri PropertyRecord, nie na Material root. Material nevlastní Observation ani StockMaterial.

Draft môže mať prázdne root `sourceLinks`; Review a Approved vyžadujú root provenance cez EOS aplikačnú vrstvu. Claim a assignment provenance zostávajú na vnorených objektoch. Replacement MAT odkazy sú zatiaľ iba štrukturálne a ich existencia sa nekontroluje.

V1 neobsahuje designation, root material condition, chemical composition, structured NormReference väzbu, Supplier údaje, stock form ani process/machine/tool compatibility. Fixtures neobsahujú reálne Material znalosti. Phase 0.2C.1 je implementovaná a čaká na samostatné closure review.

## Aktuálny stav po Phase 0.2B.2

EOS má sedem implementovaných Knowledge Core kontraktov: `Quantity`, `ValueRange`, `MeasurementQuality`, `Condition`, `Classification`, `PropertyRecord` a `Observation`. Katalógovú vrstvu tvoria štyri samostatné Catalog Entry Aggregate Roots: Unit Catalog Entry a Classification Catalog Entry ako Reference Catalog položky a Condition Type Catalog Entry a Property Catalog Entry ako Knowledge Catalog položky. Všetky kontrakty sú dostupné cez `index.schema.json`.

JSON Schema naďalej overuje iba štruktúru dátových kontraktov. Runtime existencia a typ UNT, CND, PRP a CLS cieľov sa overujú vo vrstve `reference_integrity`; lifecycle a významová kompatibilita sa overujú vo vrstve `catalog_validation` s explicitným `ValidationContext` a immutable `CatalogRegistry`. Contract-only validácia tieto runtime tvrdenia neposkytuje.

Repozitár neobsahuje reálne produkčné katalógové dáta, persistence ani všeobecný entity resolver. Phase 0.2B.2 je technicky dokončená; Phase 0.2C nebola implementovaná. Nasledujúce sekcie zachovávajú historický stav jednotlivých míľnikov v čase ich dokončenia.

## Míľnik 0.2B.2.4 - Classification Catalog v1

Classification Catalog je Reference Catalog. Jeho položka je samostatný Catalog Entry Aggregate Root:

- schéma: `catalogs/classification-catalog-entry.schema.json`,
- schema id: `https://eos.local/schemas/catalogs/classification-catalog-entry.schema.json`,
- discovery: `index.schema.json#/$defs/classificationCatalogEntry`, kolekcia `classificationCatalogEntries`,
- identita: centrálne `CLS-xxxxxx`,
- povinné sú common metadata, `name`, `description` a `sourceLinks`,
- voliteľné sú `notes`, `replaces` a `replacedBy`.

`name` je canonical human-readable label, nie identita ani globálne unikátna hodnota. `description` je autoritatívna textová definícia CLS významu, ale nie machine-readable taxonómia. Metadata, lifecycle a SourceLink sa používajú rovnako ako pri ostatných katalógoch: Draft môže mať prázdne `sourceLinks`, kým Review/Approved bez definition provenance je aplikačne neplatný. Root nemá `verificationStatus`; replacement odkazy používajú iba CLS.

Catalog Entry `sourceLinks` nesú provenance definície. Embedded `Classification.sourceLinks` nesú provenance konkrétneho priradenia. V1 je system-neutral: nemá Classification System model, external code, hierarchiu, aliases, equivalence ani target-entity restrictions. Catalog-aware kontrola existencie a použiteľnosti CLS zostáva odložená a nevznikla žiadna reálna CLS položka.

Phase 0.2B.2.4 je dokončená. Celá Phase 0.2B.2 zostáva rozpracovaná; nasleduje `Phase 0.2B.2.5-prep - Catalog-aware / Reference-integrity Integration Review`.

## Míľnik 0.2B.2.3 - Property Catalog v1

Property Catalog je Knowledge Catalog. Jeho položka je samostatný Catalog Entry Aggregate Root:

- schéma: `catalogs/property-catalog-entry.schema.json`,
- schema id: `https://eos.local/schemas/catalogs/property-catalog-entry.schema.json`,
- discovery: `index.schema.json#/$defs/propertyCatalogEntry`, kolekcia `propertyCatalogEntries`,
- identita: centrálne `PRP-xxxxxx`,
- povinné sú common metadata, `name`, `description`, `allowedValueTypes` a `allowedUnitIds`,
- voliteľné sú `allowedConditionTypeIds`, `notes`, `replaces` a `replacedBy`.

`allowedValueTypes` je neprázdny unique zoznam jednej alebo oboch aktuálnych číselných foriem `quantity` a `valueRange`. `allowedUnitIds` je neprázdny unique zoznam UNT a predstavuje iba presný whitelist; nevyjadruje rozmerovú kompatibilitu, konverziu ani canonical unit. Voliteľné `allowedConditionTypeIds` je neprázdny unique CND allow-list. Jeho neprítomnosť znamená, že Conditions nie sú pre property povolené, ale vynútenie voči PropertyRecord a Observation zostáva catalog-aware validácii.

Metadata, lifecycle a SourceLink sa znovu používajú rovnakým spôsobom ako pri Unit a Condition Type katalógu. Draft môže mať prázdne `sourceLinks`; Review/Approved bez provenance je aplikačne neplatný. Root nemá `verificationStatus`. Replacement odkazy používajú iba PRP.

V1 nemá canonical unit, required Conditions, multiplicitu, MeasurementQuality policy, classifications, aliases, equivalence, quantity kind, dimension ani conversion. Nevznikla žiadna reálna PRP položka. Phase 0.2B.2.3 je dokončená; celá Phase 0.2B.2 zostáva rozpracovaná a nasleduje `Phase 0.2B.2.4-prep - Classification Catalog Pre-design Review`.

## Míľnik 0.2B.2.2 - Condition Type Catalog v1

Condition Type Catalog je Knowledge Catalog. Jeho položka je samostatný Catalog Entry Aggregate Root:

- schéma: `catalogs/condition-type-catalog-entry.schema.json`,
- schema id: `https://eos.local/schemas/catalogs/condition-type-catalog-entry.schema.json`,
- discovery: `index.schema.json#/$defs/conditionTypeCatalogEntry`, kolekcia `conditionTypeCatalogEntries`,
- identita: centrálne `CND-xxxxxx`,
- povinné sú common entity metadata, `name` a `allowedValueForms`,
- voliteľné sú `description`, `notes`, `replaces` a `replacedBy`.

`allowedValueForms` je neprázdny unique zoznam jednej alebo viacerých existujúcich Condition foriem: `quantity`, `valueRange`, `textValue`, `booleanValue`, `referenceId`. Jedna Condition stále obsahuje presne jednu formu. Ak zoznam obsahuje `referenceId`, položka musí uviesť neprázdne unique `allowedReferencePrefixes`; bez `referenceId` je toto pole zakázané. Prefixová policy presne zodpovedá aktuálnemu Condition reference unionu a nepotvrdzuje existenciu cieľa.

Metadata používajú property-level `$ref` na common metadata rovnako ako Unit Catalog v1. Lifecycle je `Draft`, `Review`, `Approved`, `Deprecated`, `Archived`; root nemá `verificationStatus`. `sourceLinks` je required, Draft môže byť prázdny a Review/Approved bez provenance je aplikačne neplatný. Replacement odkazy používajú iba CND.

V1 neobsahuje evaluation-mode policy, jednotkové obmedzenia, quantity kind, dimension, multiplicitu, aliases, logické výrazy ani rule engine. Catalog-aware kontrola existencie a kompatibility Condition, reference integrity a Property Catalog pravidlá zostávajú odložené. Nevznikla žiadna reálna CND položka.

Phase 0.2B.2.2 je dokončená. Celá Phase 0.2B.2 zostáva rozpracovaná; nasleduje `Phase 0.2B.2.3-prep - Property Catalog Pre-design Review`.

## Míľnik 0.2B.2.1 - Unit Catalog v1

Prvý Reference Catalog kontrakt je `Unit Catalog Entry`, samostatný Catalog Entry Aggregate Root:

- schéma: `catalogs/unit-catalog-entry.schema.json`,
- schema id: `https://eos.local/schemas/catalogs/unit-catalog-entry.schema.json`,
- discovery: `index.schema.json#/$defs/unitCatalogEntry`, kolekcia `unitCatalogEntries`,
- stabilné `id` používa centrálny `UNT-xxxxxx`,
- povinné sú common entity metadata, `name` a `symbol`,
- voliteľné sú `description`, `notes`, `replaces` a `replacedBy`.

Unit Catalog je Reference Catalog. `UNT` identifikuje položku, nie názov alebo symbol. Symbol je case-sensitive Unicode display metadata a nie je globálne unikátny. `unitId` zostáva referenčným poľom Quantity a ValueRange; nie je identitou Unit Catalog Entry.

Metadata obmedzenia sa znovu používajú property-level `$ref` odkazmi na `common/metadata.schema.json`, pretože uzavretý common metadata objekt nemožno priamo rozšíriť o katalógové polia. Lifecycle používa `Draft`, `Review`, `Approved`, `Deprecated` a `Archived`; root nemá `verificationStatus`. `sourceLinks` je required, Draft môže byť prázdny a Review/Approved bez zdroja je aplikačne neplatný.

`replaces` a `replacedBy` sú priame one-to-one UNT referencie bez vnoreného vlastníctva. Existencia cieľa a cykly zostávajú budúcej catalog-aware/reference-integrity validácii.

V1 neobsahuje quantity kind, dimension, unit system, aliasy, ekvivalenciu ani conversion metadata alebo engine. Nevznikla žiadna reálna Unit Catalog položka; fixtures sú iba fiktívne validačné príklady. Phase 0.2B.2.1 je dokončená, celá Phase 0.2B.2 zostáva rozpracovaná.

## Míľnik 0.2B.1.7 - Observation Contract

Siedmy Knowledge Core Contract je `Observation`, first-class evidence Entity a Aggregate Root. Počiatočný profil je zámerne obmedzený na jedno číselné pozorovanie jednej vlastnosti jedného EOS subjektu:

- schéma: `knowledge-core/observation.schema.json`,
- schema id: `https://eos.local/schemas/knowledge-core/observation.schema.json`,
- discovery: `index.schema.json#/$defs/observation`, kolekcia `observations`,
- vlastné `id` používa centrálny `OBS-xxxxxx`,
- `subjectId` povoľuje centrálne MAT, POL, TEC, MAC, TOOL, SUP, JOB a JOB_OPERATION rodiny,
- scope je `GLOBAL` bez referencie alebo `JOB` s povinným `scopeReferenceId`,
- `propertyId`, `valueType` a presne jedna Quantity alebo ValueRange vetva tvoria jediný observed result,
- voliteľné `measurementQuality`, `conditions` a `notes`.

Spoločné entity metadata sa používajú priamo bez druhého wrappera. Jednotlivé metadata polia odkazujú na spoločnú metadata schému; `id` má špecializovaný centrálny OBS formát. `observedAt` je čas technického pozorovania, zatiaľ čo `createdAt` je čas vytvorenia EOS záznamu. Poradie medzi nimi sa nevynucuje.

Observation je evidence, nie embedded `PropertyRecord`, Claim, Decision ani Derived Result. Nepovoľuje arbitrary payload, `textValue`, `subjectType`, `observationType`, `observedBy`, `recordedAt`, koreňový `verificationStatus` ani korekčné polia. MeasurementQuality a Conditions kvalifikujú jediný výsledok. Ich existujúce významové pravidlá sa aplikujú rekurzívne bez kopírovania validátorov.

`sourceLinks` je štrukturálne povinné pole a Draft môže použiť prázdny zoznam. Review alebo Approved Observation bez zdroja je aplikačne neplatná. Formát ID nepotvrdzuje existenciu subjektu, JOB, PRP, UNT ani CND záznamu. PROJECT/EXPERIMENT, všeobecné a nečíselné výsledky, attachment, actor, evidence verification, correction relation a katalógové pravidlá zostávajú deferred.

Míľnik 0.2B.1.7 je implementovaný v stave Review. Sedem plánovaných Knowledge Core kontraktov má technickú implementáciu, ale Phase 0.2B.2 nezačala.

## Míľnik 0.2B.1.6 - PropertyRecord Contract

Šiesty Knowledge Core Contract je `PropertyRecord`, embedded claim-like Value Object vlastnený rodičom:

- schéma: `knowledge-core/property-record.schema.json`,
- schema id: `https://eos.local/schemas/knowledge-core/property-record.schema.json`,
- discovery: `index.schema.json#/$defs/propertyRecord`, kolekcia `propertyRecords`,
- povinné `propertyId`, `valueType`, `verificationStatus`, `sourceLinks` a presne jedna hodnotová vetva,
- `valueType` povoľuje iba `quantity` a `valueRange` a musí zodpovedať rovnomennej vetve,
- voliteľné `measurementQuality` a pole `conditions`; prázdne `conditions` je prípustné.

`propertyId` používa centrálny `PRP-xxxxxx` a označuje budúci Property Catalog Entry, nie identitu vnorenej inštancie. Kontrakt nemá vlastné ID, lifecycle ani verziu. Neumožňuje `textValue`, `booleanValue`, `referenceId`, classification, koreňové notes ani voľný JSON.

`sourceLinks` je štrukturálne povinné pole existujúcich SourceLink objektov, ale môže byť prázdne. Kontextová povinnosť reálneho dôkazu závisí od rodiča a budúceho workflow; samostatná validácia PropertyRecord tento kontext nepredstiera. `verificationStatus` overuje tvrdenie a používa `Draft`, `Reviewed`, `Approved`, `Disputed`; nie je lifecycle rodiča.

Quantity, ValueRange, MeasurementQuality a Condition sa používajú cez `$ref`. Významové pravidlá vnoreného ValueRange a MeasurementQuality vykonáva EOS aplikačná vrstva. Property Catalog v 0.2B.2 doplní existenciu PRP, povolený typ hodnoty, jednotkovú a rozmerovú kompatibilitu, povinné podmienky a doménové rozsahy. Observation zostáva dôkazom a Decision budúcim explicitným mechanizmom prijatia; žiadny z nich nevznikol v tomto míľniku.

Dokončený je iba rozsah Phase 0.2B.1.6. Celá Phase 0.2B.1 zostáva rozpracovaná a Phase 0.2B.2 nezačala.

## Míľnik 0.2B.1.5 - Classification Contract

Piaty Knowledge Core Contract je `Classification`, embedded reference Value Object vlastnený rodičom:

- schéma: `knowledge-core/classification.schema.json`,
- schema id: `https://eos.local/schemas/knowledge-core/classification.schema.json`,
- discovery: `index.schema.json#/$defs/classification`, kolekcia `classifications`,
- povinné `classificationId` cez centrálny `common/identifiers.schema.json#/$defs/CLS`,
- nepovinné `sourceLinks` ako pole existujúcich `common/source-link.schema.json` objektov.

`CLS-xxxxxx` identifikuje budúcu Classification Catalog Entry, nie túto vnorenú inštanciu. Jedna Classification reprezentuje jedno zaradenie; viac klasifikácií tvoria viaceré objekty v kolekcii rodiča. Hierarchia a klasifikačné systémy patria budúcemu Classification Catalog.

Kontrakt nemá vlastné ID, lifecycle, `verificationStatus`, `evaluationMode`, `notes`, enum klasifikačných hodnôt ani voľný text či fallback. Neznáme polia odmieta. Vnorený SourceLink zachováva vlastný `verificationStatus` podľa existujúceho kontraktu.

`sourceLinks` sú v `0.2B.1` štrukturálne nepovinné. Pri uvedení ide o pole s nulou alebo viacerými položkami, bez novej požiadavky unikátnosti, rovnako ako v spoločných EOS metadátach. RFC-0001 §4.6 naďalej sémanticky vyžaduje zdroje pri klasifikáciách pochádzajúcich z externých systémov, noriem alebo dokumentov. Vynucovanie tejto podmienky podľa katalógového pôvodu je odložené do `0.2B.2`; pôvod sa z CLS neodhaduje.

Validátor zatiaľ nekontroluje existenciu ani aktívny stav CLS položky, referenčnú integritu voči katalógu, správny systém, kompatibilitu s rodičom ani hierarchiu. Existujúce kontroly formátu `sourceReferenceId` zostávajú zachované; nepotvrdzujú existenciu SRC záznamu. Štrukturálne platná Classification nie je dôkazom správneho zaradenia. Zdroj definície kategórie automaticky nedokazuje zaradenie konkrétneho objektu.

Implementačný rozsah `Phase 0.2B.1.5` je dokončený; celý `0.2B.1` zostáva rozpracovaný. Classification Catalog ani reálne CLS položky nevznikli a `0.2B.2` nezačala. JSON Schema je serializačný kontrakt, nie samotný Knowledge Model.

## Míľnik 0.2B.1.4 - Condition Contract

Štvrtý Knowledge Core Contract je `Condition`:

- schéma: `knowledge-core/condition.schema.json`,
- schema id: `https://eos.local/schemas/knowledge-core/condition.schema.json`,
- discovery: `index.schema.json#/$defs/condition`,
- typ: value object vlastnený rodičovským objektom,
- lifecycle: nemá vlastné `id`, `status`, `revision`, `schemaVersion`, `recordVersion`, `sourceLinks` ani `verificationStatus`.

`Condition` opisuje kontext, okolnosť, hranicu alebo stav, za ktorých má tvrdenie, vlastnosť, pozorovanie alebo schopnosť význam. Neobsahuje meranú hodnotu samotnú, property identitu, observation identitu, workflow stav ani zdrojové dôkazy.

Počiatočný scope obsahuje povinné polia `conditionTypeId` a `evaluationMode`. `conditionTypeId` používa centralizovaný formát `CND-xxxxxx` pre budúci Condition Type Catalog Entry. Samotný Condition Type Catalog zatiaľ nevzniká.

Presne jedna hodnotová forma musí byť prítomná:

- `quantity`,
- `valueRange`,
- `textValue`,
- `booleanValue`,
- `referenceId`.

`quantity` a `valueRange` používajú `$ref` na existujúce Knowledge Core kontrakty. `textValue` a `referenceId` musia byť neprázdne. `referenceId` je obmedzený na existujúce centrálne podporované EOS identifikátory a nezavádza univerzálny prefix.

`evaluationMode` používa hodnoty `mandatory`, `limiting`, `descriptive`, `recommended` a `contextual`. Hodnoty `required` a `optional` sa nepoužívajú, pretože miešajú význam požiadavky so štrukturálnou povinnosťou poľa.

Validácia pre `Condition` je v tomto míľniku schema-only. Budúca aplikačná validácia bude potrebná až pre existenciu Condition Type Catalog položiek, kompatibilitu hodnotovej formy a vyhodnotenie použiteľnosti.

## Míľnik 0.2B.1.3 - MeasurementQuality Contract

Tretí Knowledge Core Contract je `MeasurementQuality`:

- schéma: `knowledge-core/measurement-quality.schema.json`,
- schema id: `https://eos.local/schemas/knowledge-core/measurement-quality.schema.json`,
- discovery: `index.schema.json#/$defs/measurementQuality`,
- typ: value object vlastnený rodičovským objektom,
- lifecycle: nemá vlastné `id`, `status`, `revision`, `schemaVersion`, `recordVersion`, `sourceLinks` ani `verificationStatus`.

Počiatočný scope obsahuje iba `uncertainty`, `resolution`, `confidenceLevel` a `notes`. Aspoň jedno zo štruktúrovaných polí `uncertainty`, `resolution` alebo `confidenceLevel` musí byť prítomné; notes-only objekt je neplatný.

`uncertainty` a `resolution` používajú `$ref` na `Quantity`, takže jednotky sú nesené iba vo vnorených `Quantity` objektoch. `confidenceLevel` je normalizované číslo od 0 do 1 vrátane.

`MeasurementQuality` neobsahuje meranú hodnotu, property význam, podmienky, zdroje ani tolerancie. Výrobná alebo akceptačná tolerancia je requirement a zostáva odložená do budúceho requirement/tolerance kontraktu.

Odložené koncepty pre budúcu stabilizáciu: `accuracy`, `declaredError`, `maximumPermissibleError`, `repeatability`, `reproducibility`, `methodReference`, `instrumentId`, `calibrationReference`, `tolerance`, `upperTolerance`, `lowerTolerance`.

## Míľnik 0.2B.1.2 - ValueRange Contract

Druhý Knowledge Core Contract je `ValueRange`:

- schéma: `knowledge-core/value-range.schema.json`,
- schema id: `https://eos.local/schemas/knowledge-core/value-range.schema.json`,
- discovery: `index.schema.json#/$defs/valueRange`,
- typ: value object vlastnený rodičovským objektom,
- lifecycle: nemá vlastné `id`, `status`, `revision`, `schemaVersion`, `recordVersion`, `sourceLinks` ani `verificationStatus`.

`ValueRange` používa povinné `unitId` a aspoň jednu hranicu z `minValue` alebo `maxValue`. Voliteľné `lowerInclusive` a `upperInclusive` určujú otvorenosť hraníc; ak sú vynechané, sémantická predvolená hodnota je `true`, ale schéma nedopĺňa hodnoty do dát.

`unitId` používa centrálny identifikátor `UNT-xxxxxx` zo `common/identifiers.schema.json#/$defs/UNT`. Unit Catalog záznamy ani konkrétne jednotky zatiaľ nie sú implementované.

`ValueRange` reprezentuje interval. `Quantity` reprezentuje jednu skalárnu hodnotu. `ValueRange` preto v tejto fáze nevkladá dve `Quantity` hranice a udržiava jednu spoločnú jednotku na úrovni rozsahu.

Štrukturálna validácia kontroluje povinné polia, typy, centrálny `UNT` formát, aspoň jednu hranicu, väzbu inkluzivity na existenciu hranice a `additionalProperties: false`. EOS aplikačná validácia kontroluje `minValue <= maxValue` a opakuje významové pravidlá pre inkluzivitu bez hranice.

## Míľnik 0.2B.1.1 - Quantity Contract

Prvý Knowledge Core Contract je `Quantity`:

- schéma: `knowledge-core/quantity.schema.json`,
- schema id: `https://eos.local/schemas/knowledge-core/quantity.schema.json`,
- discovery: `index.schema.json#/$defs/quantity`,
- typ: value object vlastnený rodičovským objektom,
- lifecycle: nemá vlastné `id`, `status`, `revision`, `schemaVersion`, `recordVersion` ani `sourceLinks`.

`Quantity` používa povinné polia `value` a `unitId`. Voliteľné pole `notes` je povolené iba ako lokálna poznámka bez významu jednotky, tolerancie, neistoty, zdrojovej citácie alebo prevodovej logiky.

`unitId` používa centrálny identifikátor `UNT-xxxxxx` zo `common/identifiers.schema.json#/$defs/UNT`. Unit Catalog záznamy ani konkrétne jednotky zatiaľ nie sú implementované.

`Quantity` zámerne neobsahuje `ValueRange`, `MeasurementQuality`, `Condition`, `PropertyRecord`, `Observation`, konkrétne strojárske hodnoty, konverzné faktory ani zobrazovacie jednotky.

Tento priečinok je určený pre dátové kontrakty EOS.

Schémy definujú štruktúru dát, nie technické hodnoty.

## Fáza 0.2A

Základné schémy sú rozdelené modulárne:

- `common/lifecycle-status.schema.json`
- `common/identifiers.schema.json`
- `common/source-link.schema.json`
- `common/metadata.schema.json`
- `source-reference.schema.json`
- `norm-reference.schema.json`
- `document-record.schema.json`
- `index.schema.json`

Používa sa JSON Schema Draft 2020-12.

Riadené kontrakty používajú `additionalProperties: false`, ak nie je výslovne schválená výnimka.

`core_entities.schema.json` je kompatibilitný vstup na centrálny index.

Štrukturálnu validáciu vykonáva Python knižnica `jsonschema` cez `Draft202012Validator`. Závislosť je evidovaná v `pyproject.toml`.
