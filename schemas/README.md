# schemas

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
