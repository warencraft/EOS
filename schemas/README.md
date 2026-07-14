# schemas

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
