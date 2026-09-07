# schemas

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
